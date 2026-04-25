# 03 — HUD JOUEUR (Interface System)

**Retour** : [[00-MASTER-Phase1]]

---

## OVERVIEW

**HUD** = Interface SL attrapée au joueur. Gère Kirou, montre jauges, permet interactions.

**Design** : Minimaliste, holographique, cyberpunk (Dark kawaii).

---

## LAYOUT VISUEL

```
┌──────────────────────────────────┐
│  [PROFILE] ⚙️ [FLUX] [SETTINGS]  │  ← Top bar
├──────────────────────────────────┤
│                                  │
│          🐱 KIROU DISPLAY        │  ← Main display
│     (3D animé, réactions)        │
│                                  │
├──────────────────────────────────┤
│  ❤️ 75%  💛 60%  💚 80%  💜 45%   │  ← Jauges quick view
├──────────────────────────────────┤
│  [FEED] [PLAY] [TALK] [SKIN]     │  ← Action buttons
└──────────────────────────────────┘
```

---

## SECTIONS

### 1. TOP BAR

**Left** :
- Avatar name
- Kirou nickname
- Current stage (Egg/Chaton/Chat/Awakened)

**Center** :
- HUD title "ORIGIN"

**Right** :
- Flux balance (e.g., "Flux: 450")
- Settings ⚙️ (click for options)

### 2. MAIN DISPLAY

**Kirou 3D Model** :
- Rotates slowly
- Animesh with expressions
- Responds to actions (plays animation)
- Shows current skin

**Status Indicator** :
- Orb pulses based on overall health
- Color changes based on dominant emotion (jauges)
- Green = healthy, Yellow = warning, Red = critical

### 3. JAUGES VITALES

4 bars affichées :

```
❤️  Hunger    [████░░░░░] 75%
💛  Happiness [██░░░░░░░] 60%
💚  Health    [████████░] 80%
💜  Bond      [████░░░░░] 45%
```

**Color coding** :
- Green (>70%) = OK
- Yellow (40-70%) = Warning
- Red (<40%) = Critical

### 4. ACTION BUTTONS

**[FEED]** :
- Opens food menu
- Shows available food types
- Costs Flux or item consumption

**[PLAY]** :
- Triggers playtime interaction
- Random mini-games or activities
- +Happiness, +Flux earned

**[TALK]** :
- Opens chat interface with Kirou IA
- Rita personality responds
- +Bond, +Flux earned

**[SKIN]** :
- Opens skin selector
- Shows unlocked skins
- Allows changing appearance
- Preview before applying

---

## SECONDARY PANELS

### PROFILE TAB

Shows player info :
- Nickname
- Kirou owned (if multiple later)
- Total Flux earned
- Account age
- Achievements unlocked

### SETTINGS ⚙️

Options :
- Volume (IA response sounds)
- Notification frequency
- HUD transparency
- Kirou expression sensitivity

---

## INTERACTIONS IN HUD

### Feed Kirou

**Flow** :
1. Click [FEED] button
2. Panel shows food options :
   - "Basic Meal" (1 Flux) → +20 hunger
   - "Deluxe Meal" (3 Flux) → +40 hunger
   - "Premium Treat" (5 Flux or 100 L$) → +60 hunger
3. Player selects food
4. HUD plays animation
5. Kirou eats, responds via IA
6. Hunger restored, Flux earned

### Play with Kirou

**Flow** :
1. Click [PLAY] button
2. Mini-activity spawns
3. Player interacts (e.g., click target, follow prompts)
4. Kirou plays with animations
5. +Happiness, +Flux (2-5)
6. IA comment : "That was fun!" / "Again! Again!"

### Talk to Kirou (IA)

**Flow** :
1. Click [TALK] button
2. Chat window opens
3. Player types message
4. Send to API → Gemini processes
5. IA response displays in HUD
6. +Bond, +Flux (2)
7. Kirou animation plays reaction

### Change Skin

**Flow** :
1. Click [SKIN] button
2. Skin selector opens with thumbnails
3. Player hovers to preview on Kirou
4. Click to apply (if unlocked)
5. Kirou model updates instantly
6. IA reacts : "New look! I like it!" / etc.

---

## FLUX ECONOMY DISPLAY

### Flux Counter

Always visible in top-right :
```
💎 Flux: 450 [+2 earned this session]
```

### Flux Spending

When player buys skin/food/etc :
```
Purchase: "Neon Skin" (300 Flux)
Confirm? [YES] [NO]

New balance: 450 - 300 = 150 Flux
```

### Daily Flux Limit (optional)

Could show progress bar :
```
Daily Quest: [████████░░] 80/100 Flux earned
```

---

## HUD TECHNICAL SPECS

### Attachment Point

- **Position** : HUD center (screen space)
- **Size** : ~600x600 pixels (resizable)
- **Depth** : Always on top layer

### State Sync

HUD polls API every 30 seconds :
```
GET /api/kirou/{id}/state
→ Updates all jauges display
→ Checks for stage transitions
→ Alerts if critical
```

### Real-time Updates

On player action :
```
POST /api/kirou/{id}/feed → Immediately update display
(not wait for poll cycle)
```

---

## LSL SCRIPT STRUCTURE

```lsl
// hud_main.lsl - Main HUD controller

default {
    state_entry() {
        // Initialize HUD
        llSetMemoryLimit(65536);
        llHTTPRequest(API_ENDPOINT, ["VERB", "GET"], "");
    }
    
    http_response(key request_id, integer status, list metadata, string body) {
        // Parse Kirou state
        // Update display elements
        // Render jauges
    }
    
    touch_start(integer num_detected) {
        // Handle button clicks
        // [FEED], [PLAY], [TALK], [SKIN]
    }
}
```

---

## FUTURE EXTENSIBILITY

**Phase 2 additions (don't code now)** :
- Multiple Kirous selector (if player has 2+)
- Breeding interface
- Card collection view
- Clan interface
- Marketplace access

**Architecture note** : Tab-based system allows easy addition without redesign.

---

**Status** : HUD design finalized, ready for LSL development
**Next** : Dev Roadmap

