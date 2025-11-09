# Deployment Strategies - Quick Reference Diagram

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    JENKINS PARAMETERIZED DEPLOYMENT STRATEGIES                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────────┐
│                            DEPLOYMENT STRATEGY SELECTOR                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Parameter: DEPLOYMENT_STRATEGY                                               │
│                                                                                │
│  ┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   AUTO   │  │  BLUE-GREEN  │  │ CANARY  │  │    SHADOW    │  │ A/B TEST │ │
│  │  (Smart) │  │ (Zero Down)  │  │(Gradual)│  │  (Testing)   │  │(Compare) │ │
│  └────┬─────┘  └──────┬───────┘  └────┬────┘  └──────┬───────┘  └────┬─────┘ │
│       │                │                │               │                │      │
│       ▼                ▼                ▼               ▼                ▼      │
│  Branch-based    Instant Switch   10→50→100%    Mirror Traffic      50/50     │
│  Selection       Blue ⟷ Green     Traffic Steps   No Impact          Split     │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                           🔵🟢 BLUE-GREEN DEPLOYMENT                           │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   ┌─────────────────┐                        ┌─────────────────┐              │
│   │   BLUE (old)    │                        │  GREEN (new)    │              │
│   │   ┌─────────┐   │                        │   ┌─────────┐   │              │
│   │   │  v1.0   │   │   Deploy New Version   │   │  v1.1   │   │              │
│   │   │ Running │   │  ─────────────────────▶│   │ Deploy  │   │              │
│   │   └─────────┘   │                        │   └─────────┘   │              │
│   └─────────────────┘                        └─────────────────┘              │
│           │                                           │                        │
│           │  100% Traffic                             │  0% Traffic            │
│           ▼                                           ▼                        │
│   ┌───────────────────┐                      ┌───────────────────┐            │
│   │     SERVICE       │    Health Check ✓    │     SERVICE       │            │
│   │  (active: blue)   │    Switch Traffic    │  (active: green)  │            │
│   └───────────────────┘  ────────────────▶   └───────────────────┘            │
│           │                                           │                        │
│           │  0% Traffic                               │  100% Traffic          │
│           ▼                                           ▼                        │
│   ┌─────────────────┐                        ┌─────────────────┐              │
│   │   BLUE (old)    │                        │  GREEN (new)    │              │
│   │  (kept for      │                        │  (now active)   │              │
│   │   rollback)     │                        │                 │              │
│   └─────────────────┘                        └─────────────────┘              │
│                                                                                │
│   ✅ Zero downtime   ✅ Instant rollback   ✅ Full testing   ❌ 2x resources  │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                            🕯️ CANARY DEPLOYMENT                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   Step 1: Deploy Canary                  Step 2: 10% Traffic                  │
│   ┌───────────────────────┐              ┌───────────────────────┐            │
│   │  STABLE (v1.0)        │              │  STABLE (v1.0)        │            │
│   │  ████████████████     │              │  █████████████        │ 90%        │
│   └───────────────────────┘              └───────────────────────┘            │
│                                          ┌───────────────────────┐            │
│   ┌───────────────────────┐              │  CANARY (v1.1)        │            │
│   │  CANARY (v1.1)        │              │  █                    │ 10%        │
│   │  (deploying...)       │              └───────────────────────┘            │
│   └───────────────────────┘                                                   │
│                                               ⏰ Wait 120s                     │
│                                                                                │
│   Step 3: 50% Traffic                    Step 4: 100% Traffic                 │
│   ┌───────────────────────┐              ┌───────────────────────┐            │
│   │  STABLE (v1.0)        │              │  CANARY (v1.1)        │            │
│   │  ███████              │ 50%          │  ████████████████     │ 100%       │
│   └───────────────────────┘              └───────────────────────┘            │
│   ┌───────────────────────┐              ┌───────────────────────┐            │
│   │  CANARY (v1.1)        │              │  STABLE (v1.0)        │            │
│   │  ███████              │ 50%          │  (can remove)         │ 0%         │
│   └───────────────────────┘              └───────────────────────┘            │
│        ⏰ Wait 120s                                                            │
│                                                                                │
│   Parameters:                                                                 │
│   CANARY_TRAFFIC_STEPS: 10,50,100 | 20,40,60,80,100 | 25,75,100             │
│   CANARY_WAIT_TIME: 60-600 seconds                                           │
│                                                                                │
│   ✅ Gradual risk   ✅ Monitor each step   ✅ Auto rollback   ❌ Slower       │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                           👤 SHADOW DEPLOYMENT                                 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   ┌──────────────────────────────────────────────────────────────────────┐    │
│   │                          USER REQUEST                                │    │
│   └────────────────────────────┬─────────────────────────────────────────┘    │
│                                │                                              │
│                                ▼                                              │
│                    ┌───────────────────────┐                                  │
│                    │   LOAD BALANCER       │                                  │
│                    └───────┬───────────────┘                                  │
│                            │                                                  │
│            ┌───────────────┴────────────────┐                                │
│            │                                 │                                │
│            ▼                                 ▼                                │
│   ┌────────────────────┐          ┌────────────────────┐                     │
│   │  PRODUCTION v1.0   │          │   SHADOW v1.1      │                     │
│   │  ┌──────────────┐  │          │  ┌──────────────┐  │                     │
│   │  │   Process    │  │  Mirror  │  │   Process    │  │                     │
│   │  │   Request    │  │  Traffic │  │   Request    │  │                     │
│   │  │              │  │ ────────▶│  │              │  │                     │
│   │  │   Return     │  │  100%    │  │   Discard    │  │                     │
│   │  │   Response   │  │          │  │   Response   │  │                     │
│   │  └──────────────┘  │          │  └──────────────┘  │                     │
│   └─────────┬──────────┘          └────────────────────┘                     │
│             │                              │                                  │
│             │ Real Response                │ No Response                      │
│             │ to User                      │ (only logs)                      │
│             ▼                              ▼                                  │
│        ┌─────────┐                  ┌──────────────┐                         │
│        │  USER   │                  │   METRICS    │                         │
│        └─────────┘                  │   & LOGS     │                         │
│                                     └──────────────┘                         │
│                                                                                │
│   ✅ Zero user impact   ✅ Real traffic   ✅ Performance test   ❌ 2x cost    │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                          🔬 A/B TESTING DEPLOYMENT                             │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   ┌──────────────────────────────────────────────────────────────────────┐    │
│   │                        INCOMING TRAFFIC                              │    │
│   └────────────────────────────┬─────────────────────────────────────────┘    │
│                                │                                              │
│                                ▼                                              │
│                    ┌───────────────────────┐                                  │
│                    │   TRAFFIC SPLITTER    │                                  │
│                    │  (Istio VirtualSvc)   │                                  │
│                    └───────┬───────────────┘                                  │
│                            │                                                  │
│              ┌─────────────┴─────────────┐                                   │
│              │ 50%              50%      │   (Configurable: AB_TRAFFIC_SPLIT) │
│              ▼                           ▼                                    │
│   ┌──────────────────────┐    ┌──────────────────────┐                       │
│   │   VARIANT A (v1.0)   │    │   VARIANT B (v1.1)   │                       │
│   │  ┌────────────────┐  │    │  ┌────────────────┐  │                       │
│   │  │  Old Feature   │  │    │  │  New Feature   │  │                       │
│   │  │  Blue Button   │  │    │  │  Green Button  │  │                       │
│   │  └────────────────┘  │    │  └────────────────┘  │                       │
│   └──────────┬───────────┘    └──────────┬───────────┘                       │
│              │                            │                                   │
│              ▼                            ▼                                   │
│   ┌──────────────────────┐    ┌──────────────────────┐                       │
│   │  METRICS & ANALYTICS │    │  METRICS & ANALYTICS │                       │
│   │  • Conversion: 3.2%  │    │  • Conversion: 4.8%  │                       │
│   │  • Bounce: 45%       │    │  • Bounce: 38%       │                       │
│   │  • Time: 2.5min      │    │  • Time: 3.1min      │                       │
│   └──────────────────────┘    └──────────────────────┘                       │
│                                                                                │
│   Header Routing: x-variant: B → Always route to Variant B                   │
│   Cookie Routing: Consistent experience per user session                     │
│                                                                                │
│   ✅ Data-driven   ✅ Compare features   ✅ Measure KPIs   ❌ Need analytics  │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                          🔄 ROLLING UPDATE DEPLOYMENT                          │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   Step 1: Initial State          Step 2: Pod 1 Updating                      │
│   ┌────┐ ┌────┐ ┌────┐           ┌────┐ ┌────┐ ┌────┐                       │
│   │ v1 │ │ v1 │ │ v1 │           │ v2 │ │ v1 │ │ v1 │                       │
│   └────┘ └────┘ └────┘           └────┘ └────┘ └────┘                       │
│     ✓      ✓      ✓                ↻      ✓      ✓                          │
│                                                                                │
│   Step 3: Pod 2 Updating          Step 4: Complete                           │
│   ┌────┐ ┌────┐ ┌────┐           ┌────┐ ┌────┐ ┌────┐                       │
│   │ v2 │ │ v2 │ │ v1 │           │ v2 │ │ v2 │ │ v2 │                       │
│   └────┘ └────┘ └────┘           └────┘ └────┘ └────┘                       │
│     ✓      ↻      ✓                ✓      ✓      ✓                          │
│                                                                                │
│   Configuration:                                                              │
│   • maxSurge: 1 (max 1 extra pod during update)                              │
│   • maxUnavailable: 0 (always maintain full capacity)                        │
│   • revisionHistoryLimit: 10 (keep 10 previous versions)                     │
│                                                                                │
│   ✅ Simple   ✅ Built-in K8s   ✅ No extra resources   ❌ No traffic control │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                        ⚙️ PIPELINE PARAMETERS MATRIX                          │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   DEPLOYMENT_STRATEGY     ┌────────┬────────┬────────┬────────┬────────┐     │
│   ├─ auto                 │ Branch │  Env   │ Deploy │ Manual │Rollback│     │
│   ├─ blue-green           │  main  │  prod  │  auto  │   ✓    │   ✓    │     │
│   ├─ canary               │develop │staging │  auto  │   ✗    │   ✓    │     │
│   ├─ rolling-update       │feature │  dev   │ manual │   ✗    │   ✓    │     │
│   ├─ shadow               └────────┴────────┴────────┴────────┴────────┘     │
│   └─ ab-testing                                                               │
│                                                                                │
│   SKIP_TESTS              ☐ false (run tests)                                │
│                           ☐ true (skip - not recommended)                    │
│                                                                                │
│   SKIP_SONAR              ☐ false (run analysis)                             │
│                           ☐ true (skip for speed)                            │
│                                                                                │
│   SKIP_SECURITY_SCAN      ☐ false (run Trivy)                                │
│                           ☐ true (skip for speed)                            │
│                                                                                │
│   AUTO_ROLLBACK           ☑ true (recommended)                               │
│                           ☐ false (manual rollback only)                     │
│                                                                                │
│   MANUAL_APPROVAL         ☐ false (auto deploy)                              │
│                           ☐ true (wait for approval)                         │
│                                                                                │
│   CANARY_TRAFFIC_STEPS    ┌─────────────────────────────────────┐            │
│                           │ 10,50,100 (conservative - 3 steps)  │            │
│                           │ 20,40,60,80,100 (fine - 5 steps)    │            │
│                           │ 25,75,100 (aggressive - 3 steps)    │            │
│                           │ 10,30,50,70,100 (balanced - 5 steps)│            │
│                           └─────────────────────────────────────┘            │
│                                                                                │
│   CANARY_WAIT_TIME        [120] seconds (60-600 recommended)                 │
│                                                                                │
│   AB_TRAFFIC_SPLIT        [50] percent for variant B (0-100)                 │
│                           • 50 = equal split (50/50)                         │
│                           • 30 = conservative (70/30)                        │
│                           • 80 = aggressive (20/80)                          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                            🔙 ROLLBACK STRATEGIES                              │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   ┌────────────────┬──────────────────────┬───────────────────────────────┐   │
│   │   Strategy     │   Rollback Method    │   Command                     │   │
│   ├────────────────┼──────────────────────┼───────────────────────────────┤   │
│   │ Blue-Green     │ Switch service       │ kubectl patch service...      │   │
│   │                │ selector back        │   -p '{"spec":{"selector":    │   │
│   │                │                      │   {"color":"blue"}}}'         │   │
│   ├────────────────┼──────────────────────┼───────────────────────────────┤   │
│   │ Canary         │ Set canary traffic   │ kubectl patch virtualservice  │   │
│   │                │ to 0%, delete canary │   weight: 0 for canary        │   │
│   ├────────────────┼──────────────────────┼───────────────────────────────┤   │
│   │ Rolling Update │ K8s rollback to      │ kubectl rollout undo          │   │
│   │                │ previous revision    │   deployment/aceest-web       │   │
│   ├────────────────┼──────────────────────┼───────────────────────────────┤   │
│   │ Shadow         │ Delete shadow        │ kubectl delete deployment     │   │
│   │                │ deployment           │   aceest-web-shadow           │   │
│   ├────────────────┼──────────────────────┼───────────────────────────────┤   │
│   │ A/B Testing    │ Shift 100% to        │ kubectl patch virtualservice  │   │
│   │                │ variant A            │   weight: 100 for A, 0 for B  │   │
│   └────────────────┴──────────────────────┴───────────────────────────────┘   │
│                                                                                │
│   Automatic Rollback (AUTO_ROLLBACK: true):                                  │
│   1. Pre-deployment: Save current image → PREVIOUS_DEPLOYMENT                │
│   2. Deployment: Apply new image                                             │
│   3. On Failure: Restore PREVIOUS_DEPLOYMENT image automatically             │
│   4. Verification: Wait for rollout completion                               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                          📊 DECISION TREE                                      │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│                          Need to test without user impact?                    │
│                                    ├─ YES → SHADOW                            │
│                                    └─ NO ↓                                    │
│                                                                                │
│                          Need instant rollback capability?                    │
│                                    ├─ YES → BLUE-GREEN                        │
│                                    └─ NO ↓                                    │
│                                                                                │
│                          Need gradual rollout with monitoring?                │
│                                    ├─ YES → CANARY                            │
│                                    └─ NO ↓                                    │
│                                                                                │
│                          Need to compare two versions?                        │
│                                    ├─ YES → A/B TESTING                       │
│                                    └─ NO ↓                                    │
│                                                                                │
│                          Standard deployment                                  │
│                                    └─ ROLLING UPDATE                          │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                     LEGEND & QUICK REFERENCE                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Symbols:                                                                     ║
║  ✅ Advantage    ❌ Disadvantage    ⏰ Wait time    ✓ Ready    ↻ Updating     ║
║  ▶ Deploy       ⟷ Switch           → Flow         ▼ Down      ☑ Enabled      ║
║                                                                               ║
║  Time to Deploy:                                                              ║
║  • Rolling Update: ~5 minutes                                                 ║
║  • Blue-Green: ~10 minutes                                                    ║
║  • Canary (3 steps): ~15 minutes                                              ║
║  • Shadow: ~10 minutes (+ monitoring time)                                    ║
║  • A/B Testing: ~10 minutes (+ experiment time)                               ║
║                                                                               ║
║  Resources Required:                                                          ║
║  • Rolling Update: 1x                                                         ║
║  • Blue-Green: 2x                                                             ║
║  • Canary: 1.1x - 1.3x                                                        ║
║  • Shadow: 2x                                                                 ║
║  • A/B Testing: 2x                                                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
