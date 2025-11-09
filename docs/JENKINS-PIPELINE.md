# Jenkins CI/CD Pipeline Documentation
# ACEest Fitness Gym Management Application

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Jenkins Setup](#jenkins-setup)
4. [Credentials Configuration](#credentials-configuration)
5. [Pipeline Parameters](#pipeline-parameters)
6. [Pipeline Stages](#pipeline-stages)
7. [Usage Guide](#usage-guide)
8. [Deployment Strategies](#deployment-strategies)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## 🎯 Overview

This Jenkins pipeline provides a complete CI/CD workflow for the ACEest Fitness application with:

- ✅ **Automated Testing**: Pytest-based unit, integration, and API tests
- ✅ **Code Quality**: SonarQube static code analysis with quality gates
- ✅ **Security Scanning**: Docker image vulnerability scanning with Trivy
- ✅ **Containerization**: Docker build and push to Docker Hub
- ✅ **Deployment**: Multiple Kubernetes deployment strategies for AKS
- ✅ **Validation**: Health checks and smoke tests
- ✅ **Notifications**: Build status notifications

---

## 🔧 Prerequisites

### Jenkins Version
- Jenkins 2.375+ (LTS recommended)
- Java 11 or 17

### Required Jenkins Plugins

Install the following plugins via **Manage Jenkins → Manage Plugins**:

```
# Core plugins
- Pipeline (workflow-aggregator)
- Docker Pipeline (docker-workflow)
- Kubernetes CLI (kubernetes-cli)
- Git (git)
- Credentials Binding (credentials-binding)

# Testing and Quality
- JUnit (junit)
- HTML Publisher (htmlpublisher)
- SonarQube Scanner (sonar)

# Utilities
- Pipeline Utility Steps (pipeline-utility-steps)
- Timestamper (timestamper)
- AnsiColor (ansicolor)
- Workspace Cleanup (ws-cleanup)

# Notifications (optional)
- Email Extension (email-ext)
- Slack Notification (slack)
```

### System Requirements

**Jenkins Agent/Node:**
- Python 3.13+
- Docker 20.10+
- kubectl 1.28+
- SonarQube Scanner CLI
- Trivy (installed automatically by pipeline)
- Git

**Install on Jenkins agent:**
```bash
# Python and pip
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# SonarQube Scanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip
sudo mv sonar-scanner-5.0.1.3006-linux /opt/sonar-scanner
sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
```

---

## 🚀 Jenkins Setup

### 1. Create Jenkins Pipeline Job

1. **Navigate to Jenkins Dashboard**
2. Click **New Item**
3. Enter job name: `aceest-fitness-cicd`
4. Select **Pipeline**
5. Click **OK**

### 2. Configure Pipeline

**General Settings:**
- ✅ Enable **Discard old builds** (Keep last 10 builds)
- ✅ Enable **This project is parameterized** (parameters defined in Jenkinsfile)
- ✅ Enable **GitHub project** (optional: add repository URL)

**Pipeline Configuration:**
- **Definition**: `Pipeline script from SCM`
- **SCM**: `Git`
- **Repository URL**: `https://github.com/your-username/aceest-fitness.git`
- **Credentials**: Select GitHub credentials
- **Branch**: `*/main` (or your default branch)
- **Script Path**: `Jenkinsfile`

### 3. Configure SonarQube

**Add SonarQube Server:**

1. Go to **Manage Jenkins → Configure System**
2. Scroll to **SonarQube servers**
3. Click **Add SonarQube**
   - **Name**: `SonarQube`
   - **Server URL**: `http://your-sonarqube-server:9000`
   - **Server authentication token**: Select credential (see below)

---

## 🔐 Credentials Configuration

Configure these credentials in **Manage Jenkins → Manage Credentials → (global)**:

### 1. Docker Hub Credentials

**Type**: Username with password
- **ID**: `dockerhub-credentials`
- **Username**: Your Docker Hub username (e.g., `dharmalakshmi15`)
- **Password**: Docker Hub access token or password
- **Description**: Docker Hub credentials for image push

**Create Docker Hub Access Token:**
```
1. Login to hub.docker.com
2. Account Settings → Security → New Access Token
3. Name: jenkins-ci
4. Permissions: Read, Write, Delete
5. Copy the token
```

### 2. AKS Kubeconfig

**Type**: Secret file
- **ID**: `kubeconfig-aks`
- **File**: Upload your AKS kubeconfig file
- **Description**: AKS cluster kubeconfig for deployment

**Get AKS Kubeconfig:**
```bash
# Get credentials from Azure
az aks get-credentials \
  --resource-group <your-resource-group> \
  --name <your-aks-cluster> \
  --file kubeconfig-aks.yaml

# Verify it works
KUBECONFIG=kubeconfig-aks.yaml kubectl get nodes

# Upload this file to Jenkins credentials
```

### 3. SonarQube Token

**Type**: Secret text
- **ID**: `sonarqube-token`
- **Secret**: Your SonarQube authentication token
- **Description**: SonarQube authentication token

**Generate SonarQube Token:**
```
1. Login to SonarQube
2. My Account → Security → Generate Token
3. Name: jenkins-ci
4. Type: Global Analysis Token
5. Copy the token
```

### 4. GitHub Token (Optional)

**Type**: Secret text
- **ID**: `github-token`
- **Secret**: GitHub personal access token
- **Description**: GitHub token for status updates

---

## 🎛️ Pipeline Parameters

The pipeline supports the following parameters:

### DEPLOYMENT_STRATEGY
**Type**: Choice
**Values**: 
- `rolling-update` (default) - Zero-downtime gradual rollout
- `blue-green` - Instant switch between environments
- `canary` - Gradual traffic shift (90/10 split)
- `ab-testing` - Header-based routing for A/B tests
- `shadow` - Mirror traffic to test environment

**Description**: Kubernetes deployment strategy

### ENVIRONMENT
**Type**: Choice
**Values**: 
- `dev` - Development environment
- `staging` - Staging/QA environment
- `production` - Production environment

**Description**: Target deployment environment

### IMAGE_TAG
**Type**: String
**Default**: `latest`
**Examples**: `v1.2.3`, `staging`, `latest`

**Description**: Docker image tag (version)

### RUN_TESTS
**Type**: Boolean
**Default**: `true`

**Description**: Execute Pytest test suite (recommended)

### RUN_SONARQUBE
**Type**: Boolean
**Default**: `true`

**Description**: Run SonarQube code analysis

### DEPLOY_TO_AKS
**Type**: Boolean
**Default**: `true`

**Description**: Deploy to AKS cluster

### SKIP_BUILD
**Type**: Boolean
**Default**: `false`

**Description**: Skip Docker build and use existing image

---

## 📊 Pipeline Stages

### Stage 1: Checkout
**Duration**: ~5-10 seconds
**Actions**:
- Checkout source code from Git
- Extract commit metadata (branch, author, message)
- Display build information

**Failure Impact**: Pipeline fails immediately

---

### Stage 2: Setup Environment
**Duration**: ~30-60 seconds
**Actions**:
- Verify Python and pip versions
- Create Python virtual environment
- Install application dependencies from `requirements.txt`

**Failure Impact**: Pipeline fails, cannot proceed without dependencies

---

### Stage 3: Run Tests
**Duration**: ~2-5 minutes
**Condition**: `RUN_TESTS == true`

**Actions**:
- Install test dependencies (`requirements-test.txt`)
- Execute Pytest test suite (unit, integration, API tests)
- Generate coverage reports (HTML, XML, terminal)
- Enforce 70% code coverage threshold

**Outputs**:
- JUnit test results: `test-results/pytest-results.xml`
- Coverage HTML report: `htmlcov/index.html`
- Coverage XML: `coverage.xml`

**Failure Impact**: Pipeline fails if tests fail or coverage < 70%

**Skip Conditions**: `RUN_TESTS == false`

---

### Stage 4: SonarQube Analysis
**Duration**: ~1-3 minutes
**Condition**: `RUN_SONARQUBE == true`

**Actions**:
- Upload code to SonarQube for static analysis
- Analyze code quality, bugs, vulnerabilities, code smells
- Generate quality metrics

**Failure Impact**: Continues to Quality Gate stage

---

### Stage 5: Quality Gate
**Duration**: ~30-60 seconds
**Condition**: `RUN_SONARQUBE == true`

**Actions**:
- Wait for SonarQube analysis completion
- Check quality gate status (OK/ERROR)
- Enforce quality standards

**Failure Impact**: Pipeline fails if quality gate is not OK

**Quality Gate Criteria** (configurable in SonarQube):
- Coverage >= 70%
- Code Smells < 50
- Bugs: 0
- Vulnerabilities: 0
- Security Hotspots reviewed

---

### Stage 6: Build Docker Image
**Duration**: ~3-7 minutes
**Condition**: `SKIP_BUILD == false`

**Actions**:
- Build Docker image using multi-stage Dockerfile
- Tag with multiple tags:
  - `<version>-<build_number>`
  - `<branch>-<build_number>`
  - `build-<build_number>`
  - `latest` (only for main/master branch)
- Add OCI labels for traceability

**Build Arguments**:
```
BUILD_DATE=<timestamp>
VCS_REF=<git_commit>
VERSION=<build_version>
```

**Failure Impact**: Pipeline fails, no image to deploy

---

### Stage 7: Security Scan
**Duration**: ~2-4 minutes
**Condition**: `SKIP_BUILD == false`

**Actions**:
- Install Trivy scanner (if not present)
- Scan Docker image for vulnerabilities
- Report HIGH and CRITICAL vulnerabilities
- Generate vulnerability report

**Output**: `trivy-report.txt`

**Failure Impact**: Continues (scan failures are warnings)

---

### Stage 8: Push to Docker Hub
**Duration**: ~2-5 minutes
**Condition**: `SKIP_BUILD == false`

**Actions**:
- Authenticate to Docker Hub
- Push all image tags to repository
- Logout from Docker Hub

**Registry**: `docker.io`
**Image**: `dharmalakshmi15/aceest-fitness-gym`

**Failure Impact**: Pipeline fails, deployment cannot proceed

---

### Stage 9: Deploy to AKS
**Duration**: ~3-7 minutes
**Condition**: `DEPLOY_TO_AKS == true`

**Actions**:
1. Verify kubectl connection to AKS
2. Create namespace if not exists
3. Deploy base infrastructure:
   - Namespace
   - ConfigMap
   - Secrets
   - PostgreSQL StatefulSet
   - HPA
   - Resource Quotas
   - Network Policies
   - Ingress
4. Wait for PostgreSQL to be ready
5. Update deployment manifest with new image tag
6. Apply deployment using selected strategy
7. Display deployment status

**Failure Impact**: Pipeline fails, rollback may be needed

---

### Stage 10: Verify Deployment
**Duration**: ~2-5 minutes
**Condition**: `DEPLOY_TO_AKS == true`

**Actions**:
- Wait for pods to reach Ready state (timeout: 5 minutes)
- Display deployment status
- Show pod logs
- Get service endpoints

**Failure Impact**: Pipeline fails if pods don't become ready

---

### Stage 11: Health Check
**Duration**: ~30-90 seconds
**Condition**: `DEPLOY_TO_AKS == true`

**Actions**:
- Get LoadBalancer external IP
- Test `/health` endpoint
- Retry up to 10 times with 15-second intervals
- Verify HTTP 200 response

**Failure Impact**: Pipeline fails, deployment unhealthy

---

### Stage 12: Smoke Tests
**Duration**: ~15-30 seconds
**Condition**: `DEPLOY_TO_AKS == true`

**Actions**:
- Test critical endpoints:
  - `/` (home page)
  - `/health` (health check)
  - `/auth/login` (login page)
  - `/auth/register` (registration page)
- Verify all return HTTP 200

**Failure Impact**: Pipeline fails if any endpoint fails

---

## 💻 Usage Guide

### Running the Pipeline

#### Method 1: Jenkins Web UI

1. Navigate to job: `aceest-fitness-cicd`
2. Click **Build with Parameters**
3. Select parameters:
   - **Deployment Strategy**: `rolling-update`
   - **Environment**: `dev`
   - **Image Tag**: `latest`
   - Check **Run Tests**: ✅
   - Check **Run SonarQube**: ✅
   - Check **Deploy to AKS**: ✅
   - Uncheck **Skip Build**: ❌
4. Click **Build**

#### Method 2: Jenkins CLI

```bash
# Download Jenkins CLI
wget http://jenkins.example.com/jnlpJars/jenkins-cli.jar

# Run pipeline with parameters
java -jar jenkins-cli.jar -s http://jenkins.example.com/ \
  -auth username:token \
  build aceest-fitness-cicd \
  -p DEPLOYMENT_STRATEGY=rolling-update \
  -p ENVIRONMENT=dev \
  -p IMAGE_TAG=latest \
  -p RUN_TESTS=true \
  -p RUN_SONARQUBE=true \
  -p DEPLOY_TO_AKS=true \
  -p SKIP_BUILD=false
```

#### Method 3: Jenkinsfile Trigger (Webhook)

Configure GitHub webhook for automatic builds:

1. **GitHub**: Repository → Settings → Webhooks → Add webhook
   - **Payload URL**: `http://jenkins.example.com/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Push, Pull Request

2. **Jenkins**: Job configuration
   - Enable **GitHub hook trigger for GITScm polling**

---

## 🚀 Deployment Strategies

### 1. Rolling Update (Default)
**Use Case**: Standard production deployments

**How it works**:
- Gradually replaces old pods with new ones
- MaxSurge: 1 (one extra pod during update)
- MaxUnavailable: 0 (no downtime)

**Rollback**:
```bash
kubectl rollout undo deployment/aceest-web -n aceest-fitness
```

### 2. Blue-Green
**Use Case**: Instant switchover, easy rollback

**How it works**:
- Two identical environments (blue and green)
- Update green while blue serves traffic
- Switch service selector to green when ready

**Switch to Green**:
```bash
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"version":"green"}}}'
```

**Rollback to Blue**:
```bash
kubectl patch service aceest-web-service -n aceest-fitness \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

### 3. Canary
**Use Case**: Gradual rollout with risk mitigation

**How it works**:
- Deploy 10% of traffic to new version (canary)
- 90% traffic stays on stable version
- Monitor canary performance
- Gradually increase canary replicas

**Scale Canary**:
```bash
# Increase canary to 50%
kubectl scale deployment aceest-web-canary -n aceest-fitness --replicas=5
kubectl scale deployment aceest-web-stable -n aceest-fitness --replicas=5
```

**Rollback**:
```bash
kubectl scale deployment aceest-web-canary -n aceest-fitness --replicas=0
```

### 4. A/B Testing
**Use Case**: Feature testing with specific user groups

**How it works**:
- Route traffic based on HTTP headers
- Header `X-Version: b` routes to version B
- No header routes to version A

**Test Version B**:
```bash
curl -H "X-Version: b" http://your-domain.com
```

**Rollback**:
```bash
# Scale down version B
kubectl scale deployment aceest-web-version-b -n aceest-fitness --replicas=0
```

### 5. Shadow
**Use Case**: Testing in production without user impact

**How it works**:
- Production handles real traffic
- Shadow deployment receives mirrored traffic (read-only)
- Responses are discarded
- Used for performance testing

**Requires**: Istio service mesh or compatible ingress

---

## 🐛 Troubleshooting

### Issue: Tests Fail

**Symptom**: Stage "Run Tests" fails

**Solutions**:
```bash
# Check test output
cat test-results/pytest-results.xml

# Run tests locally
python -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt
pytest -v

# Fix failing tests, commit, and rerun pipeline
```

---

### Issue: Quality Gate Fails

**Symptom**: SonarQube quality gate fails

**Solutions**:
1. Check SonarQube dashboard for issues
2. Fix code quality issues:
   - Reduce code complexity
   - Fix security vulnerabilities
   - Increase test coverage
3. Temporarily adjust quality gate thresholds (not recommended for production)

---

### Issue: Docker Build Fails

**Symptom**: Stage "Build Docker Image" fails

**Solutions**:
```bash
# Check Docker daemon
docker info

# Test Dockerfile locally
docker build -t test-image .

# Check disk space
df -h

# Clean up Docker
docker system prune -a --volumes
```

---

### Issue: Docker Push Fails

**Symptom**: Authentication or push errors

**Solutions**:
```bash
# Verify Docker Hub credentials
docker login -u dharmalakshmi15

# Check credential in Jenkins
# Manage Jenkins → Credentials → dockerhub-credentials

# Recreate credential with correct token

# Check Docker Hub rate limits
# Free tier: 100 pulls/6 hours
```

---

### Issue: Deployment Fails

**Symptom**: kubectl commands fail

**Solutions**:
```bash
# Verify kubeconfig
export KUBECONFIG=/path/to/kubeconfig-aks.yaml
kubectl cluster-info

# Check AKS connectivity
az aks get-credentials --resource-group <rg> --name <cluster>

# Verify namespace exists
kubectl get namespace aceest-fitness

# Check pod status
kubectl get pods -n aceest-fitness
kubectl describe pod <pod-name> -n aceest-fitness

# Check events
kubectl get events -n aceest-fitness --sort-by='.lastTimestamp'
```

---

### Issue: Pods Not Ready

**Symptom**: Pods stuck in Pending, CrashLoopBackOff, or ImagePullBackOff

**Solutions**:

**ImagePullBackOff**:
```bash
# Check if image exists in Docker Hub
curl https://hub.docker.com/v2/repositories/dharmalakshmi15/aceest-fitness-gym/tags

# Verify image name in deployment
kubectl get deployment aceest-web -n aceest-fitness -o yaml | grep image:

# If using ACR, verify attachment
az aks update --resource-group <rg> --name <cluster> --attach-acr <acr-name>
```

**CrashLoopBackOff**:
```bash
# Check pod logs
kubectl logs <pod-name> -n aceest-fitness

# Check previous logs
kubectl logs <pod-name> -n aceest-fitness --previous

# Common issues:
# - Database connection failure (check postgres service)
# - Missing environment variables (check configmap/secrets)
# - Application errors (check logs)
```

**Pending**:
```bash
# Check node resources
kubectl describe nodes

# Check if PVC is bound (for PostgreSQL)
kubectl get pvc -n aceest-fitness

# Check resource quotas
kubectl describe resourcequota -n aceest-fitness
```

---

### Issue: Health Check Fails

**Symptom**: Health check times out or returns non-200

**Solutions**:
```bash
# Check if LoadBalancer IP is assigned
kubectl get service aceest-web-service -n aceest-fitness

# Test health endpoint manually
curl http://<external-ip>/health

# Check if ingress is ready
kubectl get ingress -n aceest-fitness

# Port-forward to test directly
kubectl port-forward service/aceest-web-service 8080:5000 -n aceest-fitness
curl http://localhost:8080/health
```

---

### Issue: Database Connection Errors

**Symptom**: Application can't connect to PostgreSQL

**Solutions**:
```bash
# Check PostgreSQL status
kubectl get statefulset postgres -n aceest-fitness
kubectl get pods -l app=postgres -n aceest-fitness

# Check PostgreSQL logs
kubectl logs postgres-0 -n aceest-fitness

# Verify service exists
kubectl get service postgres-service -n aceest-fitness

# Test connection from application pod
kubectl exec -it <app-pod> -n aceest-fitness -- bash
nc -zv postgres-service 5432

# Check secrets are correct
kubectl get secret aceest-secrets -n aceest-fitness -o yaml
echo '<base64-encoded-password>' | base64 -d
```

---

## ✨ Best Practices

### 1. Version Control
- ✅ Always use semantic versioning (v1.2.3)
- ✅ Tag releases in Git: `git tag -a v1.2.3 -m "Release 1.2.3"`
- ✅ Match IMAGE_TAG with Git tags for traceability

### 2. Testing
- ✅ Never skip tests in production deployments
- ✅ Maintain >70% code coverage
- ✅ Write tests for all new features
- ✅ Run tests locally before pushing

### 3. Deployments
- ✅ Use `rolling-update` for standard releases
- ✅ Use `canary` for major changes
- ✅ Use `blue-green` for critical production updates
- ✅ Test in `dev` → `staging` → `production` sequence
- ✅ Monitor deployments for 15-30 minutes after release

### 4. Security
- ✅ Rotate credentials every 90 days
- ✅ Use least-privilege access for kubeconfig
- ✅ Enable Docker Content Trust: `export DOCKER_CONTENT_TRUST=1`
- ✅ Review Trivy security scan results
- ✅ Fix HIGH/CRITICAL vulnerabilities before deployment

### 5. Monitoring
- ✅ Set up alerts for failed builds
- ✅ Monitor AKS cluster health
- ✅ Track deployment metrics
- ✅ Review SonarQube dashboard weekly

### 6. Rollback Strategy
- ✅ Always have a rollback plan
- ✅ Test rollback procedures in non-production
- ✅ Document rollback steps for each strategy
- ✅ Keep previous images in registry

---

## 📧 Notifications

### Email Notifications

Configure in Jenkinsfile `post` section:

```groovy
emailext (
    subject: "BUILD ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
    body: """<p>BUILD ${currentBuild.result}</p>
             <p>Job: ${env.JOB_NAME}</p>
             <p>Build: ${env.BUILD_NUMBER}</p>
             <p>URL: ${env.BUILD_URL}</p>""",
    to: 'team@example.com',
    recipientProviders: [[$class: 'DevelopersRecipientProvider']]
)
```

### Slack Notifications

Install Slack plugin and configure:

```groovy
slackSend (
    color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
    message: "BUILD ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
)
```

---

## 📚 Additional Resources

- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)

---

## 🆘 Support

**Issues?** Check troubleshooting section above or contact DevOps team.

**Pipeline Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintained By**: DevOps Team
