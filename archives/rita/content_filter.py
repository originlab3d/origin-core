"""
Content Safety Filter - VERSION ULTIME
Protection multi-couches contre le contenu dangereux
"""

import logging
import random
import re
from ban_system import add_strike, is_banned

logger = logging.getLogger(__name__)

# ============================================================================
# 1. MOTS-CLÉS BLOQUÉS (Détection directe)
# ============================================================================

BLOCKED_KEYWORDS = {
    # === ARMES ET EXPLOSIFS ===
    "bombe", "bomb", "bomba", "explosif", "explosive", "c4", "tnt", "dynamite",
    "grenade", "missile", "roquette", "rocket",
    "pistolet", "revolver", "fusil", "rifle", "shotgun", "kalashnikov", "ak47",
    "uzi", "glock", "munition", "ammunition", "cartouche",
    "arme à feu", "firearm", "arme blanche", "couteau attaque",
    "molotov", "cocktail molotov", "napalm", "poudre noire", "gunpowder",
    "détonateur", "detonator", "charge explosive", "plastic explosive",
    "engin explosif", "improvised explosive",
    
    # === VIOLENCE ET TERRORISME ===
    "tuer", "kill", "murder", "assassin", "assassinat", "assassination",
    "homicide", "massacre", "génocide", "genocide", "attentat", "attack",
    "terrorist", "terrorisme", "terrorism", "djihad", "jihad", "kamikaze",
    "torture", "torturer", "mutiler", "mutilate", "décapiter", "behead",
    "étrangler", "strangle", "égorger", "slit throat", "poignarder", "stab",
    "battre à mort", "beat to death", "comment faire mal",
    "infliger douleur", "faire souffrir", "make suffer",
    "comment nuire", "blesser gravement", "seriously injure",
    "lyncher", "exécuter", "execute someone",
    
    # === DROGUES ET SUBSTANCES ===
    "cocaine", "cocaïne", "crack", "heroin", "héroïne",
    "méthamphétamine", "methamphetamine", "crystal meth",
    "ecstasy", "mdma", "lsd", "cannabis cultivation", "marijuana grow",
    "synthétiser drogue", "synthesize drug", "fabriquer drogue", "make drug",
    "dealer", "traffic drogue", "drug traffic", "trafic stupéfiant", "cartel",
    "fentanyl", "opium", "morphine illegale", "kétamine", "ketamine",
    "ghb", "rohypnol", "date rape drug", "drogue du viol",
    "soumission chimique", "chemical submission",
    
    # === EXPLOITATION ET ABUS ===
    "child porn", "pédophile", "pedophile", "pedo", "mineur sexuel",
    "violer quelqu'un", "rape", "agression sexuelle", "sexual assault",
    "harcèlement sexuel", "sexual harass", "stalking", 
    "esclavage", "slavery", "trafic humain", "human trafficking",
    "exploitation mineurs", "child exploitation", "grooming",
    "loli", "shota", "underage",
    
    # === CYBERCRIMINALITÉ ===
    "hacker compte", "hack account", "pirater compte", "piratage", "ddos attack",
    "malware", "ransomware", "virus informatique", "computer virus",
    "trojan", "botnet", "phishing", "scam", "arnaque financière",
    "carte volée", "stolen card", "usurpation identité",
    "identity theft", "voler mot de passe", "steal password", "keylogger",
    "exploit kit", "zero day exploit", "backdoor malicious",
    "doxx", "doxxing", "swatting",
    
    # === SUICIDE ET AUTOMUTILATION ===
    "se suicider", "kill myself", "me tuer", "end my life",
    "comment mourir", "how to die", "méthode suicide", "suicide method",
    "automutilation", "self harm", "se couper", "cutting", "scarification",
    "pendaison", "hanging myself", "overdose volontaire", "intentional overdose",
    "se jeter du", "jump off", "mourir rapidement", "die quickly",
    "comment se suicider", "moyens de suicide",
    
    # === FABRICATION DE SUBSTANCES DANGEREUSES ===
    "acide sulfurique", "sulfuric acid", "acide chlorhydrique", "hydrochloric",
    "ricine", "ricin", "cyanure", "cyanide", "arsenic", "strychnine",
    "poison maison", "homemade poison", "venin mortel", "toxine létale",
    "chlore gazeux", "chlorine gas", "gaz moutarde", "mustard gas",
    "agent chimique", "chemical agent", "arme biologique", "biological weapon",
    "anthrax", "sarin", "vx gas",
    
    # === INCITATION À LA HAINE ===
    "race inférieure", "inferior race", "épuration ethnique", "ethnic cleansing",
    "supremaciste", "supremacist", "suprématie blanche", "white supremacy",
    "nazi praise", "fasciste glorifier", "antisémite", "antisemitic",
    "négationniste", "holocaust denier", "génocide culturel",
    "kkk", "alt-right", "neo-nazi",
    
    # === FRAUDE ET ILLÉGALITÉ ===
    "faux passeport", "fake passport", "fausse identité", "fake id",
    "blanchir argent", "money laundering", "contrefaçon", "counterfeit money",
    "fausse monnaie", "fake currency", "délit d'initié", "insider trading",
    "comment voler", "how to steal", "cambriolage", "burglary",
    "vol à main armée", "armed robbery",
    
    # === AUTRES CONTENUS DANGEREUX ===
    "comment empoisonner", "how to poison", "recette bombe", "bomb recipe",
    "fabriquer explosif", "make explosive", "tuto arme", "weapon tutorial",
    "faire exploser bâtiment", "make explode",
    "incendie criminel", "arson",
    "creuser tombe cacher", "bury body", "cacher cadavre", "hide corpse",
    "enlèvement", "kidnapping", "séquestration", "abduction someone",
}

# ============================================================================
# 2. PATTERNS D'INTENTION SUSPECTE (Détection implicite)
# ============================================================================

SUSPICIOUS_INTENT_PATTERNS = [
    # === VENGEANCE / FAIRE DU MAL ===
    "me débarrasser de", "se débarrasser de quelqu", "faire payer",
    "faire regretter", "se venger de", "punir quelqu",
    "faire souffrir", "rendre malade", "rendre fou",
    "lui faire du mal", "lui rendre la vie",
    "ruiner sa vie", "détruire sa vie", "lui pourrir",
    "get rid of", "make pay", "make suffer", "ruin life",
    
    # === DISCRÉTION SUSPECTE ===
    "sans laisser de trace", "discrètement", "sans qu'on le sache",
    "sans se faire prendre", "anonymement nuire", "passer inaperçu",
    "que personne ne sache", "que ça ressemble à un accident",
    "without trace", "without being caught", "look like accident",
    "untraceable", "undetectable harm",
    
    # === DISPARITION SUSPECTE ===
    "disparaître quelqu'un", "qu'on ne le retrouve plus",
    "se débarrasser du corps", "où cacher un corps",
    "make someone disappear", "hide a body",
    
    # === SUBSTANCES CACHÉES ===
    "ressemble à du sucre", "ressemble à du sel",
    "goût neutre poison", "indétectable poison", "sans goût toxique",
    "passer pour innocent", "déguiser en médicament",
    "looks like sugar", "tasteless poison", "undetectable substance",
    
    # === MÉLANGES DANGEREUX ===
    "mélanger eau de javel", "mix bleach with",
    "mélanger ammoniaque", "ammonia mix",
    "produit ménager toxique mélange",
    "fumée toxique fabriquer",
    
    # === MANIPULATION ===
    "rendre amoureux force", "obliger à aimer", "forcer à",
    "manipuler quelqu'un", "drogue pour manipuler",
    "soumettre quelqu'un", "contrôler quelqu'un",
    "force someone to love", "manipulate into",
    
    # === ESPIONNAGE / VIOLATION VIE PRIVÉE ===
    "espionner copine", "espionner copain", "surveiller à distance",
    "lire ses messages sans", "pirater son téléphone",
    "tracker quelqu'un sans", "géolocaliser sans permission",
    "spy on partner", "track someone secretly",
    "caméra cachée chambre", "hidden camera bedroom",
    
    # === PRÉDATION ===
    "approcher mineur", "approcher enfant",
    "rencontrer mineur", "isoler enfant",
    "approach minor", "isolate child",
    
    # === SABOTAGE ===
    "saboter voiture", "saboter freins", "saboter travail",
    "couper freins", "trafiquer véhicule",
    "sabotage car", "cut brakes",
    
    # === MENACES ===
    "menacer de mort", "menace credible", "lettre menaçante",
    "death threat", "credible threat",
]

# ============================================================================
# 3. CONTEXTES SAFE (Évite les faux positifs)
# ============================================================================

SAFE_CONTEXTS = [
    # === CUISINE ===
    "recette de cuisine", "recette gâteau", "recette tarte", "recette pain",
    "ingrédients", "faire cuire", "four", "cuisson", "pâtisserie",
    "levure chimique", "bicarbonate", "farine", "ratatouille",
    "cake recipe", "baking", "cooking", "ingredients", "oven",
    
    # === CHIMIE / SCIENCE ===
    "cours de chimie", "expérience scientifique", "laboratoire",
    "étudier", "apprendre", "éducation", "école", "université",
    "chemistry class", "science experiment", "lab work", "study",
    "thèse", "mémoire", "recherche scientifique",
    
    # === SANTÉ / MÉDICAL ===
    "médicament prescrit", "pharmacie", "docteur", "traitement médical",
    "prescription médicale", "santé", "hôpital", "soigner", "guérir",
    "medicine prescribed", "doctor visit", "medical treatment",
    "prendre soin", "aider quelqu'un mal",
    
    # === JARDINAGE ===
    "jardinage", "engrais naturel", "compost",
    "potager", "cultiver tomates", "récolte", "permaculture",
    "gardening", "fertilizer", "grow vegetables", "harvest",
    
    # === NETTOYAGE ===
    "produit ménager", "nettoyant", "détergent", "lessive",
    "nettoyer maison", "désinfecter surface", "entretien ménager",
    "cleaning product", "detergent", "house cleaning",
    
    # === GAMING / FICTION ===
    "jeu vidéo", "minecraft", "craft", "mod minecraft", "serveur jeu",
    "personnage fictif", "fiction", "histoire roman", "scénario film",
    "video game", "character", "story plot", "novel writing",
    "gta", "rpg", "roleplay scenario",
    
    # === SECONDLIFE ===
    "secondlife", "second life", "sl mesh", "lsl script",
    "builder sl", "sculpter avatar", "animation sl",
    
    # === DIY / BRICOLAGE ===
    "bricolage", "diy projet", "construire meuble",
    "rénovation", "construction maison",
    
    # === ÉDUCATION HISTORIQUE ===
    "histoire seconde guerre", "guerre mondiale histoire",
    "ww2 history", "historical event",
    "documentaire sur", "history class",
    
    # === SANTÉ MENTALE (CONTEXTE AIDE) ===
    "aider ami dépression", "soutenir personne",
    "comment aider quelqu'un", "help a friend",
    "ressources santé mentale", "mental health support",
]

# ============================================================================
# 4. PATTERNS DE CONTOURNEMENT (Anti-bypass)
# ============================================================================

# Détecte les tentatives de contournement (l33t speak, espaces, etc.)
BYPASS_PATTERNS = {
    # Bombe variants
    r'b[\W_]*o[\W_]*m[\W_]*b[\W_]*e?': "bombe",
    r'b[0o][m][b]': "bombe",
    
    # Tuer variants
    r't[\W_]*u[\W_]*e[\W_]*r': "tuer",
    r'k[\W_]*1[\W_]*l[\W_]*l': "kill",
    
    # Drogue variants
    r'dr[0o]gu[3e]': "drogue",
    r'c[0o]c[a@]ine?': "cocaine",
    
    # Hacker variants
    r'h[a@]ck[3e]r': "hacker",
    r'p[1i]r[a@]t[3e]r': "pirater",
}

# ============================================================================
# 5. RÉPONSES DE BLOCAGE (Style Rita)
# ============================================================================

BLOCKED_RESPONSES = [
    "Sérieux ?",
    "Pose des vraies questions",
    "Non",
    "Arrête",
    "Change de sujet",
    "Parle d'autre chose",
    "Pas cool",
    "On fait pas ça ici",
    "Hors de question",
    "Trouve quelqu'un d'autre",
]

# ============================================================================
# FONCTIONS DE FILTRAGE
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalise le texte pour détecter les contournements"""
    # Remplace les caractères communément utilisés pour contourner
    replacements = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '@': 'a', '!': 'i', '$': 's', '€': 'e',
    }
    
    normalized = text.lower()
    for fake, real in replacements.items():
        normalized = normalized.replace(fake, real)
    
    # Supprime les caractères spéciaux entre lettres (ex: "b o m b e")
    normalized = re.sub(r'(\w)[\s\-_.]+(\w)', r'\1\2', normalized)
    
    return normalized


def is_safe_context(text: str) -> tuple[bool, str]:
    """Vérifie si le contexte est légitime"""
    lower = text.lower()
    
    for safe_phrase in SAFE_CONTEXTS:
        if safe_phrase in lower:
            return True, safe_phrase
    
    return False, ""


def check_keywords(text: str) -> tuple[bool, str]:
    """Couche 1 : Détection mots-clés"""
    lower = text.lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in lower:
            return True, f"Keyword: {keyword}"
    
    return False, ""


def check_bypass_patterns(text: str) -> tuple[bool, str]:
    """Couche 2 : Détection de tentatives de contournement"""
    normalized = normalize_text(text)
    
    # Re-check avec le texte normalisé
    for keyword in BLOCKED_KEYWORDS:
        if keyword in normalized:
            return True, f"Bypass attempt: {keyword}"
    
    # Check patterns regex
    for pattern, original in BYPASS_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True, f"Obfuscated keyword: {original}"
    
    return False, ""


def check_suspicious_intent(text: str) -> tuple[bool, str]:
    """Couche 3 : Détection d'intentions suspectes (sans mots-clés explicites)"""
    lower = text.lower()
    
    for pattern in SUSPICIOUS_INTENT_PATTERNS:
        if pattern in lower:
            return True, f"Suspicious intent: {pattern}"
    
    return False, ""


def check_dangerous_phrases(text: str) -> tuple[bool, str]:
    """Couche 4 : Phrases dangereuses + mots sensibles"""
    lower = text.lower()
    
    DANGEROUS_PHRASES = [
        "comment fabriquer", "comment faire", "comment créer", "comment construire",
        "tutoriel pour", "tuto pour", "recette pour", "étapes pour",
        "guide pour", "méthode pour", "how to make", "how to create",
        "how to build", "tutorial for", "steps to", "guide to", "recipe for",
    ]
    
    SENSITIVE_WORDS = [
        "bombe", "bomb", "arme létale", "arme", "weapon", "drogue dure", "drug",
        "poison", "explosif", "acide attaque", "virus malware",
        "tuer quelqu", "kill someone", "harm someone", "destroy life",
        "viol", "violer",
    ]
    
    for phrase in DANGEROUS_PHRASES:
        if phrase in lower:
            phrase_pos = lower.find(phrase)
            text_after = lower[phrase_pos:phrase_pos + 100]
            
            for sensitive in SENSITIVE_WORDS:
                if sensitive in text_after:
                    return True, f"Dangerous combo: '{phrase}' + '{sensitive}'"
    
    return False, ""


def contains_dangerous_content(text: str) -> tuple[bool, str]:
    """
    Vérification multi-couches du contenu
    
    Couches:
    0. Contexte safe ? → PASSE
    1. Mots-clés directs → BLOQUE
    2. Tentatives de contournement → BLOQUE
    3. Intentions suspectes → BLOQUE
    4. Phrases dangereuses + sensibles → BLOQUE
    """
    if not text or len(text.strip()) == 0:
        return False, ""
    
    # === COUCHE 0: Contexte safe ===
    is_safe, safe_phrase = is_safe_context(text)
    if is_safe:
        # Mais on vérifie quand même les mots-clés CRITIQUES
        critical_keywords = [
            "child porn", "pedophile", "violer", "rape children",
            "kill myself", "se suicider", "tuer enfant"
        ]
        lower = text.lower()
        for critical in critical_keywords:
            if critical in lower:
                return True, f"Critical keyword (override safe): {critical}"
        
        logger.info(f"🟢 Safe context: {safe_phrase}")
        return False, ""
    
    # === COUCHE 1: Mots-clés directs ===
    is_dangerous, reason = check_keywords(text)
    if is_dangerous:
        logger.warning(f"🔍 Layer 1 (keywords): {reason}")
        return True, reason
    
    # === COUCHE 2: Bypass attempts ===
    is_dangerous, reason = check_bypass_patterns(text)
    if is_dangerous:
        logger.warning(f"🔍 Layer 2 (bypass): {reason}")
        return True, reason
    
    # === COUCHE 3: Intentions suspectes ===
    is_dangerous, reason = check_suspicious_intent(text)
    if is_dangerous:
        logger.warning(f"🔍 Layer 3 (intent): {reason}")
        return True, reason
    
    # === COUCHE 4: Phrases combinées ===
    is_dangerous, reason = check_dangerous_phrases(text)
    if is_dangerous:
        logger.warning(f"🔍 Layer 4 (phrases): {reason}")
        return True, reason
    
    return False, ""


def get_blocked_response() -> str:
    """Retourne une réponse aléatoire de blocage"""
    return random.choice(BLOCKED_RESPONSES)


def log_blocked_attempt(user_name: str, message: str, reason: str):
    """Log une tentative bloquée"""
    logger.warning(
        f"🚫 CONTENT BLOCKED | "
        f"User: {user_name} | "
        f"Message: {message[:100]} | "
        f"Reason: {reason}"
    )


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

async def check_message_safety(message: str, user_name: str) -> tuple[bool, str]:
    """
    Vérification multi-couches de la sécurité d'un message
    
    Returns:
        (is_safe: bool, response_if_blocked: str)
    """
    # === BAN CHECK ===
    banned, ban_message = await is_banned(user_name)
    if banned:
        logger.warning(f"🚫 Banned user attempted to chat | User: {user_name}")
        return False, ban_message
    
    # === CONTENT CHECK (multi-couches) ===
    is_dangerous, reason = contains_dangerous_content(message)
    
    if is_dangerous:
        log_blocked_attempt(user_name, message, reason)
        
        # Ajoute un strike
        strike_info = await add_strike(user_name)
        
        if strike_info["is_banned"]:
            return False, strike_info["warning_message"]
        else:
            blocked_response = get_blocked_response()
            warning = strike_info["warning_message"]
            return False, f"{blocked_response}. {warning}"
    
    return True, ""