# 🚀 Quick Start Guide - Kubernetes Deployment

## ✅ What's Created

### Base Infrastructure (8 files)
```
00-namespace.yaml           - aceest-fitness namespace
01-configmap.yaml          - Application configuration
02-secrets.yaml            - Database credentials & secrets
03-postgres-statefulset.yaml - PostgreSQL with persistent storage
04-hpa.yaml                - Horizontal Pod Autoscaler (3-10 pods)
05-resource-quotas.yaml    - Resource limits
06-network-policies.yaml   - Network security
07-ingress.yaml            - Ingress controller config
```

### Deployment Strategies (5 strategies)
```
strategies/rolling-update/  - Standard rolling update (zero downtime)
strategies/blue-green/      - Instant traffic switching
strategies/canary/          - Gradual rollout (10% → 100%)
strategies/ab-testing/      - Header-based routing
strategies/shadow/          - Traffic mirroring for testing
```

---

## 🎯 Quick Deploy

### 1. Rolling Update (Recommended for start)
```bash
cd /home/dharmalakshmi15/Projects/bits_pilani-Devops_assignment/kube_manifests
./deploy.sh rolling-update deploy
```

### 2. Blue-Green
```bash
./deploy.sh blue-green deploy
./deploy.sh blue-green switch green    # Switch to green
./deploy.sh blue-green switch blue     # Rollback to blue
```

### 3. Canary
```bash
./deploy.sh canary deploy              # 10% canary, 90% stable
kubectl scale deployment aceest-web-canary --replicas=3 -n aceest-fitness  # 25%
kubectl scale deployment aceest-web-canary --replicas=5 -n aceest-fitness  # 50%
```

### 4. A/B Testing
```bash
./deploy.sh ab-testing deploy
curl http://aceest-fitness.local                    # Version A
curl -H "X-Version: B" http://aceest-fitness.local  # Version B
```

### 5. Shadow
```bash
./deploy.sh shadow deploy  # Production + Shadow (mirrored traffic)
```

---

## 📊 Check Status

```bash
# Overall status
./deploy.sh rolling-update status

# Specific resources
kubectl get all -n aceest-fitness
kubectl get pods -n aceest-fitness -o wide
kubectl get svc -n aceest-fitness
kubectl get hpa -n aceest-fitness
```

---

## 🔄 Rollback

### Rolling Update
```bash
kubectl rollout undo deployment/aceest-web -n aceest-fitness
```

### Blue-Green
```bash
./deploy.sh blue-green switch blue  # Switch back
```

### Canary
```bash
kubectl scale deployment aceest-web-canary --replicas=0 -n aceest-fitness
kubectl scale deployment aceest-web-stable --replicas=10 -n aceest-fitness
```

---

## 🔍 Access Application

```bash
# Get external IP
kubectl get svc aceest-web-service -n aceest-fitness

# Or port-forward locally
kubectl port-forward svc/aceest-web-service 8080:80 -n aceest-fitness
# Access: http://localhost:8080
```

---

## 🧹 Cleanup

```bash
# Delete specific strategy
./deploy.sh rolling-update delete

# Delete everything
./deploy.sh all delete
```

---

## 📝 Jenkins Integration

Use in Jenkinsfile:
```groovy
parameters {
    choice(
        name: 'DEPLOYMENT_STRATEGY',
        choices: ['rolling-update', 'blue-green', 'canary', 'ab-testing', 'shadow'],
        description: 'Deployment strategy'
    )
}

stage('Deploy') {
    sh "./kube_manifests/deploy.sh ${params.DEPLOYMENT_STRATEGY} deploy"
}
```

---

## ⚙️ Configuration

### Before deploying:

1. **Update secrets** in `02-secrets.yaml`:
   ```yaml
   SECRET_KEY: "your-production-key"
   POSTGRES_PASSWORD: "secure-password"
   ```

2. **Update image** if needed:
   ```bash
   # Current: dharmalakshmi15/aceest-fitness-gym
   # Change to your registry/image
   ```

3. **Update ingress host** in strategy files:
   ```yaml
   host: aceest-fitness.local  # Change to your domain
   ```

---

## 🎯 Strategy Selection Guide

| Strategy | Use Case | Complexity | Rollback |
|----------|----------|------------|----------|
| **Rolling Update** | Standard deployments | ⭐ Low | Automatic |
| **Blue-Green** | Zero-risk deployments | ⭐⭐ Medium | Instant |
| **Canary** | Gradual feature rollout | ⭐⭐⭐ High | Manual |
| **A/B Testing** | Feature comparison | ⭐⭐⭐ High | Manual |
| **Shadow** | Production testing | ⭐⭐⭐⭐ Very High | N/A |

---

**Image:** dharmalakshmi15/aceest-fitness-gym  
**Namespace:** aceest-fitness  
**Status:** ✅ Ready to deploy
