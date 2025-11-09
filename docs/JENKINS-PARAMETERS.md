# Jenkins Pipeline Parameters - Quick Reference

## Pipeline Parameters Overview

### 📋 Deployment Strategy Selection

**Parameter:** `DEPLOYMENT_STRATEGY`  
**Type:** Choice  
**Default:** `auto`  

**Options:**
```
┌────────────────┬──────────────────────────────────────────────────────┐
│ Value          │ Description                                          │
├────────────────┼──────────────────────────────────────────────────────┤
│ auto           │ Branch-based: main→blue-green, develop→canary       │
│ blue-green     │ Zero-downtime with instant rollback                 │
│ canary         │ Gradual traffic shift (10%→50%→100%)               │
│ rolling-update │ Standard Kubernetes deployment                      │
│ shadow         │ Mirror traffic for testing (no user impact)         │
│ ab-testing     │ Split traffic for A/B comparison                    │
└────────────────┴──────────────────────────────────────────────────────┘
```

---

### 🕯️ Canary-Specific Parameters

**Parameter:** `CANARY_TRAFFIC_STEPS`  
**Type:** Choice  
**Default:** `10,50,100`  

**Options:**
```
┌────────────────────┬──────────────────────────────────────────────┐
│ Value              │ Traffic Distribution                         │
├────────────────────┼──────────────────────────────────────────────┤
│ 10,50,100          │ Conservative (3 steps)                      │
│ 20,40,60,80,100    │ Fine-grained (5 steps)                      │
│ 25,75,100          │ Aggressive (3 steps)                        │
│ 10,30,50,70,100    │ Balanced (5 steps)                          │
└────────────────────┴──────────────────────────────────────────────┘
```

**Parameter:** `CANARY_WAIT_TIME`  
**Type:** String  
**Default:** `120`  
**Description:** Seconds to wait between traffic steps for monitoring  
**Range:** 60-600 seconds recommended

---

### 🔬 A/B Testing Parameters

**Parameter:** `AB_TRAFFIC_SPLIT`  
**Type:** String  
**Default:** `50`  
**Description:** Traffic percentage for variant B (variant A gets remainder)  
**Range:** 0-100

**Examples:**
```
┌────────┬──────────────┬──────────────┬─────────────────┐
│ Value  │ Variant A    │ Variant B    │ Use Case        │
├────────┼──────────────┼──────────────┼─────────────────┤
│ 50     │ 50%          │ 50%          │ Equal split     │
│ 30     │ 70%          │ 30%          │ Conservative    │
│ 80     │ 20%          │ 80%          │ Aggressive      │
│ 10     │ 90%          │ 10%          │ Small test      │
└────────┴──────────────┴──────────────┴─────────────────┘
```

---

### ⚙️ Pipeline Control Parameters

**Parameter:** `SKIP_TESTS`  
**Type:** Boolean  
**Default:** `false`  
**Description:** Skip pytest execution (NOT recommended for production)

**Parameter:** `SKIP_SONAR`  
**Type:** Boolean  
**Default:** `false`  
**Description:** Skip SonarQube code quality analysis

**Parameter:** `SKIP_SECURITY_SCAN`  
**Type:** Boolean  
**Default:** `false`  
**Description:** Skip Trivy security vulnerability scanning

---

### 🔒 Safety Parameters

**Parameter:** `AUTO_ROLLBACK`  
**Type:** Boolean  
**Default:** `true`  
**Description:** Automatically rollback to previous deployment on failure

**How it works:**
- Saves current deployment image before deploying
- On failure, restores previous image automatically
- Works with all deployment strategies

**Parameter:** `MANUAL_APPROVAL`  
**Type:** Boolean  
**Default:** `false`  
**Description:** Require manual approval before production deployment

**Approval settings:**
- Only applies to production environment
- 30-minute timeout
- Requires `admin` or `deployer` permissions

---

## Common Parameter Combinations

### 🚀 Production Deployment (Safe)
```yaml
DEPLOYMENT_STRATEGY: blue-green
SKIP_TESTS: false
SKIP_SONAR: false
SKIP_SECURITY_SCAN: false
AUTO_ROLLBACK: true
MANUAL_APPROVAL: true
```

### 🎯 Staging Canary (Gradual)
```yaml
DEPLOYMENT_STRATEGY: canary
CANARY_TRAFFIC_STEPS: 10,50,100
CANARY_WAIT_TIME: 120
SKIP_TESTS: false
AUTO_ROLLBACK: true
MANUAL_APPROVAL: false
```

### ⚡ Development (Fast)
```yaml
DEPLOYMENT_STRATEGY: rolling-update
SKIP_TESTS: true
SKIP_SONAR: true
SKIP_SECURITY_SCAN: true
AUTO_ROLLBACK: true
MANUAL_APPROVAL: false
```

### 🔬 A/B Testing (Experimental)
```yaml
DEPLOYMENT_STRATEGY: ab-testing
AB_TRAFFIC_SPLIT: 30
SKIP_TESTS: false
AUTO_ROLLBACK: true
MANUAL_APPROVAL: false
```

### 🧪 Shadow Testing (No Impact)
```yaml
DEPLOYMENT_STRATEGY: shadow
SKIP_TESTS: false
AUTO_ROLLBACK: false  # Not needed (no user traffic)
MANUAL_APPROVAL: false
```

---

## Branch-Based Auto Mode

When `DEPLOYMENT_STRATEGY = auto`, parameters are auto-selected:

```
┌────────────────┬─────────────────┬─────────────┬─────────────────┐
│ Branch         │ Strategy        │ Environment │ Auto Deploy     │
├────────────────┼─────────────────┼─────────────┼─────────────────┤
│ main/master    │ blue-green      │ production  │ ✅ Yes          │
│ develop        │ canary          │ staging     │ ✅ Yes          │
│ release/*      │ canary          │ staging     │ ✅ Yes          │
│ feature/*      │ rolling-update  │ dev         │ ❌ Manual only  │
│ hotfix/*       │ rolling-update  │ production  │ ❌ Manual only  │
│ PR             │ (test only)     │ none        │ ❌ No deploy    │
└────────────────┴─────────────────┴─────────────┴─────────────────┘
```

---

## Parameter Validation

### ✅ Valid Combinations

```yaml
# Canary with custom steps
DEPLOYMENT_STRATEGY: canary
CANARY_TRAFFIC_STEPS: 20,40,60,80,100
CANARY_WAIT_TIME: 180

# A/B with traffic split
DEPLOYMENT_STRATEGY: ab-testing
AB_TRAFFIC_SPLIT: 30

# Blue-Green with approval
DEPLOYMENT_STRATEGY: blue-green
MANUAL_APPROVAL: true
```

### ⚠️ Ignored Parameters

```yaml
# A/B traffic split ignored for non-A/B strategies
DEPLOYMENT_STRATEGY: blue-green
AB_TRAFFIC_SPLIT: 50  # ← Ignored

# Canary parameters ignored for non-canary
DEPLOYMENT_STRATEGY: rolling-update
CANARY_TRAFFIC_STEPS: 10,50,100  # ← Ignored
CANARY_WAIT_TIME: 120  # ← Ignored
```

---

## Environment Variables Set by Pipeline

These are automatically set based on parameters:

```groovy
DEPLOYMENT_STRATEGY_RESOLVED  # Actual strategy after 'auto' resolution
DEPLOY_ENV                    # production, staging, or dev
IMAGE_TAG                     # Docker image tag
SHOULD_DEPLOY                 # Whether auto-deploy enabled
PREVIOUS_DEPLOYMENT           # Saved for rollback
ROLLBACK_AVAILABLE            # Boolean flag
```

---

## Quick Tips

### 💡 Tip 1: Use Auto Mode
```yaml
# Let the pipeline choose based on branch
DEPLOYMENT_STRATEGY: auto
```

### 💡 Tip 2: Safety First for Production
```yaml
# Always enable for main branch
AUTO_ROLLBACK: true
MANUAL_APPROVAL: true
SKIP_TESTS: false
```

### 💡 Tip 3: Speed Up Dev Deployments
```yaml
# For feature branches
DEPLOYMENT_STRATEGY: rolling-update
SKIP_SONAR: true
SKIP_SECURITY_SCAN: true
```

### 💡 Tip 4: Conservative Canary
```yaml
# More gradual steps = more safety
CANARY_TRAFFIC_STEPS: 10,20,30,50,75,100
CANARY_WAIT_TIME: 300  # 5 minutes per step
```

### 💡 Tip 5: Test A/B in Staging First
```yaml
# Develop branch with A/B testing
DEPLOYMENT_STRATEGY: ab-testing
AB_TRAFFIC_SPLIT: 50
```

---

## Parameter Decision Tree

```
┌─ Need to test in production without user impact?
│  └─ YES → DEPLOYMENT_STRATEGY: shadow
│  └─ NO → Continue
│
┌─ Need instant rollback capability?
│  └─ YES → DEPLOYMENT_STRATEGY: blue-green
│  └─ NO → Continue
│
┌─ Need gradual rollout with monitoring?
│  └─ YES → DEPLOYMENT_STRATEGY: canary
│  │         CANARY_TRAFFIC_STEPS: 10,50,100
│  │         CANARY_WAIT_TIME: 120
│  └─ NO → Continue
│
┌─ Need to compare two versions?
│  └─ YES → DEPLOYMENT_STRATEGY: ab-testing
│  │         AB_TRAFFIC_SPLIT: 50
│  └─ NO → Continue
│
└─ Standard deployment
   └─ DEPLOYMENT_STRATEGY: rolling-update
```

---

## Troubleshooting Parameters

### Problem: Deployment too slow
**Solution:**
```yaml
# Reduce wait times
CANARY_WAIT_TIME: 60  # Down from 120

# Use fewer steps
CANARY_TRAFFIC_STEPS: 10,100  # Just 2 steps
```

### Problem: Need to skip quality gates temporarily
**Solution:**
```yaml
# Only for emergency hotfixes
SKIP_TESTS: true
SKIP_SONAR: true
SKIP_SECURITY_SCAN: true
```

### Problem: Production deployment fails and doesn't rollback
**Solution:**
```yaml
# Ensure rollback is enabled
AUTO_ROLLBACK: true

# Check previous deployment exists
# First deployment can't rollback
```

### Problem: Manual approval times out
**Solution:**
```yaml
# Approval has 30-minute timeout
# Approve faster or disable for non-prod
MANUAL_APPROVAL: false  # For staging/dev
```

---

## Jenkins UI Parameter Display

When you click "Build with Parameters", you'll see:

```
╔═══════════════════════════════════════════════════════════╗
║                 Build Parameters                          ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Deployment Strategy: [auto ▼]                           ║
║    ◯ auto                                                ║
║    ◯ blue-green                                          ║
║    ◯ canary                                              ║
║    ◯ rolling-update                                      ║
║    ◯ shadow                                              ║
║    ◯ ab-testing                                          ║
║                                                           ║
║  ☐ Skip Tests                                            ║
║  ☐ Skip SonarQube                                        ║
║  ☐ Skip Security Scan                                    ║
║                                                           ║
║  Canary Traffic Steps: [10,50,100 ▼]                     ║
║  Canary Wait Time: [120]                                 ║
║                                                           ║
║  AB Traffic Split: [50]                                  ║
║                                                           ║
║  ☑ Auto Rollback                                         ║
║  ☐ Manual Approval                                       ║
║                                                           ║
║                       [Build]  [Cancel]                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Summary Table

| Parameter | Required | Default | Type | Strategies |
|-----------|----------|---------|------|------------|
| `DEPLOYMENT_STRATEGY` | ✅ Yes | `auto` | Choice | All |
| `CANARY_TRAFFIC_STEPS` | ❌ No | `10,50,100` | Choice | Canary only |
| `CANARY_WAIT_TIME` | ❌ No | `120` | String | Canary only |
| `AB_TRAFFIC_SPLIT` | ❌ No | `50` | String | A/B only |
| `SKIP_TESTS` | ❌ No | `false` | Boolean | All |
| `SKIP_SONAR` | ❌ No | `false` | Boolean | All |
| `SKIP_SECURITY_SCAN` | ❌ No | `false` | Boolean | All |
| `AUTO_ROLLBACK` | ❌ No | `true` | Boolean | All |
| `MANUAL_APPROVAL` | ❌ No | `false` | Boolean | All |

---

## Related Documentation

- [DEPLOYMENT-STRATEGIES.md](./DEPLOYMENT-STRATEGIES.md) - Detailed strategy guide
- [Jenkinsfile](./Jenkinsfile) - Pipeline implementation
- [JENKINS-QUICKSTART.md](./JENKINS-QUICKSTART.md) - Setup guide
