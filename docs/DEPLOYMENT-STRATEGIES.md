# Deployment Strategies Guide

## Overview

This Jenkins pipeline supports **parameterized deployment strategies** with automatic rollback capabilities. Choose the optimal deployment strategy based on your risk tolerance, traffic requirements, and testing needs.

## Available Strategies

### 1. 🔵🟢 Blue-Green Deployment

**Best for:** Zero-downtime production deployments with instant rollback capability

**How it works:**
- Maintains two identical production environments (blue and green)
- Deploy new version to inactive environment
- Test the new environment thoroughly
- Switch traffic instantly from old to new
- Keep old environment for instant rollback

**Advantages:**
- ✅ Zero downtime
- ✅ Instant rollback (just switch back)
- ✅ Full testing before traffic switch
- ✅ Easy to understand and implement

**Disadvantages:**
- ❌ Requires 2x infrastructure
- ❌ Database migrations can be complex
- ❌ Not suitable for stateful applications

**Pipeline Configuration:**
```groovy
DEPLOYMENT_STRATEGY = 'blue-green'
```

**Usage:**
```bash
# In Jenkins, select:
Deployment Strategy: blue-green

# Or use auto mode for main branch (default):
Deployment Strategy: auto  # main → blue-green
```

**Rollback:**
```bash
# Automatic in pipeline, or manual:
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"color":"blue"}}}'
```

---

### 2. 🕯️ Canary Deployment

**Best for:** Gradual rollout with risk mitigation and real-user testing

**How it works:**
- Deploy new version alongside current version
- Gradually shift traffic using replica scaling: 10% → 50% → 100%
- Monitor metrics at each step
- Automatic rollback if health checks fail
- Wait time between steps for monitoring

**Implementation:** Uses native Kubernetes replica scaling (no Istio required)
- Traffic distribution is approximate based on pod count
- For precise percentage-based traffic control, install Istio service mesh

**Advantages:**
- ✅ Gradual risk exposure
- ✅ Real-user testing with small subset
- ✅ Monitor metrics before full rollout
- ✅ Easy to abort if issues detected
- ✅ No service mesh dependency

**Disadvantages:**
- ❌ Slower rollout process
- ❌ Requires monitoring infrastructure
- ❌ Traffic split is approximate (not exact percentages)

**Pipeline Configuration:**
```groovy
DEPLOYMENT_STRATEGY = 'canary'
CANARY_TRAFFIC_STEPS = '10,50,100'      // Traffic percentages (approximate)
CANARY_WAIT_TIME = '120'                 // Seconds between steps
```

**Traffic Step Options:**
- `10,50,100` - Conservative (default)
- `20,40,60,80,100` - Fine-grained
- `25,75,100` - Aggressive
- `10,30,50,70,100` - Balanced

**Usage:**
```bash
# Jenkins parameters:
Deployment Strategy: canary
Canary Traffic Steps: 10,50,100
Canary Wait Time: 120
```

**Monitoring During Canary:**
```bash
# Watch canary pods
kubectl get pods -n aceest-fitness -l version=canary -w

# Check canary logs
kubectl logs -n aceest-fitness -l version=canary --tail=100 -f

# View traffic distribution
kubectl get virtualservice aceest-web-vs -n aceest-fitness -o yaml
```

---

### 3. 🔄 Rolling Update

**Best for:** Standard deployments with minimal complexity

**How it works:**
- Default Kubernetes deployment strategy
- Replace pods gradually (maxSurge: 1, maxUnavailable: 0)
- Automatic rollback on readiness probe failure
- Maintains 10 revision history

**Advantages:**
- ✅ Simple and reliable
- ✅ Built into Kubernetes
- ✅ No extra infrastructure
- ✅ Automatic health checking

**Disadvantages:**
- ❌ No traffic control
- ❌ All users see new version eventually
- ❌ Rollback takes time

**Pipeline Configuration:**
```groovy
DEPLOYMENT_STRATEGY = 'rolling-update'
```

**Usage:**
```bash
# Jenkins parameters:
Deployment Strategy: rolling-update
```

**Manual Rollback:**
```bash
# Rollback to previous version
kubectl rollout undo deployment/aceest-web -n aceest-fitness

# Rollback to specific revision
kubectl rollout undo deployment/aceest-web -n aceest-fitness --to-revision=3

# Check rollout history
kubectl rollout history deployment/aceest-web -n aceest-fitness
```

---

### 4. 👤 Shadow Deployment

**Best for:** Testing new version in parallel for manual comparison (Simplified implementation)

**How it works:**
- Deploy new version alongside production
- Shadow runs independently without receiving traffic
- Access shadow via port-forward for manual testing
- Compare behavior and performance manually
- No user impact

**Implementation:** Simplified (no traffic mirroring)
- Shadow deployment runs separately for testing
- Production receives all user traffic
- For automatic traffic mirroring, install Istio service mesh

**Advantages:**
- ✅ Zero user impact
- ✅ No service mesh dependency
- ✅ Simple to set up
- ✅ Good for load testing and manual validation

**Disadvantages:**
- ❌ Requires 2x infrastructure
- ❌ No automatic traffic mirroring (without Istio)
- ❌ Manual testing required
- ❌ Side effects (DB writes) need handling

**Pipeline Configuration:**
```groovy
DEPLOYMENT_STRATEGY = 'shadow'
```

**Requirements:**
- None (native Kubernetes)
- Optional: Istio for automatic traffic mirroring

**Usage:**
```bash
# Jenkins parameters:
Deployment Strategy: shadow

# Access shadow for testing:
kubectl port-forward deployment/aceest-web-shadow 8080:5000 -n aceest-fitness
# Then test at http://localhost:8080
```

**Monitoring Shadow:**
```bash
# Compare shadow vs production logs
kubectl logs -n aceest-fitness -l version=shadow --tail=100 -f
kubectl logs -n aceest-fitness -l version=production --tail=100 -f

# Check shadow performance
kubectl top pods -n aceest-fitness -l version=shadow
```

---

### 5. 🔬 A/B Testing

**Best for:** Comparing two versions to measure user behavior and conversions

**How it works:**
- Deploy variant A (current) and variant B (new)
- Split traffic using replica counts (approximate distribution)
- Both variants share the same service for load balancing
- Measure KPIs and conversion metrics
- Choose winner based on data

**Implementation:** Uses native Kubernetes replica scaling
- Traffic distribution is approximate based on pod count
- For precise percentage control and header-based routing, install Istio

**Advantages:**
- ✅ Data-driven decisions
- ✅ Measure business impact
- ✅ Compare features side-by-side
- ✅ No service mesh dependency

**Disadvantages:**
- ❌ Requires analytics infrastructure
- ❌ Takes time to gather data
- ❌ Traffic split is approximate (not exact)
- ❌ Need significant traffic for meaningful results

**Pipeline Configuration:**
```groovy
DEPLOYMENT_STRATEGY = 'ab-testing'
AB_TRAFFIC_SPLIT = '50'  // Percentage for variant B (0-100, approximate)
```

**Usage:**
```bash
# Jenkins parameters:
Deployment Strategy: ab-testing
AB Traffic Split: 50  # 50% to variant B, 50% to variant A
```

**Force Specific Variant:**
```bash
# Force variant B with header
curl -H "x-variant: B" http://your-app-url

# Variant A gets remaining traffic
curl http://your-app-url  # May get A or B based on split
```

---

## Pipeline Parameters

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `DEPLOYMENT_STRATEGY` | Choice | `auto` | Deployment strategy selection |
| `SKIP_TESTS` | Boolean | `false` | Skip test execution |
| `SKIP_SONAR` | Boolean | `false` | Skip SonarQube analysis |
| `SKIP_SECURITY_SCAN` | Boolean | `false` | Skip Trivy security scan |
| `AUTO_ROLLBACK` | Boolean | `true` | Auto rollback on failure |
| `MANUAL_APPROVAL` | Boolean | `false` | Require manual approval for production |

### Strategy-Specific Parameters

| Parameter | Applies To | Default | Description |
|-----------|------------|---------|-------------|
| `CANARY_TRAFFIC_STEPS` | Canary | `10,50,100` | Traffic shift percentages |
| `CANARY_WAIT_TIME` | Canary | `120` | Seconds between steps |
| `AB_TRAFFIC_SPLIT` | A/B Testing | `50` | Percentage for variant B |

---

## Auto Mode (Branch-Based)

When `DEPLOYMENT_STRATEGY = 'auto'`, the pipeline automatically selects the strategy based on branch:

| Branch Pattern | Auto Strategy | Environment | Rationale |
|---------------|---------------|-------------|-----------|
| `main`, `master` | Blue-Green | Production | Zero-downtime, instant rollback |
| `develop` | Canary | Staging | Gradual rollout, risk mitigation |
| `release/*` | Canary | Staging | Pre-production validation |
| `feature/*` | Rolling Update | Dev | Simple, no extra infrastructure |
| `hotfix/*` | Rolling Update | Production | Fast deployment for urgent fixes |

**Example:**
```bash
# On main branch
DEPLOYMENT_STRATEGY = 'auto' → Blue-Green to Production

# On develop branch  
DEPLOYMENT_STRATEGY = 'auto' → Canary to Staging

# On feature/new-login branch
DEPLOYMENT_STRATEGY = 'auto' → Rolling Update to Dev
```

---

## Rollback Capabilities

### Automatic Rollback

Enabled by default with `AUTO_ROLLBACK = true`:

- Triggers on deployment failure
- Saves pre-deployment state automatically
- Restores previous image version
- Works with all strategies

**Pipeline Stage:**
```groovy
stage('Save Pre-Deployment State') {
    // Captures current deployment image
    // Stored in PREVIOUS_DEPLOYMENT variable
}

post {
    failure {
        // Automatic rollback if AUTO_ROLLBACK enabled
        kubectl set image deployment/aceest-web ...
    }
}
```

### Manual Rollback

#### Blue-Green
```bash
# Switch back to previous color
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"color":"blue"}}}'
```

#### Canary
```bash
# Set canary traffic to 0%
kubectl patch virtualservice aceest-web-vs -n aceest-fitness --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "aceest-web-stable"}, "weight": 100},
        {"destination": {"host": "aceest-web-canary"}, "weight": 0}
      ]
    }]
  }
}'

# Delete canary deployment
kubectl delete deployment aceest-web-canary -n aceest-fitness
```

#### Rolling Update
```bash
# Rollback to previous revision
kubectl rollout undo deployment/aceest-web -n aceest-fitness

# Rollback to specific revision
kubectl rollout undo deployment/aceest-web -n aceest-fitness --to-revision=5

# Check history
kubectl rollout history deployment/aceest-web -n aceest-fitness
```

#### Shadow
```bash
# Simply delete shadow deployment (no user impact)
kubectl delete deployment aceest-web-shadow -n aceest-fitness
```

#### A/B Testing
```bash
# Shift all traffic to variant A
kubectl patch virtualservice aceest-web-ab-test -n aceest-fitness --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "aceest-web-variant-a"}, "weight": 100},
        {"destination": {"host": "aceest-web-variant-b"}, "weight": 0}
      ]
    }]
  }
}'
```

---

## Best Practices

### 1. Choose the Right Strategy

| Scenario | Recommended Strategy |
|----------|---------------------|
| Production release with zero downtime | Blue-Green |
| Gradual rollout with risk mitigation | Canary |
| Standard development deployment | Rolling Update |
| Performance testing with production traffic | Shadow |
| Feature comparison and user testing | A/B Testing |

### 2. Enable Safety Features

```bash
# Always use for production
AUTO_ROLLBACK = true
MANUAL_APPROVAL = true  # For production deployments
```

### 3. Monitor Deployments

```bash
# Watch deployment progress
kubectl rollout status deployment/aceest-web -n aceest-fitness

# Monitor pod health
kubectl get pods -n aceest-fitness -w

# Check logs
kubectl logs -n aceest-fitness -l app=aceest-web --tail=100 -f
```

### 4. Test Strategies in Non-Production

- Use `develop` branch to test canary deployments
- Use `feature/*` branches for rolling updates
- Validate rollback procedures regularly

---

## Troubleshooting

### Deployment Stuck

```bash
# Check deployment status
kubectl describe deployment aceest-web -n aceest-fitness

# Check pod events
kubectl get events -n aceest-fitness --sort-by='.lastTimestamp'

# Force rollback
kubectl rollout undo deployment/aceest-web -n aceest-fitness
```

### Health Check Failures

```bash
# Check liveness/readiness probes
kubectl describe pod <pod-name> -n aceest-fitness

# Test health endpoint manually
kubectl exec <pod-name> -n aceest-fitness -- curl -f http://localhost:5000/health
```

### Traffic Not Switching (Blue-Green/Canary)

```bash
# Verify service selector
kubectl get service aceest-web-service -n aceest-fitness -o yaml

# Check Istio VirtualService (if using)
kubectl get virtualservice -n aceest-fitness
kubectl describe virtualservice aceest-web-vs -n aceest-fitness
```

---

## Examples

### Example 1: Production Deployment with Blue-Green

```bash
# Jenkins parameters:
Branch: main
Deployment Strategy: auto (or blue-green)
Manual Approval: true
Auto Rollback: true
Skip Tests: false
```

Pipeline will:
1. Run tests and SonarQube
2. Build and scan Docker image
3. Wait for manual approval
4. Save current deployment state
5. Deploy to green environment
6. Test green environment
7. Switch traffic to green
8. Keep blue for rollback

### Example 2: Gradual Rollout with Canary

```bash
# Jenkins parameters:
Branch: develop
Deployment Strategy: canary
Canary Traffic Steps: 10,30,50,100
Canary Wait Time: 180
Auto Rollback: true
```

Pipeline will:
1. Deploy canary alongside stable
2. Shift 10% traffic → wait 3 minutes
3. Shift 30% traffic → wait 3 minutes
4. Shift 50% traffic → wait 3 minutes
5. Shift 100% traffic
6. Rollback automatically if health checks fail

### Example 3: Feature Testing with A/B

```bash
# Jenkins parameters:
Branch: feature/new-ui
Deployment Strategy: ab-testing
AB Traffic Split: 30
Auto Rollback: true
```

Pipeline will:
1. Deploy variant A (current) and B (new)
2. Split traffic 70% A / 30% B
3. Monitor metrics and user behavior
4. Use header routing for consistency

---

## Summary

| Strategy | Risk | Speed | Complexity | Infrastructure | Best Use Case |
|----------|------|-------|------------|----------------|---------------|
| Blue-Green | Low | Fast | Medium | 2x | Production releases |
| Canary | Very Low | Slow | High | 1.1x | Risk-averse rollouts |
| Rolling Update | Medium | Medium | Low | 1x | Standard deployments |
| Shadow | None | N/A | High | 2x | Performance testing |
| A/B Testing | Low | Slow | High | 2x | Feature comparison |

**Quick Decision Tree:**

1. **Need zero user impact?** → Shadow
2. **Need instant rollback?** → Blue-Green
3. **Need gradual rollout?** → Canary
4. **Need to compare features?** → A/B Testing
5. **Simple standard deployment?** → Rolling Update

---

## Additional Resources

- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Istio Traffic Management](https://istio.io/latest/docs/concepts/traffic-management/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Blue-Green Deployment Guide](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary Releases](https://martinfowler.com/bliki/CanaryRelease.html)
