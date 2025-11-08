# ACEest Fitness Kubernetes Manifests

Complete Kubernetes deployment manifests for ACEest Fitness & Gym Management System with multiple deployment strategies.

## 📁 Directory Structure

```
kube_manifests/
├── 00-namespace.yaml              # Namespace definition
├── 01-configmap.yaml              # Application configuration
├── 02-secrets.yaml                # Sensitive data (credentials)
├── 03-postgres-statefulset.yaml   # PostgreSQL database
├── 04-hpa.yaml                    # Horizontal Pod Autoscaler
├── 05-resource-quotas.yaml        # Resource limits and quotas
├── 06-network-policies.yaml       # Network security policies
├── 07-ingress.yaml                # Ingress controller configuration
├── deploy.sh                      # Deployment automation script
└── strategies/
    ├── rolling-update/
    │   └── deployment.yaml        # Standard rolling update
    ├── blue-green/
    │   └── deployment.yaml        # Blue-green deployment
    ├── canary/
    │   └── deployment.yaml        # Canary release
    ├── ab-testing/
    │   └── deployment.yaml        # A/B testing deployment
    └── shadow/
        └── deployment.yaml        # Shadow deployment
```

## 🚀 Deployment Strategies

### 1. **Rolling Update** (Default)
Standard Kubernetes rolling update with zero downtime.

**Features:**
- MaxSurge: 1 (one extra pod during update)
- MaxUnavailable: 0 (zero downtime)
- Gradual pod replacement
- Automatic rollback on failure

**Deploy:**
```bash
./deploy.sh rolling-update deploy
```

---

### 2. **Blue-Green Deployment**
Run two identical environments; switch traffic instantly between them.

**Features:**
- Two complete deployments (blue and green)
- Instant traffic switching via service selector
- Easy rollback (switch back to previous)
- Zero downtime

**Deploy:**
```bash
# Deploy both blue and green
./deploy.sh blue-green deploy

# Switch traffic to green
./deploy.sh blue-green switch green

# Rollback to blue
./deploy.sh blue-green switch blue
```

**Manual switch:**
```bash
# Switch to green
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Switch to blue
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

### 3. **Canary Release**
Gradually roll out new version to subset of users while monitoring metrics.

**Features:**
- Stable: 9 replicas (90% traffic)
- Canary: 1 replica (10% traffic)
- Monitor metrics before full rollout
- Easy to increase/decrease canary traffic

**Deploy:**
```bash
./deploy.sh canary deploy
```

**Scale canary traffic:**
```bash
# Increase to 25% (3 canary, 7 stable)
kubectl scale deployment aceest-web-canary --replicas=3 -n aceest-fitness
kubectl scale deployment aceest-web-stable --replicas=7 -n aceest-fitness

# Increase to 50% (5 canary, 5 stable)
kubectl scale deployment aceest-web-canary --replicas=5 -n aceest-fitness
kubectl scale deployment aceest-web-stable --replicas=5 -n aceest-fitness

# Promote canary to stable (update stable image)
kubectl set image deployment/aceest-web-stable \
  aceest-web=dharmalakshmi15/aceest-fitness-gym:canary -n aceest-fitness
kubectl scale deployment aceest-web-canary --replicas=0 -n aceest-fitness
```

---

### 4. **A/B Testing**
Route traffic to different versions based on headers or other criteria.

**Features:**
- Version A and Version B deployments
- Header-based routing (X-Version: B)
- 50/50 traffic split by default
- Requires Nginx Ingress Controller

**Deploy:**
```bash
./deploy.sh ab-testing deploy
```

**Test different versions:**
```bash
# Access Version A (default)
curl http://aceest-fitness.local

# Access Version B (with header)
curl -H "X-Version: B" http://aceest-fitness.local
```

**Update /etc/hosts:**
```bash
echo "127.0.0.1 aceest-fitness.local" | sudo tee -a /etc/hosts
```

---

### 5. **Shadow Deployment**
Mirror production traffic to new version without affecting users.

**Features:**
- Production: Handles real traffic
- Shadow: Receives mirrored traffic (responses discarded)
- Test new version with real production load
- Requires Istio service mesh for traffic mirroring

**Deploy:**
```bash
./deploy.sh shadow deploy
```

**Note:** Full traffic mirroring requires Istio. Without Istio, shadow deployment runs separately for manual testing.

---

## 📋 Prerequisites

### Required
- Kubernetes cluster (v1.24+)
- `kubectl` configured
- Container registry access (DockerHub)
- Minimum 4GB RAM, 2 CPUs

### Optional (for advanced features)
- **Nginx Ingress Controller** (for A/B testing)
- **Istio Service Mesh** (for shadow deployment traffic mirroring)
- **Metrics Server** (for HPA)
- **Cert-Manager** (for TLS certificates)

### Install Nginx Ingress Controller:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### Install Metrics Server:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## 🔧 Configuration

### Update Secrets
Edit `02-secrets.yaml` before deploying:
```yaml
SECRET_KEY: "your-production-secret-key"
POSTGRES_PASSWORD: "your-secure-password"
```

### Update Image
Replace `dharmalakshmi15/aceest-fitness-gym` with your image:
```bash
# Update all deployment files
find strategies/ -name "deployment.yaml" -exec sed -i 's|dharmalakshmi15/aceest-fitness-gym|your-registry/your-image|g' {} +
```

---

## 📝 Deployment Commands

### Deploy Base Infrastructure
```bash
./deploy.sh all deploy
```

### Deploy Specific Strategy
```bash
# Rolling update
./deploy.sh rolling-update deploy

# Blue-green
./deploy.sh blue-green deploy

# Canary
./deploy.sh canary deploy

# A/B testing
./deploy.sh ab-testing deploy

# Shadow
./deploy.sh shadow deploy
```

### Check Status
```bash
./deploy.sh rolling-update status
```

### Delete Deployment
```bash
./deploy.sh rolling-update delete
```

### Delete Everything
```bash
./deploy.sh all delete
```

---

## 🔍 Monitoring & Debugging

### View Pods
```bash
kubectl get pods -n aceest-fitness -o wide
```

### View Logs
```bash
# All pods
kubectl logs -f -l app=aceest-web -n aceest-fitness

# Specific pod
kubectl logs -f <pod-name> -n aceest-fitness
```

### Describe Resources
```bash
kubectl describe deployment aceest-web -n aceest-fitness
kubectl describe pod <pod-name> -n aceest-fitness
```

### Access Application
```bash
# Get service external IP
kubectl get service aceest-web-service -n aceest-fitness

# Port forward for local testing
kubectl port-forward service/aceest-web-service 8080:80 -n aceest-fitness
# Access: http://localhost:8080
```

### Database Access
```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n aceest-fitness -- psql -U aceest_user -d aceest_fitness
```

---

## 🔄 Rollback Procedures

### Rolling Update Rollback
```bash
# View rollout history
kubectl rollout history deployment/aceest-web -n aceest-fitness

# Rollback to previous version
kubectl rollout undo deployment/aceest-web -n aceest-fitness

# Rollback to specific revision
kubectl rollout undo deployment/aceest-web --to-revision=2 -n aceest-fitness
```

### Blue-Green Rollback
```bash
# Simply switch service back to previous version
./deploy.sh blue-green switch blue
```

### Canary Rollback
```bash
# Scale canary to 0, scale stable to full
kubectl scale deployment aceest-web-canary --replicas=0 -n aceest-fitness
kubectl scale deployment aceest-web-stable --replicas=10 -n aceest-fitness
```

---

## 📊 Horizontal Pod Autoscaling

The HPA automatically scales pods based on:
- CPU usage: 70% target
- Memory usage: 80% target
- Min replicas: 3
- Max replicas: 10

**View HPA status:**
```bash
kubectl get hpa -n aceest-fitness
kubectl describe hpa aceest-web-hpa -n aceest-fitness
```

---

## 🔐 Security Features

- **Network Policies**: Restrict pod-to-pod communication
- **Resource Quotas**: Prevent resource exhaustion
- **Secrets**: Encrypted storage of sensitive data
- **RBAC**: Role-based access control (configure separately)
- **Pod Security**: Non-root containers with read-only filesystem

---

## 🎯 Jenkins Integration

For Jenkins pipeline, use the deployment strategy as a parameter:

```groovy
parameters {
    choice(
        name: 'DEPLOYMENT_STRATEGY',
        choices: ['rolling-update', 'blue-green', 'canary', 'ab-testing', 'shadow'],
        description: 'Select deployment strategy'
    )
}

stages {
    stage('Deploy to Kubernetes') {
        steps {
            script {
                sh """
                    cd kube_manifests
                    ./deploy.sh ${params.DEPLOYMENT_STRATEGY} deploy
                """
            }
        }
    }
}
```

---

## 🧪 Testing

### Test Rolling Update
```bash
# Deploy initial version
./deploy.sh rolling-update deploy

# Update image and watch rollout
kubectl set image deployment/aceest-web aceest-web=dharmalakshmi15/aceest-fitness-gym:v2 -n aceest-fitness
kubectl rollout status deployment/aceest-web -n aceest-fitness
```

### Test Blue-Green
```bash
# Deploy and test switching
./deploy.sh blue-green deploy
./deploy.sh blue-green switch green
./deploy.sh blue-green switch blue
```

### Test Canary
```bash
# Deploy and scale canary traffic
./deploy.sh canary deploy
kubectl scale deployment aceest-web-canary --replicas=3 -n aceest-fitness
```

---

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [Istio Service Mesh](https://istio.io/latest/docs/)

---

## 🆘 Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n aceest-fitness
kubectl logs <pod-name> -n aceest-fitness
```

### Database connection issues
```bash
# Check PostgreSQL status
kubectl get statefulset postgres -n aceest-fitness
kubectl logs postgres-0 -n aceest-fitness

# Test connectivity
kubectl exec -it <app-pod> -n aceest-fitness -- nc -zv postgres-service 5432
```

### Image pull errors
```bash
# Check image exists
docker pull dharmalakshmi15/aceest-fitness-gym:latest

# Add image pull secrets if private registry
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n aceest-fitness
```

---

**Status:** ✅ All deployment strategies configured and ready  
**Image:** dharmalakshmi15/aceest-fitness-gym  
**Namespace:** aceest-fitness
