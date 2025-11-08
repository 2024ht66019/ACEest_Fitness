# Jenkins CI/CD Pipeline - Quick Reference

## 🚀 Quick Start

### 1. Run Pipeline with Default Settings
```
Strategy: rolling-update
Environment: dev
Image Tag: latest
All checks: ✅ Enabled
```

### 2. Production Deployment
```
Strategy: blue-green or canary
Environment: production
Image Tag: v1.2.3
All checks: ✅ Enabled
```

---

## 📋 Required Jenkins Credentials

| Credential ID | Type | Description |
|--------------|------|-------------|
| `dockerhub-credentials` | Username + Password | Docker Hub push access |
| `kubeconfig-aks` | Secret File | AKS cluster kubeconfig |
| `sonarqube-token` | Secret Text | SonarQube authentication |

---

## 🎯 Pipeline Stages (Summary)

| # | Stage | Duration | Condition |
|---|-------|----------|-----------|
| 1 | Checkout | ~10s | Always |
| 2 | Setup Environment | ~60s | Always |
| 3 | Run Tests | ~3m | RUN_TESTS |
| 4 | SonarQube Analysis | ~2m | RUN_SONARQUBE |
| 5 | Quality Gate | ~60s | RUN_SONARQUBE |
| 6 | Build Docker | ~5m | !SKIP_BUILD |
| 7 | Security Scan | ~3m | !SKIP_BUILD |
| 8 | Push to Docker Hub | ~3m | !SKIP_BUILD |
| 9 | Deploy to AKS | ~5m | DEPLOY_TO_AKS |
| 10 | Verify Deployment | ~3m | DEPLOY_TO_AKS |
| 11 | Health Check | ~60s | DEPLOY_TO_AKS |
| 12 | Smoke Tests | ~30s | DEPLOY_TO_AKS |

**Total Duration**: ~15-25 minutes (full pipeline)

---

## ⚙️ Common Parameter Combinations

### Development Testing
```
DEPLOYMENT_STRATEGY: rolling-update
ENVIRONMENT: dev
IMAGE_TAG: latest
RUN_TESTS: ✅
RUN_SONARQUBE: ✅
DEPLOY_TO_AKS: ✅
SKIP_BUILD: ❌
```

### Staging Release
```
DEPLOYMENT_STRATEGY: canary
ENVIRONMENT: staging
IMAGE_TAG: v1.2.3-rc1
RUN_TESTS: ✅
RUN_SONARQUBE: ✅
DEPLOY_TO_AKS: ✅
SKIP_BUILD: ❌
```

### Production Release
```
DEPLOYMENT_STRATEGY: blue-green
ENVIRONMENT: production
IMAGE_TAG: v1.2.3
RUN_TESTS: ✅
RUN_SONARQUBE: ✅
DEPLOY_TO_AKS: ✅
SKIP_BUILD: ❌
```

### Hotfix (Skip Tests - Emergency Only)
```
DEPLOYMENT_STRATEGY: rolling-update
ENVIRONMENT: production
IMAGE_TAG: v1.2.4-hotfix
RUN_TESTS: ❌
RUN_SONARQUBE: ❌
DEPLOY_TO_AKS: ✅
SKIP_BUILD: ❌
```

### Redeploy Existing Image
```
DEPLOYMENT_STRATEGY: rolling-update
ENVIRONMENT: production
IMAGE_TAG: v1.2.3
RUN_TESTS: ❌
RUN_SONARQUBE: ❌
DEPLOY_TO_AKS: ✅
SKIP_BUILD: ✅ (Use existing image)
```

---

## 🔧 Common kubectl Commands

### Check Deployment Status
```bash
export KUBECONFIG=/path/to/kubeconfig-aks.yaml

# Get pods
kubectl get pods -n aceest-fitness

# Get deployments
kubectl get deployments -n aceest-fitness

# Get services
kubectl get services -n aceest-fitness

# Get ingress
kubectl get ingress -n aceest-fitness
```

### View Logs
```bash
# Application logs
kubectl logs -l app=aceest-web -n aceest-fitness --tail=100

# PostgreSQL logs
kubectl logs postgres-0 -n aceest-fitness --tail=50

# Follow logs
kubectl logs -f deployment/aceest-web -n aceest-fitness
```

### Rollback Deployment
```bash
# View rollout history
kubectl rollout history deployment/aceest-web -n aceest-fitness

# Rollback to previous version
kubectl rollout undo deployment/aceest-web -n aceest-fitness

# Rollback to specific revision
kubectl rollout undo deployment/aceest-web -n aceest-fitness --to-revision=2
```

---

## 🐳 Docker Commands

### Manual Build & Push
```bash
# Build
docker build -t dharmalakshmi15/aceest-fitness-gym:v1.2.3 .

# Test locally
docker run -p 5000:5000 dharmalakshmi15/aceest-fitness-gym:v1.2.3

# Push
docker login
docker push dharmalakshmi15/aceest-fitness-gym:v1.2.3
```

### Check Existing Images
```bash
# List images on Docker Hub
curl -s https://hub.docker.com/v2/repositories/dharmalakshmi15/aceest-fitness-gym/tags | jq -r '.results[].name'

# List local images
docker images dharmalakshmi15/aceest-fitness-gym
```

---

## 🧪 Run Tests Locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::TestAuthentication::test_successful_login -v
```

---

## 📊 SonarQube

### View Results
```
URL: http://your-sonarqube:9000/dashboard?id=aceest-fitness-gym
```

### Quality Gate Criteria
- Code Coverage: ≥70%
- Bugs: 0
- Vulnerabilities: 0
- Code Smells: <50
- Duplications: <3%

---

## 🔒 Security Scan Results

### View Trivy Report
```bash
# Download from Jenkins artifacts
# Or run locally:
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image dharmalakshmi15/aceest-fitness-gym:latest
```

---

## 🚨 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Tests fail | Run `pytest -v` locally, fix issues |
| Quality gate fails | Check SonarQube dashboard |
| Docker push fails | Verify credentials: `dockerhub-credentials` |
| Deployment fails | Check `kubectl get pods -n aceest-fitness` |
| Pods not ready | Check logs: `kubectl logs <pod> -n aceest-fitness` |
| Health check fails | Port-forward and test: `kubectl port-forward svc/aceest-web-service 8080:5000 -n aceest-fitness` |

---

## 📞 Getting Help

1. **Check Jenkins console output** for detailed error messages
2. **Review logs**: Application pods, PostgreSQL, Ingress
3. **Verify credentials** are correct and not expired
4. **Check AKS cluster** health and node resources
5. **Consult full documentation**: `JENKINS-PIPELINE.md`

---

## 🎯 Best Practices

✅ **Always test in dev first**  
✅ **Use semantic versioning** (v1.2.3)  
✅ **Never skip tests in production**  
✅ **Monitor deployments** for 15+ minutes  
✅ **Have rollback plan ready**  
✅ **Review security scan results**  
✅ **Keep credentials rotated** (90 days)  

---

**Pipeline Version**: 1.0.0  
**Quick Reference Guide**
