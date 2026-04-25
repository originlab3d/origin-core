# 04 — DEVELOPMENT ROADMAP (May-Oct 2026)

**Retour** : [[00-MASTER-Phase1]]

---

## TIMELINE OVERVIEW

```
MAY       JUN       JUL       AUG       SEP       OCT
|---------|---------|---------|---------|---------|
Alpha      Beta     Stress    Final     Launch
Dev                 Test      Polish    Prep
```

---

## PHASE 1 : ALPHA DEVELOPMENT (May)

### Week 1-2 : Foundation

**Backend** :
- [ ] FastAPI project scaffold
- [ ] PostgreSQL schema creation (players, kirous)
- [ ] Auth system (UUID validation)
- [ ] Basic CRUD endpoints

**Frontend** :
- [ ] HUD prototype mockup (GIMP/Photoshop)
- [ ] Kirou 3D model rigging (Blender)
- [ ] Animation skeleton (purr, meow, sleep, jump)

**AI Integration** :
- [ ] Integrate Gemini API calls
- [ ] Adapt personality_core.py for Kirou context
- [ ] Test IA responses with gauge states

### Week 3-4 : Core Systems

**Backend** :
- [ ] Jauge calculation engine (hunger decay, etc.)
- [ ] Interaction handlers (feed, play, talk)
- [ ] Flux earning/spending logic
- [ ] Death/revival system

**HUD Development** :
- [ ] LSL HUD script foundation
- [ ] Button logic (feed, play, talk, skin)
- [ ] Jauge display rendering
- [ ] HTTP request handler to backend

**Testing** :
- [ ] Unit tests on backend (pytest)
- [ ] Manual SL testing (basic HUD)

---

## PHASE 2 : BETA DEVELOPMENT (June)

### Week 1-2 : Systems Refinement

**Backend** :
- [ ] Stage evolution logic (egg→chaton→chat→awakened)
- [ ] Skin unlock system
- [ ] IA response caching (reduce API calls)
- [ ] Database optimization

**HUD** :
- [ ] Kirou 3D display in HUD (Animesh)
- [ ] Skin switching mechanism
- [ ] Settings panel implementation
- [ ] Animation triggers

**AI** :
- [ ] Test 1000+ varied responses
- [ ] Adjust personality for different stages
- [ ] Handle edge cases (critical hunger, death, etc.)

### Week 3-4 : Monetization

**Backend** :
- [ ] L$ transaction handler (llTransferLindenDollars)
- [ ] Egg purchase flow
- [ ] Flux purchase bundles (optional premium)
- [ ] Account balance verification

**Marketplace** :
- [ ] Create marketplace listing template
- [ ] Set up Marketplace keywords
- [ ] Photography/marketing materials

---

## PHASE 3 : STRESS TEST & POLISH (July)

### Week 1-2 : Load Testing

**Infrastructure** :
- [ ] Load test with 50 concurrent users
- [ ] Database query optimization
- [ ] Gemini API rate limiting
- [ ] Railway auto-scaling config

**Bug Hunting** :
- [ ] Full gameplay walkthroughs
- [ ] Edge case testing (poor network, etc.)
- [ ] IA response quality audit
- [ ] Animation glitch fixes

### Week 3-4 : User Experience

**HUD Refinement** :
- [ ] Accessibility audit (font sizes, colors)
- [ ] Performance optimization (script lag)
- [ ] Tutorial flow
- [ ] Help documentation

**IA Fine-tuning** :
- [ ] Response variety increase
- [ ] Emotion transitions smoothing
- [ ] Edge case handling

---

## PHASE 4 : FINAL POLISH (August)

### Week 1-2 : Feature Completion

**All Systems** :
- [ ] Death/revival mechanics tested
- [ ] Daily reminder system (Discord ping)
- [ ] Achievements foundation (if wanted)
- [ ] Flux earning rebalance

**Documentation** :
- [ ] User guide (how to feed, play, talk, change skin)
- [ ] Troubleshooting guide
- [ ] Backend API documentation (for future devs)

### Week 3-4 : Marketing Prep

**Visual Assets** :
- [ ] Kirou screenshots (multiple skins)
- [ ] HUD UI showcase
- [ ] Animation clips (GIF/video)
- [ ] Comparison images (before/after interactions)

**Copy** :
- [ ] Product description
- [ ] Marketplace listing
- [ ] Twitter/Discord announcements
- [ ] FAQ

---

## PHASE 5 : LAUNCH PREP (September)

### Week 1-2 : Soft Launch

**Testing Environment** :
- [ ] Release to 10-20 trusted users
- [ ] Gather feedback
- [ ] Fix critical bugs only
- [ ] Monitor server stability

**Monitoring** :
- [ ] Set up error logging (Sentry or similar)
- [ ] User analytics (basic: login, purchases)
- [ ] Gemini API call tracking

### Week 3-4 : Launch Day Prep

**Infrastructure** :
- [ ] Database backups automated
- [ ] Server monitoring active
- [ ] Support channels ready (Discord)
- [ ] Emergency hotfix plan

**Marketing** :
- [ ] Social media scheduled posts (Twitter, Instagram)
- [ ] Marketplace listing live
- [ ] Community discord created
- [ ] In-world events planned

---

## PHASE 6 : LAUNCH & BEYOND (October)

### Week 1-2 : LAUNCH DAY

- [ ] Marketplace live & available
- [ ] Initial batch of eggs (100-200 reserved for launch)
- [ ] Marketing push begins
- [ ] Community support active (24h response)

### Week 3-4 : Post-Launch Monitoring

- [ ] Track concurrent users
- [ ] Monitor revenue/purchases
- [ ] Gather user feedback
- [ ] Plan Phase 2 roadmap

---

## DELIVERABLES CHECKLIST

### Code

- [ ] FastAPI backend (production-ready)
- [ ] PostgreSQL schemas
- [ ] LSL HUD scripts
- [ ] Blender Kirou model + animations
- [ ] personality_core.py adapted for Kirou

### Assets

- [ ] Kirou 3D model (default + skins)
- [ ] HUD texture/layout
- [ ] Marketing images
- [ ] Documentation

### Infrastructure

- [ ] Railway deployment configured
- [ ] Database backups
- [ ] Gemini API integration
- [ ] Error monitoring

### Business

- [ ] Marketplace listing
- [ ] Marketing plan executed
- [ ] Community channels active
- [ ] Support system ready

---

## RISKS & CONTINGENCIES

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gemini API rate-limit | Medium | High | Implement response caching + queue system |
| LSL script lag | Medium | Medium | Optimize script, limit update frequency |
| Database scaling | Low | High | Use connection pooling, optimize queries |
| Poor adoption | Medium | High | Strong marketing, community engagement |
| Kirou model issues | Low | Medium | Test on multiple SL viewers early |

---

## RESOURCE REQUIREMENTS

### Development Team (Estimated)

- **Backend Dev** : 1 (FastAPI/Python)
- **LSL Developer** : 1 (SL scripting)
- **3D Artist** : 1 (Blender modeling + animation)
- **You (Product/QA)** : Oversight

### Tools & Services

- Blender (free)
- VS Code / PyCharm (free)
- PostgreSQL (free)
- Railway hosting ($15/month)
- Gemini API (pay-per-use, ~$20-50/month)

### Total Monthly Cost

**$50-80/month** for infrastructure

---

## SUCCESS METRICS (Launch)

- **100+ players** in first month
- **Average retention** : 30+ days per player
- **Repeat purchase rate** : 15%+ (skins, animations)
- **Monthly revenue** : 200K+ L$
- **Server uptime** : 99%+
- **Average response time** : <200ms

---

## NEXT STEPS

1. **Assemble team** (if needed)
2. **Set up repos** (GitHub branches for each phase)
3. **Assign ownership** (who leads what)
4. **Begin Alpha development** (Week of May X)
5. **Weekly sync** (progress check-ins)

---

**Status** : Roadmap defined, ready to execute
**Target Launch** : October 1, 2026
**Estimated Days to Launch** : ~150 days of dev

