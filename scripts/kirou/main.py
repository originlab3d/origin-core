# main.py
# ==========================================================
# Aiguilleur Principal - Gestion des routes et Traductions
# Version 2026 - Audit Final : ADN, Bilingue et Sécurité
# ==========================================================

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, logic
from database import engine, get_db
import urllib.parse
import random

# Initialisation de la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- UTILITAIRE : FORMATAGE ET TRADUCTION DES DONNÉES ---

def format_hud_data(pet, player=None, msg_key="", msg_arg=""):
    """
    Prépare le JSON pour Second Life. 
    Traduit les valeurs ADN et les messages sans doublons.
    """
    lang = getattr(player, "language", "fr")
    texts = logic.LOCALES.get(lang, logic.LOCALES["fr"])
    
    # 1. On récupère les VALEURS PURES traduites (ex: "Fire", "Common")
    trans_rarity = texts["data"].get(pet.rarity, pet.rarity)
    trans_element = texts["data"].get(pet.element, pet.element)
    trans_sex = texts["data"].get(pet.sex, pet.sex)
    trans_status = texts["ui"].get(pet.status, pet.status)

    # 2. Encodage des labels UI (Symboles ❂, ♥, etc.)
    safe_ui = {k: urllib.parse.quote(str(v)) for k, v in texts["ui"].items()}
    
    # 3. Traduction intelligente du message d'alerte
    translated_msg = ""
    if msg_key:
        raw_text = texts["alerts"].get(msg_key, msg_key)
        try:
            if "," in str(msg_arg):
                # Nettoyage et traduction de chaque morceau de l'argument
                raw_args = [a.strip() for a in str(msg_arg).split(",")]
                clean_args = []
                for a in raw_args:
                    # On cherche dans UI (pour les labels) puis dans DATA (pour les valeurs ADN)
                    # ex: "element" -> "Élément" / "Feu" -> "Fire"
                    trad = texts["ui"].get(a.lower(), texts["data"].get(a, a))
                    clean_args.append(trad)
                translated_msg = raw_text.format(*clean_args)
            else:
                # Argument unique (ex: "manger" ou un chiffre)
                val = str(msg_arg).lower()
                trad_arg = texts["ui"].get(val, texts["data"].get(msg_arg, msg_arg))
                translated_msg = raw_text.format(trad_arg)
        except Exception:
            translated_msg = raw_text

    # 4. Catalogue des skins
    catalog_str = "|".join([f"{k}:{v['uuid']}" for k, v in logic.SKINS_DATA.items()])
    
    # 5. Gestion du caprice
    event_caprice = "none"
    if pet and pet.status != "dead":
        besoins = []
        if pet.hunger < 50: besoins.append("manger")
        if pet.thirst < 50: besoins.append("boire")
        if pet.joy < 50: besoins.append("jouer")
        if besoins and random.random() < 0.35:
            event_caprice = random.choice(besoins)

    return {
        "status": "ok",
        "message": urllib.parse.quote(translated_msg),
        "laboubou": {
            "lang": lang,
            "name": urllib.parse.quote(pet.custom_name),
            "status": urllib.parse.quote(trans_status),
            "lvl": pet.level,
            "xp": round(pet.xp),
            "xp_max": logic.get_xp_max(pet.level),
            "hp": round(pet.health),
            "fd": round(pet.hunger),
            "th": round(pet.thirst),
            "joy": round(pet.joy),
            "event_caprice": event_caprice,
            "rarity": urllib.parse.quote(trans_rarity),
            "element": urllib.parse.quote(trans_element),
            "sex": urllib.parse.quote(trans_sex),
            "catalog": catalog_str,
            "skin": pet.current_skin,
            "skin_uuid": logic.SKINS_DATA.get(pet.current_skin, {}).get("uuid", ""),
            "unlocked": getattr(pet, "unlocked_skins", "skin_1"),
            "ui": safe_ui
        },
        "player": {"flux": player.flux} if player else {}
    }

# --- ROUTES API ---

@app.get("/login")
def login(uuid: str, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    if not player:
        player = models.Player(uuid=uuid, flux=500, language="fr")
        db.add(player); db.commit(); db.refresh(player)
    
    pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
    if pet:
        pet = logic.calculer_temps_ecoule(pet); db.commit()
    else:
        pet = models.Laboubou(owner_uuid=uuid, custom_name="Kibou", unlocked_skins="skin_1")
        pet = logic.generer_adn_kibou(pet) 
        db.add(pet); db.commit(); db.refresh(pet)
        
        # --- FIX DOUBLONS : On envoie 5 arguments précis pour le template birth ---
        # 🐣 NAISSANCE ! [{}] {} : {} | {} : {}
        # Arguments : Rareté, Label Élément, Valeur Élément, Label Sexe, Valeur Sexe
        birth_args = f"{pet.rarity}, element, {pet.element}, sex, {pet.sex}"
        return format_hud_data(pet, player, "birth", birth_args)
        
    return format_hud_data(pet, player)

@app.get("/action")
def pet_action(uuid: str, type: str, is_caprice: str = "false", db: Session = Depends(get_db)):
    pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    if not pet or not player: return {"status": "error"}

    if type == "penalty":
        pet.health = max(0, pet.health - 5)
        if pet.health <= 0: pet.status = "dead"
        db.commit(); return format_hud_data(pet, player, "penalty")

    if pet.status == "dead": return format_hud_data(pet, player, "dead_msg")
    
    stat_val = getattr(pet, "hunger" if type == "manger" else "thirst" if type == "boire" else "joy", 0)
    if stat_val >= 98: return format_hud_data(pet, player, "full", type)

    gain_xp, gain_stat, gain_flux = (250, 5, 10) if pet.status == "egg" else (20, 20, 15)
    if pet.status != "egg":
        mult, _ = logic.get_multiplicateurs(pet)
        gain_xp = int(gain_xp * mult); gain_flux = int(gain_flux * mult)

    # --- FIX TRADUCTION BONUS : On sépare l'action du label ---
    bonus_label = ""
    if is_caprice.lower() == "true":
        gain_xp *= 4; gain_flux *= 4
        bonus_label = " 🔥 BONUS x4"

    if type == "manger": pet.hunger = min(100, pet.hunger + gain_stat)
    elif type == "boire": pet.thirst = min(100, pet.thirst + gain_stat)
    elif type == "jouer": pet.joy = min(100, pet.joy + gain_stat)
    
    pet.xp += gain_xp; player.flux += gain_flux
    lvl_up = logic.verifier_level_up(pet); db.commit()
    
    if lvl_up: return format_hud_data(pet, player, "lvl_up", str(pet.level))
    
    # On envoie 4 arguments : type, bonus, xp, flux
    # ✅ {}{} (+{} XP / +{} ❂)
    feedback = f"{type}, {bonus_label}, {gain_xp}, {gain_flux}"
    return format_hud_data(pet, player, "action_ok", feedback)

# --- RESTE DES ROUTES (Inchangées) ---
@app.get("/action/rename")
def rename_pet(uuid: str, name: str, db: Session = Depends(get_db)):
    pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    new_name = urllib.parse.unquote(name).strip()[:15]
    pet.custom_name = new_name
    db.commit(); return format_hud_data(pet, player, "rename_ok", pet.custom_name)

@app.get("/action/set_lang")
def set_lang(uuid: str, lang: str, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    if player and lang in ["fr", "en"]:
        player.language = lang; db.commit()
        pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
        return format_hud_data(pet, player, "lang_ok")
    return {"status": "error"}

@app.get("/action/set_skin")
def set_skin(uuid: str, skin_name: str, db: Session = Depends(get_db)):
    pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    data = logic.SKINS_DATA.get(skin_name)
    unlocked = pet.unlocked_skins.split(",")
    if skin_name not in unlocked:
        if player.flux < data["price"]: return format_hud_data(pet, player, "no_flux", str(data["price"]))
        player.flux -= data["price"]; unlocked.append(skin_name)
        pet.unlocked_skins = ",".join(unlocked)
        pet.current_skin = skin_name; db.commit()
        return format_hud_data(pet, player, "buy_ok", f"{skin_name}, {data['price']}")
    pet.current_skin = skin_name; db.commit(); return format_hud_data(pet, player)

@app.get("/action/resurrection")
def resurrect(uuid: str, db: Session = Depends(get_db)):
    pet = db.query(models.Laboubou).filter(models.Laboubou.owner_uuid == uuid).first()
    player = db.query(models.Player).filter(models.Player.uuid == uuid).first()
    if player.flux < 1500: return format_hud_data(pet, player, "no_flux", "1500")
    player.flux -= 1500; pet.health, pet.hunger, pet.thirst, pet.joy = 100, 100, 100, 100
    pet.status = "egg"; db.commit(); return format_hud_data(pet, player, "resu_ok")