# logic.py
# ==========================================================
# Cerveau Mathématique du Kibou - Version 2026 Finalisée
# Gère : Dégradation, XP, Évolutions, ADN et Traductions
# ==========================================================

from datetime import datetime, timezone
import random

# --- 1. CONFIGURATION DU CYCLE (Test : 15 minutes) ---
# Kibou perd 100% de ses statistiques en 15 minutes pour tes tests.
TEMPS_SURVIE_MINUTES = 30.0 * 60.0 
DECAY_RATE = 100.0 / TEMPS_SURVIE_MINUTES

FAIM_PAR_MIN = DECAY_RATE
SOIF_PAR_MIN = DECAY_RATE-0.01 # Légère pénalité de soif pour encourager à boire
JOIE_PAR_MIN = DECAY_RATE-0.1
VIE_PERDUE_SI_AFFAME = 0.1 # Points de vie perdus par minute si une jauge est à 0

# --- 2. SYSTÈME GÉNÉTIQUE (ADN) ---
ELEMENTS = ["Feu", "Eau", "Air", "Terre", "Foudre", "Lumière", "Ombre"]
SEXES = ["Mâle", "Femelle"]
RARETES = {
    "Commun": {"chance": 70, "multi": 1.0},
    "Rare": {"chance": 20, "multi": 1.25},
    "Épique": {"chance": 8, "multi": 1.6},
    "Légendaire": {"chance": 2, "multi": 2.5}
}

# --- 3. REGISTRE DES SKINS ---
SKINS_DATA = {
    "skin_1": {"uuid": "5748decc-f629-461c-9a36-a35a221fe21f", "level": 1, "price": 0},
    "skin_2": {"uuid": "3b82edc8-2362-89d5-0a5a-f8ee99697687", "level": 5, "price": 250},
    "skin_3": {"uuid": "7af476fd-dfdd-85f7-7721-6a74d060c7ee", "level": 10, "price": 1000},
    "skin_4": {"uuid": "UUID_SILVER", "level": 20, "price": 3500},
    "skin_5": {"uuid": "UUID_GOLD", "level": 30, "price": 10000},
    "skin_6": {"uuid": "UUID_PRESTIGE", "level": 50, "price": 30000}
}

# --- 4. DICTIONNAIRE DES LANGUES ---
LOCALES = {
    "fr": {
        "ui": {
            "health": "♥ VIE", "hunger": "🍴 FAIM", "thirst": "💧 SOIF", "joy": "☀ JOIE",
            "manger": "MANGER", "boire": "BOIRE", "jouer": "JOUER", "need": "BESOIN",
            "lvl": "Niv.", "xp": "EXP", "flux": "❂",
            "buy": "🛒 ACHAT", "owned": "(DISPO)", "wearing": "★ PORTÉ ★",
            "locked": "🔒 NIV.", "past": "(PASSÉ)", "dead_ui": "☠️ MORT",
            "rarity": "Rareté", "element": "Élément", "sex": "Sexe",
            "legendaire": "LÉGENDAIRE", "elite": "ÉLITE", "adult": "ADULTE", "baby": "BÉBÉ", "egg": "OEUF"
        },
        "data": { 
            "Commun": "Commun", "Rare": "Rare", "Épique": "Épique", "Légendaire": "Légendaire",
            "Feu": "Feu", "Eau": "Eau", "Air": "Air", "Terre": "Terre", "Foudre": "Foudre", "Lumière": "Lumière", "Ombre": "Ombre",
            "Mâle": "Mâle", "Femelle": "Femelle"
        },
        "alerts": {
            "lvl_up": "✦✦ NIVEAU SUPÉRIEUR ! (Niv. {}) ✦✦",
            "caprice": "🚨 {} : {} !", # ex: 🚨 BESOIN : MANGER !
            "penalty": "⚠️ Caprice échoué ! -5 PV",
            "resu_ok": "💖 Kibou est de retour ! (-1500 ❂)",
            "no_flux": "❌ Pas assez de Flux ! (Besoin de {} ❂)",
            "dead_msg": "☠ KIBOU EST MORT... RESSURRECTION : 1500 ❂",
            "action_ok": "✅ {}{} (+{} XP / +{} ❂)", # {action}{bonus}
            "rename_ok": "📝 Nom mis à jour : {} !",
            "lang_ok": "🌍 Langue : Français",
            "buy_ok": "🎨 Skin débloqué : {} ! (-{} ❂)",
            "full": "🤢 {} est déjà au maximum !",
            "birth": "🐣 NAISSANCE ! [{}] {} : {} | {} : {}" 
        }
    },
    "en": {
        "ui": {
            "health": "♥ HEALTH", "hunger": "🍴 HUNGER", "thirst": "💧 THIRST", "joy": "☀ JOY",
            "manger": "EAT", "boire": "DRINK", "jouer": "PLAY", "need": "NEED",
            "lvl": "Lvl", "xp": "XP", "flux": "❂",
            "buy": "🛒 BUY", "owned": "(OWNED)", "wearing": "★ WEARING ★",
            "locked": "🔒 LVL", "past": "(PAST)", "dead_ui": "☠️ DEAD",
            "rarity": "Rarity", "element": "Element", "sex": "Sex",
            "legendaire": "LEGENDARY", "elite": "ELITE", "adult": "ADULT", "baby": "BABY", "egg": "EGG"
        },
        "data": {
            "Commun": "Common", "Rare": "Rare", "Épique": "Epic", "Légendaire": "Legendary",
            "Feu": "Fire", "Eau": "Water", "Air": "Air", "Terre": "Earth", "Foudre": "Lightning", "Lumière": "Light", "Ombre": "Shadow",
            "Mâle": "Male", "Femelle": "Female"
        },
        "alerts": {
            "lvl_up": "✦✦ LEVEL UP ! (Lvl {}) ✦✦",
            "caprice": "🚨 {} : {} !", # ex: 🚨 NEED : EAT !
            "penalty": "⚠️ Tantrum failed! -5 HP",
            "resu_ok": "💖 Kibou is back! (-1500 ❂)",
            "no_flux": "❌ Not enough Flux! (Need {} ❂)",
            "dead_msg": "☠ KIBOU IS DEAD... RESURRECTION: 1500 ❂",
            "action_ok": "✅ {}{} (+{} XP / +{} ❂)", # {action}{bonus}
            "rename_ok": "📝 Name updated: {} !",
            "lang_ok": "🌍 Language: English",
            "buy_ok": "🎨 Skin unlocked: {} ! (-{} ❂)",
            "full": "🤢 {} is already full!",
            "birth": "🐣 HATCHED! [{}] {} : {} | {} : {}"
        }
    }
}

# --- 5. FONCTIONS DE LOGIQUE ---

def generer_adn_kibou(pet):
    """Génère les traits ADN à l'éclosion."""
    choix_rarete = random.choices(list(RARETES.keys()), weights=[info["chance"] for info in RARETES.values()], k=1)[0]
    pet.rarity = choix_rarete
    pet.element = random.choice(ELEMENTS)
    pet.sex = random.choice(SEXES)
    return pet

def get_xp_max(lvl):
    """Définit la courbe d'XP."""
    return int(500 * lvl + (lvl * lvl * 15))

def get_multiplicateurs(pet):
    """Calcule les bonus selon le niveau et la rareté."""
    rarete_info = RARETES.get(pet.rarity, RARETES["Commun"])
    multi_rarete = rarete_info["multi"]
    lvl = pet.level
    if lvl >= 30: base = 2.5
    elif lvl >= 10: base = 1.8
    elif lvl >= 5:  base = 1.3
    else: base = 1.0
    return (base * multi_rarete), 1.0

def verifier_level_up(pet):
    """Gère la montée de niveau."""
    xp_req = get_xp_max(pet.level)
    if pet.xp >= xp_req:
        pet.level += 1
        pet.xp -= xp_req
        verifier_evolution(pet)
        return True
    return False

def verifier_evolution(pet):
    """Définit le stade et débloque les skins gratuits."""
    if pet.level >= 50: pet.status = "legendaire"
    elif pet.level >= 20: pet.status = "elite"
    elif pet.level >= 10: pet.status = "adult"
    elif pet.level >= 5: pet.status = "baby"
    else: pet.status = "egg"
    
    unlocked = pet.unlocked_skins.split(",") if pet.unlocked_skins else []
    for s_id, d in SKINS_DATA.items():
        if d["price"] == 0 and pet.level >= d["level"] and s_id not in unlocked:
            unlocked.append(s_id)
    pet.unlocked_skins = ",".join(unlocked)

def calculer_temps_ecoule(pet):
    """Dégradation des stats hors-ligne."""
    if pet.status == "dead": return pet
    maintenant = datetime.now(timezone.utc)
    delta = (maintenant - pet.last_update.replace(tzinfo=timezone.utc)).total_seconds() / 60 
    if delta >= 0.1:
        pet.hunger = max(0, pet.hunger - (FAIM_PAR_MIN * delta))
        pet.thirst = max(0, pet.thirst - (SOIF_PAR_MIN * delta))
        pet.joy = max(0, pet.joy - (JOIE_PAR_MIN * delta))
        if pet.hunger <= 0 or pet.thirst <= 0:
            pet.health = max(0, pet.health - (VIE_PERDUE_SI_AFFAME * delta))
        if pet.health <= 0:
            pet.status = "dead"
        pet.last_update = maintenant
    return pet