# 02 — KIROU TAMAGOTCHI (Core Mechanics)

**Retour** : [[00-MASTER-Phase1]]

---

## OVERVIEW

**Kirou** = Compagnon tamagotchi intelligent avec IA, attaché au profil joueur.

**Lifecycle** :
1. **Achat œuf** (750-1500 L$)
2. **Éclosion** (free, tutoriel)
3. **Croissance** (Œuf → Chaton → Chat → Chat Éveillé)
4. **Interactions IA** (réactions personnalisées)
5. **Mort** (si négligé 7+ jours)

---

## JAUGES VITALES (4 Core Stats)

Chaque Kirou a 4 jauges qui baissent naturellement dans le temps :

### 1. Faim (❤️)
- **Baisse** : 5% par heure sans nourriture
- **Limite** : 0-100%
- **Critique** : <20% = Kirou triste, IA devient déprimée
- **Restaurée par** : Nourrir avec des items ou Flux

### 2. Bonheur (💛)
- **Baisse** : 3% par heure sans interaction
- **Limite** : 0-100%
- **Restaurée par** : Jouer, caresser, interagir avec IA
- **Bonus** : Interactions IA longues = +bonheur plus

### 3. Santé (💚)
- **Baisse** : 2% par heure naturellement
- **Limite** : 0-100%
- **Dégradation** : Si Faim + Bonheur critiques pendant 24h, santé dégringole
- **Restaurée par** : Potions soin (premium, Flux ou L$)

### 4. Lien (💜)
- **Augmente** : Par interactions joueur ↔ IA
- **Limite** : 0-100%
- **Fonction** : Plus le lien est fort, plus IA réagit intelligemment
- **Bloqué à 0** : Si mort, Lien revient lentement après revivification

---

## STADES ÉVOLUTIFS

Structure simple, extensible pour Phase 2 :

| Stade | Durée | Appearance | Mécaniques |
|-------|-------|-----------|-----------|
| **Œuf** | 0-5 jours | Œuf animé | Aucun (juste "brooding") |
| **Chaton** | 5-20 jours | Petit chat mignon | Jauges basiques, IA simple |
| **Chat** | 20-60 jours | Chat adulte | Jauges complètes, IA riche |
| **Éveillé** | 60+ jours | Chat lumineux/évolué | Déblocage skins rares, IA avancée |

**Trigger transitions** : 
- Temps passé
- Jauges au-dessus de seuil minimum
- Lien > 50%

---

## IA INTELLIGENTE (Rita Integration)

### Rita Personality System

**Basé sur** : personality_core.py (Rita)

**Adaptations pour Kirou** :
- Réactions basées sur **état des jauges** (faim = grincheux)
- Réactions basées sur **stade évolution** (chaton = immature)
- Réactions basées sur **lien joueur** (nouveau = distant, ancien = affectueux)

### Exemples de Réactions IA

**Si Faim critique (< 20%)** :
```
"Je meurs de faim... aide-moi... 🥺"
"Mon ventre gronde depuis des heures..."
"Pourquoi m'oublies-tu comme ça?"
```

**Si Bonheur faible + Chaton**:
```
"Je m'ennuie... joue avec moi! 😿"
"C'est pas amusant seul ici..."
```

**Si Lien fort + Chat adulte**:
```
"Tu m'as manqué! Je t'ai tellement attendu 😻"
"Notre lien s'est renforcé... je sens qu'on est vraiment connectés"
```

**Si Santé critique (< 10%)**:
```
"Je ne me sens pas bien... j'ai besoin d'aide..."
"Ça fait très mal... s'il te plaît... 😢"
```

---

## DEATH SYSTEM

### Death Trigger

Kirou meurt si :
- **Santé = 0** OU
- **Négligé 7+ jours** (aucune interaction)

### Death Mechanics

**Mort** :
- HUD affiche message "Ton Kirou s'est endormi... pour toujours"
- Kirou devient gris/translucide
- IA silencieuse

**Revival** :
- Coûte 1000 Flux (pressant!)
- Kirou revient, mais Lien reset à 0
- Jauges = 50%
- Message IA : "Je me suis réveillé... où étais-tu?"

### Death Prevention

- **Daily Reminder** : Si pas connecté depuis 2j, Discord ping
- **Grace Period** : 7 jours avant mort finale
- **Revival Cost** : Assez haut pour être pressant, mais pas prohibitif

---

## SKINS & CUSTOMIZATION (6-7 options)

### Skin Categories

**Base** (inclus) :
1. **Default Chat** — Chat noir de base (ref image)

**Flux-Unlock** (gagné par gameplay) :
2. **Neon Chat** — Chat avec particles néon
3. **Golden Chat** — Chat couleur or
4. **Ghost Chat** — Chat translucide/spectral
5. **Punk Chat** — Chat avec "emo" esthétique

**Premium L$** (achetable uniquement en L$) :
6. **Diamond Chat** — Chat scintillant premium
7. **Ethereal Chat** — Chat lumineux magique

### Skin Unlock Progression

```
Level 1 : Accès "Neon Chat" (200 Flux)
Level 5 : Accès "Golden Chat" (300 Flux)
Level 10 : Accès "Ghost Chat" (250 Flux) + Diamond Chat (500 L$)
Level 15+ : Punk Chat (350 Flux) + Ethereal Chat (750 L$)
```

---

## GESTURES & ANIMATIONS

**6-7 animations** pour exprimer l'IA :

1. **Purr** — Chat ronronne (happy state)
2. **Meow** — Chat miaule (seeking attention)
3. **Sleep** — Chat dort (recharge lentement jauges)
4. **Jump** — Chat saute (excited)
5. **Pounce** — Chat attaque (playful)
6. **Stretch** — Chat s'étire (morning)
7. **Cuddle** — Chat cherche caresses (low happiness)

### Animation Triggers

```
IF Bonheur > 70 → Purr/Jump animations play
IF Faim > 80 → Meow/Pounce animations
IF Lien > 50 AND Player nearby → Cuddle animation
IF (Heure SL == 0) → Sleep animation
```

---

## INTERACTIONS MECHANICS

### Player Actions

| Action | Effect | IA Response |
|--------|--------|-------------|
| **Nourrir** | Faim +30 | "Merci! Délicieux!" |
| **Jouer** | Bonheur +20 | "Ouais! C'était amusant!" |
| **Caresser** | Lien +10 | Purr animation |
| **Parler** | Lien +5, Interaction IA | Rita responses |
| **Soigner** | Santé +30-100 | "Je me sens mieux..." |

### Flux Earning

- Nourrir Kirou : 1 Flux
- Jouer : 2-5 Flux (selon durée)
- Caresser : 1 Flux
- Parler IA : 2 Flux (si réponse longue)
- Quête quotidienne : 50-100 Flux

---

## DATABASE SCHEMA

```sql
CREATE TABLE kirous (
  id UUID PRIMARY KEY,
  owner_uuid UUID REFERENCES players(uuid),
  
  -- State
  hunger INTEGER (0-100),
  happiness INTEGER (0-100),
  health INTEGER (0-100),
  bond INTEGER (0-100),
  
  -- Evolution
  stage VARCHAR (egg, chaton, chat, awakened),
  age_days INTEGER,
  
  -- Customization
  skin VARCHAR (default, neon, golden, ghost, punk, diamond, ethereal),
  
  -- Status
  is_alive BOOLEAN DEFAULT true,
  last_interaction TIMESTAMP,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

## API ENDPOINTS (LSL → Python)

```python
# Sync Kirou state
GET /api/kirou/{kirou_id}/state
Response: { hunger: 45, happiness: 60, health: 75, bond: 30, stage: "chat" }

# Feed Kirou
POST /api/kirou/{kirou_id}/feed
Body: { food_type: "basic" }
Response: { hunger: 75, flux_earned: 1 }

# Play with Kirou
POST /api/kirou/{kirou_id}/play
Response: { happiness: 80, flux_earned: 5, animation: "jump" }

# Talk to Kirou (IA)
POST /api/kirou/{kirou_id}/talk
Body: { message: "Ça va?" }
Response: { 
  ai_response: "Ça va mieux maintenant que tu es là! 😻",
  bond: +10,
  flux_earned: 2
}

# Revive Kirou
POST /api/kirou/{kirou_id}/revive
Body: { flux_cost: 1000 }
Response: { is_alive: true, message: "Kirou is back!" }
```

---

**Status** : Core mechanics defined, ready for dev
**Next** : HUD System design

