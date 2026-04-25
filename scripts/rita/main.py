"""
Rita AI - Main API Server
Version 2.2.0 - Production-ready, robust, optimized
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
import time
import hashlib
from typing import Optional

from config import config
from personality import personality 
from memory import memory
from content_filter import check_message_safety
from ban_system import initialize_ban_table

# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# GEMINI CONFIGURATION
# ============================================================================
genai.configure(api_key=config.GEMINI_API_KEY)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

model = genai.GenerativeModel(
    model_name=config.MODEL_NAME,
    system_instruction=personality.get_system_prompt(),
    safety_settings=safety_settings,
    generation_config={
        "temperature": config.TEMPERATURE,
        "max_output_tokens": config.MAX_TOKENS
    }
)

# ============================================================================
# CACHE & ANTI-DUPLICATE
# ============================================================================
# Cache pour empêcher les doublons (clé: hash du message + user)
recent_requests = {}
DUPLICATE_WINDOW = 3.0  # secondes

# ============================================================================
# FASTAPI APP
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le démarrage et l'arrêt propre"""
    logger.info("🚀 Starting Rita AI v2.2...")
    await memory.initialize()
    await initialize_ban_table() 
    logger.info("✅ Rita is online")
    yield
    logger.info("👋 Shutting down...")
    await memory.shutdown()

app = FastAPI(
    title="Rita AI",
    description="Advanced AI for SecondLife",
    version="2.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_text(text: str) -> str:
    """Nettoie et limite le texte sans casser l'encodage"""
    if not text:
        return ""
    
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = text.decode('latin-1')
            except:
                text = text.decode('utf-8', errors='ignore')
    
    if not isinstance(text, str):
        text = str(text)
    
    # Supprime caractères de contrôle
    text = ''.join(
        char for char in text 
        if ord(char) >= 32 or char in '\n\t'
    )
    
    return text.strip()[:1000]


def is_system_event(message: str, user_name: str) -> bool:
    """Détecte les events système qui ne doivent PAS être traités comme des messages"""
    if user_name.lower() in ["system", "rita", "anonyme"]:
        return True
    
    if message.startswith("[") and message.endswith("]"):
        return True
    
    system_patterns = ["[EVENT_", "[SYSTEM]", "[BOT]"]
    for pattern in system_patterns:
        if pattern in message:
            return True
    
    return False


def is_duplicate_request(user_name: str, message: str) -> bool:
    """Détecte les requêtes en double (anti-spam et anti-bug LSL)"""
    # Crée une clé unique
    key = hashlib.md5(f"{user_name}:{message}".encode()).hexdigest()
    now = time.time()
    
    # Nettoyage des anciennes entrées
    expired_keys = [k for k, t in recent_requests.items() if now - t > DUPLICATE_WINDOW]
    for k in expired_keys:
        del recent_requests[k]
    
    # Check si doublon
    if key in recent_requests:
        last_time = recent_requests[key]
        if now - last_time < DUPLICATE_WINDOW:
            return True
    
    # Enregistre la requête
    recent_requests[key] = now
    return False


def extract_message_command(text: str) -> tuple:
    """Extrait les commandes %%POUR:Nom%% message"""
    match = re.search(r'%%POUR:([^%]+)%%\s*(.*)', text, re.IGNORECASE | re.DOTALL)
    if match:
        recipient = match.group(1).strip()
        content = match.group(2).strip()
        cleaned_text = text[:match.start()].strip()
        return cleaned_text, recipient, content
    return text, None, None


def clean_ai_response(text: str) -> str:
    """Nettoie la réponse de l'IA"""
    if not text:
        return ""
    
    # Remplace les guillemets pour éviter les problèmes JSON
    text = text.replace('"', "'")
    
    # Supprime les préfixes inutiles
    prefixes = [
        "Rita:", "Rita :", "[MESSAGE", "IA:", "Rita dit:", "Rita répond:",
        "AI:", "Bot:", "Réponse:", "Response:"
    ]
    for prefix in prefixes:
        if text.upper().startswith(prefix.upper()):
            text = text[len(prefix):].strip()
            break
    
    # Supprime les markdown communs
    text = text.replace("**", "")
    text = text.replace("__", "")
    
    return text.strip()


def deduplicate_context(context_lines: list) -> list:
    """Supprime les doublons consécutifs dans le contexte"""
    if not context_lines:
        return []
    
    cleaned = [context_lines[0]]
    
    for line in context_lines[1:]:
        # Évite les doublons exacts ET les répétitions très similaires
        if line != cleaned[-1] and not _is_similar(line, cleaned[-1]):
            cleaned.append(line)
    
    return cleaned


def _is_similar(line1: str, line2: str, threshold: float = 0.8) -> bool:
    """Détecte si deux lignes sont très similaires"""
    if not line1 or not line2:
        return False
    
    # Compare les 50 premiers caractères
    s1 = line1[:50].lower()
    s2 = line2[:50].lower()
    
    # Si exactement pareil
    if s1 == s2:
        return True
    
    # Calcul de similarité basique
    common = sum(1 for a, b in zip(s1, s2) if a == b)
    similarity = common / max(len(s1), len(s2))
    
    return similarity >= threshold


def truncate_safely(text: str, max_length: int = 80) -> str:
    """Tronque le texte intelligemment"""
    if not text or len(text) <= max_length:
        return text
    
    # Coupe au dernier espace
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length - 20:
        truncated = truncated[:last_space]
    
    return truncated + "..."


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "2.2.0",
        "name": "Rita AI"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected" if memory.pool else "disconnected",
        "model": config.MODEL_NAME,
        "version": "2.2.0"
    }


@app.post("/chat")
async def chat(request: Request):
    """Endpoint principal de conversation - Version optimisée et robuste"""
    try:
        # === PARSE REQUEST ===
        data = await request.json()
        user_message = clean_text(data.get("message", ""))
        user_name = clean_text(data.get("user", "Anonyme"))
        is_private_raw = data.get("is_private", False)
        
        is_private = (
            is_private_raw == "true" 
            if isinstance(is_private_raw, str) 
            else bool(is_private_raw)
        )
        
        # === VALIDATIONS ===
        if not user_message:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # === IGNORE SYSTEM EVENTS ===
        if is_system_event(user_message, user_name):
            logger.info(f"ℹ️ System event ignored | User: {user_name} | Msg: {user_message[:50]}")
            return JSONResponse(
                content={"response": ""},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # === ANTI-DUPLICATE (évite les bugs LSL) ===
        if is_duplicate_request(user_name, user_message):
            logger.warning(f"⚠️ Duplicate request blocked | User: {user_name} | Msg: {user_message[:50]}")
            return JSONResponse(
                content={"response": ""},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # === FILTRE DE SÉCURITÉ ===
        is_safe, blocked_response = await check_message_safety(user_message, user_name)
        
        if not is_safe:
            logger.warning(f"🚫 Message bloqué | User: {user_name} | Msg: {user_message[:50]}")
            return JSONResponse(
                content={"response": blocked_response},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # === LOAD USER DATA ===
        user_data = await memory.load_user_data(user_name)
        
        # === BUILD CONTEXT ===
        context = personality.build_context(
            user_name=user_name,
            affinity=user_data['affinity'],
            profile=user_data['profile'],
            recent_messages=user_data['context'],
            recent_events=user_data['events'],
            pending_messages=user_data['messages'],
            is_private=is_private
        )
        
        timestamp = personality.get_timestamp()
        mode = "chuchote en privé" if is_private else "dit publiquement"
        
        # === STRICT PROMPT (anti-hallucinations) ===
        prompt = f"""{context}

---
INSTRUCTION CRITIQUE:
- Tu réponds UNIQUEMENT au message ci-dessous
- N'invente AUCUN contexte antérieur
- N'anticipe pas de sujet non mentionné
---

{user_name} te {mode} ({timestamp}): {user_message}"""
        
        # === GENERATE RESPONSE ===
        ai_text = await _generate_response(prompt, user_name, user_message)
        
        if not ai_text or ai_text == "...":
            return JSONResponse(
                content={"response": "..."},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # === EXTRACT MESSAGE COMMANDS ===
        ai_text, msg_recipient, msg_content = extract_message_command(ai_text)
        
        if msg_recipient and msg_content:
            await memory.send_message(user_name, msg_recipient, msg_content)
            if not ai_text or ai_text.strip() == "":
                ai_text = f"Ok je transmets à {msg_recipient}"
        
        # === CLEAN RESPONSE ===
        ai_text = clean_ai_response(ai_text)
        
        # === UPDATE MEMORY (with deduplication) ===
        await _update_memory(
            user_name=user_name,
            user_message=user_message,
            ai_text=ai_text,
            user_data=user_data,
            is_private=is_private
        )
        
        # === MARK MESSAGES AS READ ===
        if is_private and user_data['messages']:
            await memory.mark_messages_read(user_name)
        
        return JSONResponse(
            content={"response": ai_text},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        return JSONResponse(
            content={"response": "Erreur interne. Ping originlab"},
            status_code=500
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _generate_response(prompt: str, user_name: str, user_message: str) -> str:
    """Génère la réponse Gemini avec gestion d'erreurs robuste"""
    try:
        response = await model.generate_content_async(prompt)
        
        # Tentative 1 : .text direct
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        
        # Tentative 2 : via parts
        if response.parts and len(response.parts) > 0:
            return response.parts[0].text.strip()
        
        # Échec : log et retourne "..."
        finish_reason = (
            response.candidates[0].finish_reason 
            if response.candidates 
            else "unknown"
        )
        logger.warning(
            f"⚠️ Gemini empty response | User: {user_name} | "
            f"Msg: {user_message[:50]} | Reason: {finish_reason}"
        )
        return "..."
        
    except Exception as e:
        logger.error(f"❌ Gemini error: {e}")
        return "Bug. Réessaie"


async def _update_memory(user_name: str, 
                         user_message: str, 
                         ai_text: str, 
                         user_data: dict, 
                         is_private: bool) -> None:
    """Met à jour la mémoire avec déduplication et protections"""
    
    # Format de la nouvelle ligne
    tag = "[P]" if is_private else "[G]"
    user_msg_short = truncate_safely(user_message, 80)
    ai_text_short = truncate_safely(ai_text, 80)
    new_line = f"{tag} {user_name}: {user_msg_short} → {ai_text_short}"
    
    # Charge le contexte actuel
    context_lines = [l for l in user_data['context'].split('\n') if l.strip()]
    
    # === DEDUPLICATION ===
    # Évite les doublons consécutifs
    if context_lines and _is_similar(new_line, context_lines[-1]):
        logger.info(f"⚠️ Duplicate line skipped for {user_name}")
        return
    
    # Ajoute la nouvelle ligne
    context_lines.append(new_line)
    
    # Nettoie les doublons résiduels
    context_lines = deduplicate_context(context_lines)
    
    # === RÉSUMÉ AUTOMATIQUE ===
    if len(context_lines) >= config.SUMMARY_THRESHOLD:
        full_conv = "\n".join(context_lines)
        
        # Lance l'analyse en arrière-plan
        asyncio.create_task(
            memory.analyze_and_save_background(
                user_name,
                user_data['profile'],
                full_conv,
                user_data['affinity']
            )
        )
        
        # Garde seulement les derniers messages après résumé
        context_lines = context_lines[-config.KEEP_AFTER_SUMMARY:]
    
    # === SAUVEGARDE ===
    new_context = "\n".join(context_lines[-config.IMMEDIATE_MEMORY:])
    
    # Vérification avant sauvegarde
    if not new_context.strip():
        logger.warning(f"⚠️ Empty context for {user_name}, skipping save")
        return
    
    # Limite de taille (sécurité)
    if len(new_context) > 5000:
        logger.warning(f"⚠️ Context too long for {user_name}, truncating")
        new_context = new_context[-5000:]
    
    await memory.save_interaction(
        user_name,
        new_context,
        user_data['profile'],
        user_data['affinity']
    )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)