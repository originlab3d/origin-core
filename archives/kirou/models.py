# models.py
# Fichier de définition des tables de la base de données (SQLAlchemy)

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func 
from database import Base

class Player(Base):
    """
    Table représentant le joueur (le propriétaire du Kibou)
    """
    __tablename__ = "players"
    
    # id unique interne (plus rapide pour les recherches SQL)
    id = Column(Integer, primary_key=True, index=True)
    # UUID Second Life de l'avatar (clé de recherche principale)
    uuid = Column(String, unique=True, index=True) 
    # Monnaie du jeu (Flux)
    flux = Column(Integer, default=500) 
    # Préférence de langue (fr ou en)
    language = Column(String, default="fr")

class Laboubou(Base):
    """
    Table représentant le Kibou (le compagnon)
    """
    __tablename__ = "laboubou"
    
    id = Column(Integer, primary_key=True, index=True)
    # Lien avec le propriétaire
    owner_uuid = Column(String, ForeignKey("players.uuid")) 
    
    # --- IDENTITÉ ---
    custom_name = Column(String, default="Kibou")
    # egg, baby, adult, elite, legendaire
    status = Column(String, default="egg") 
    # Skin actuellement utilisé par l'objet SL
    current_skin = Column(String, default="skin_1") 
    
    # --- ADN & GÉNÉTIQUE (Nouveautés) ---
    # Commun, Rare, Épique, Légendaire
    rarity = Column(String, default="Commun")
    # Feu, Eau, Terre, Air, Foudre, Lumière, Ombre
    element = Column(String, default="Terre")
    # Mâle ou Femelle
    sex = Column(String, default="?") 
    
    # --- STATISTIQUES ---
    # Santé (0-100)
    health = Column(Float, default=100.0) 
    # Faim (0-100)
    hunger = Column(Float, default=100.0) # Départ à 100 pour la naissance
    # Soif (0-100)
    thirst = Column(Float, default=100.0) 
    # Joie (0-100)
    joy = Column(Float, default=100.0)
    
    # --- PROGRESSION ---
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    # Liste des skins débloqués (format : "skin_1,skin_2")
    unlocked_skins = Column(String, default="skin_1") 

    # --- TIMESTAMPS ---
    # Date de création du Kibou (Naissance)
    birth_date = Column(DateTime(timezone=True), server_default=func.now())
    # Dernière mise à jour des statistiques (important pour le calcul hors-ligne)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())