# ORIGIN — Kirou Chat Tamagotchi
**Un compagnon intelligent sur Second Life, monétisé via vente d'œufs (750-1500 L$)**

**Objectif** : 200,000 L$/mois d'ici Octobre 2026

---

## 📋 Structure du Projet

```
origin-core/
├── docs/                    # GDD + Documentation
│   ├── GDD/                 # Game Design Documents
│   │   ├── 00-MASTER-Phase1.md
│   │   ├── 01-Business-Plan.md
│   │   ├── 02-Kirou-Tamagotchi.md
│   │   ├── 03-HUD-System.md
│   │   └── 04-Dev-Roadmap.md
│   ├── idées/               # Brainstorm
│   ├── images/              # Références visuelles
│   └── refs/                # Références externes
│
├── api/                     # Backend FastAPI (Production)
│   ├── main.py              # Routes FastAPI
│   ├── models.py            # SQLAlchemy ORM
│   ├── database.py          # Configuration DB
│   ├── logic.py             # Business logic
│   ├── config.py            # Settings
│   ├── requirements.txt      # Dépendances Python
│   └── Procfile             # Railway deployment
│
├── lsl/                     # Scripts Second Life
│   ├── hud_main.lsl         # HUD Interface joueur
│   ├── kirou.lsl            # Logique Kirou
│   └── rita.lsl             # Rita IA Chat
│
├── blender/                 # Modèles 3D
│   ├── kirou-chat.blend     # Modèle Kirou
│   └── animations/          # Fichiers animations
│
├── _archive/                # Scripts/code de reference (old)
│   ├── old_kirou/
│   ├── old_rita/
│   └── notes.md
│
├── tests/                   # Tests unitaires
│   ├── test_api.py
│   └── test_logic.py
│
├── README.md                # Ce fichier
├── .gitignore               # Git ignore rules
├── .env.example             # Template variables
└── .github/                 # GitHub config
    └── CONTRIBUTING.md      # Guide contribution
```

---

## 🚀 Quick Start

### Prérequis
- Python 3.10+
- PostgreSQL
- Second Life Viewer

### Installation

1. **Clone le repo**
```bash
git clone https://github.com/originlab3d/origin-core.git
cd origin-core
```

2. **Setup Python**
```bash
cd api
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows
pip install -r requirements.txt
```

3. **Config `.env`**
```bash
cp .env.example .env
# Édite .env avec tes variables Railway/Gemini/DB
```

4. **Run API localement**
```bash
uvicorn main:app --reload
```

API accessible sur `http://localhost:8000`

---

## 📦 Déploiement Railway

### Setup Railway

1. **Connecte ton repo GitHub à Railway** : https://railway.app
2. **Railway détecte automatiquement** Python + FastAPI
3. **Variables d'environnement** : Configure dans Railway dashboard
4. **Chaque push** → déploiement auto

### Variables Railway requises
```
DATABASE_URL=postgresql://user:pwd@host/dbname
GEMINI_API_KEY=ton_api_key
FLASK_ENV=production
```

---

## 🎮 Phases de Développement

### Phase 1 — L'Éclosion (Mai-Oct 2026)
- ✅ Backend FastAPI (jauges, interactions, Flux)
- 🔴 HUD SL (interface joueur)
- 🔴 Kirou 3D (modèle + animations)
- 🔴 IA Rita intégrée
- 🔴 Marketplace listing

### Phase 2 — L'Ascension (2026-2027)
- Breeding génétique
- Combat de cartes
- Clans & territoire

### Phase 3 — L'Infini (2028-2030)
- UE5 migration
- Cross-platform

---

## 💡 Technos

| Stack | Tech |
|-------|------|
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| IA | Gemini API |
| Second Life | LSL scripting |
| 3D | Blender (Animesh) |
| Hosting | Railway |
| VCS | GitHub |

---

## 📊 Économie (Phase 1)

**Revenu** : 200,000 L$/mois
- Vente œuf Kirou : 750-1500 L$ × 100-180 joueurs
- Skins/Animations : Flux ou L$

**Coûts** : ~$50/mois
- Railway hosting : $15
- Gemini API : $20-40

**Margin** : ~93%

---

## 🔗 Liens Utiles

- **GDD Master** : `/docs/GDD/00-MASTER-Phase1.md`
- **Dev Roadmap** : `/docs/GDD/04-Dev-Roadmap.md`
- **Railway Dashboard** : https://railway.app
- **Gemini API Docs** : https://ai.google.dev

---

## 📝 Contribution

Voir `/github/CONTRIBUTING.md`

---

**Status** : Phase 1 en développement  
**Launch** : Octobre 2026  
**Créateur** : OriginLab  

