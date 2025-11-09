# ACEest Fitness - Gym Management Application

A comprehensive fitness tracking and gym management web application built with Flask, containerized with Docker, and deployed on Azure Kubernetes Service (AKS) using modern DevOps practices.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5.svg)](https://kubernetes.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

ACEest Fitness is a full-stack web application designed for fitness enthusiasts and gym members to track workouts, monitor progress, and manage their fitness journey. The application features user authentication, workout logging with MET-based calorie calculations, progress analytics, and personalized workout plans.

### Key Features

- 🔐 **User Authentication** - Secure registration and login with password hashing
- 💪 **Workout Tracking** - Log workouts with duration, type, and automatic calorie calculation
- 📊 **Analytics Dashboard** - Visualize progress with charts and statistics
- 🎯 **Workout Plans** - Create and follow personalized workout routines
- 🍎 **Diet Tracking** - Monitor nutritional intake and diet plans
- 📱 **Responsive Design** - Bootstrap 5 UI works on all devices
- 🔒 **Security** - SQLAlchemy ORM with parameterized queries, CSRF protection

---

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- HTML5, CSS3 (Bootstrap 5)
- JavaScript (vanilla)
- Jinja2 templating

**Backend:**
- Python 3.13
- Flask 3.0.0 web framework
- SQLAlchemy 2.0.35 ORM
- PostgreSQL 16 (production) / SQLite (development)

**DevOps & Infrastructure:**
- Docker & Docker Compose (containerization)
- Kubernetes (orchestration)
- Azure Kubernetes Service (AKS)
- Terraform (infrastructure as code)
- Jenkins (CI/CD pipeline)
- SonarQube (code quality)
- Pytest (automated testing)

**Deployment Strategies:**
- Rolling Update
- Blue-Green Deployment
- Canary Release
- A/B Testing
- Shadow Deployment

---

## 📁 Project Structure 

```
ACEest_Fitness/
├── app.py                        # Flask application entry point
├── config.py                     # Configuration settings
├── run.py                        # Application runner
├── requirements.txt              # Python dependencies
├── requirements-test.txt         # Test dependencies
├── utils.py                      # Utility functions
│
├── models/                       # Database models
│   ├── user.py                  # User model
│   └── workout.py               # Workout model
│
├── routes/                       # Application routes
│   ├── auth.py                  # Authentication routes
│   ├── main.py                  # Main routes
│   ├── workouts.py              # Workout routes
│   └── analytics.py             # Analytics routes
│
├── templates/                    # HTML templates
├── static/                       # CSS, JS, images
│
├── tests/                        # Automated tests
│   ├── conftest.py              # Pytest fixtures
│   ├── test_auth.py             # Authentication tests
│   ├── test_workouts.py         # Workout tests
│   ├── test_api.py              # API endpoint tests
│   └── test_models.py           # Model tests
│
├── kube_manifests/               # Kubernetes manifests
│   ├── 00-namespace.yaml        # Namespace definition
│   ├── 01-configmap.yaml        # Configuration
│   ├── 02-secrets.yaml          # Secrets management
│   ├── 03-postgres-statefulset.yaml  # PostgreSQL database
│   ├── 04-hpa.yaml              # Horizontal Pod Autoscaler
│   ├── 05-resource-quotas.yaml  # Resource limits
│   ├── 06-network-policies.yaml # Network security
│   ├── 07-ingress.yaml          # Ingress controller
│   └── strategies/              # Deployment strategies
│       ├── rolling-update/      # Standard K8s rolling update
│       ├── blue-green/          # Zero-downtime deployment
│       ├── canary/              # Gradual traffic shift
│       ├── ab-testing/          # A/B comparison testing
│       └── shadow/              # Parallel testing
│
├── docs/                         # Documentation
│   ├── DEPLOYMENT-STRATEGIES.md # Deployment strategies guide
│   ├── JENKINS-PARAMETERS.md    # Pipeline parameters reference
│   ├── DEPLOYMENT-IMPLEMENTATION.md  # Implementation details
│   ├── DEPLOYMENT-DIAGRAM.md    # Strategy diagrams
│   ├── CLUSTER-RESOURCES.md     # Resource optimization guide
│   ├── GITHUB-JENKINS-WEBHOOK.md     # GitHub webhook setup
│   ├── JENKINS-PIPELINE.md      # Jenkins CI/CD guide
│   ├── JENKINS-QUICKSTART.md    # Jenkins quick start
│   └── PIPELINE_DEBUG_SUMMARY.md     # Pipeline debugging
│
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                  # Main Terraform configuration
│   ├── terraform.tfvars         # Variable values
│   └── modules/
│       ├── aks/                 # AKS cluster module
│       └── networking/          # Network module
│
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Multi-container setup
├── Jenkinsfile                   # Parameterized CI/CD pipeline
├── pytest.ini                    # Pytest configuration
├── sonar-project.properties     # SonarQube settings
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

### Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Git
- Kubernetes cluster (optional for K8s deployment)
- Jenkins (optional for CI/CD)

### Local Development

```bash
# Clone the repository
git clone https://github.com/2024ht66019/ACEest_Fitness.git
cd ACEest_Fitness

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Access the application at http://localhost:5000
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# http://localhost:80 (via LoadBalancer)
# http://localhost:5000 (direct Flask)

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests with coverage
pytest -v --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 🔧 CI/CD Pipeline

### Jenkins Parameterized Pipeline

The project uses a comprehensive Jenkins pipeline with **9 configurable parameters** supporting **5 deployment strategies**.

**Pipeline Features:**
- ✅ Parameterized builds with branch-based auto-selection
- ✅ Multi-stage deployment strategies
- ✅ Automatic rollback on failure
- ✅ Manual approval gates for production
- ✅ Resource cleanup between strategy switches

**Pipeline Stages:**
1. ✅ Branch Information & Configuration
2. ✅ Checkout & Python Environment Setup
3. ✅ Run Tests (Pytest with 45% coverage minimum)
4. ✅ SonarQube Analysis & Quality Gate
5. ✅ Docker Build with Build Arguments
6. ✅ Security Scan (Trivy vulnerability scanning)
7. ✅ Push to Docker Hub (dharmalakshmi15/aceest-fitness-gym)
8. ✅ Manual Approval (optional for production)
9. ✅ Save Pre-Deployment State (for rollback)
10. ✅ Strategy Cleanup (scale down other strategies)
11. ✅ Deploy to Kubernetes (strategy-specific)
12. ✅ Verify Deployment & Health Checks

**Pipeline Parameters:**
- `DEPLOYMENT_STRATEGY`: auto, blue-green, canary, rolling-update, shadow, ab-testing
- `SKIP_TESTS`: Skip test execution (not recommended)
- `SKIP_SONAR`: Skip SonarQube analysis
- `SKIP_SECURITY_SCAN`: Skip Trivy security scan
- `CANARY_TRAFFIC_STEPS`: Traffic distribution steps (e.g., 10,50,100)
- `CANARY_WAIT_TIME`: Seconds between canary steps (default: 120s)
- `AB_TRAFFIC_SPLIT`: A/B traffic split percentage (0-100)
- `AUTO_ROLLBACK`: Automatic rollback on failure (default: true)
- `MANUAL_APPROVAL`: Require approval before production deploy

**Branch Strategy:**
- `main` → Production (auto: blue-green)
- `develop` → Staging (auto: canary)
- `feature/*` → Dev (auto: rolling-update)
- `hotfix/*` → Production (rolling-update, manual approval)
- `release/*` → Staging (canary)
- Pull Requests → Test only (no deployment)

**Documentation:**
- 📖 [DEPLOYMENT-STRATEGIES.md](docs/DEPLOYMENT-STRATEGIES.md) - Complete strategy guide
- 📖 [JENKINS-PARAMETERS.md](docs/JENKINS-PARAMETERS.md) - Parameter reference
- 📖 [DEPLOYMENT-IMPLEMENTATION.md](docs/DEPLOYMENT-IMPLEMENTATION.md) - Implementation details
- 📖 [DEPLOYMENT-DIAGRAM.md](docs/DEPLOYMENT-DIAGRAM.md) - Visual diagrams
- 📖 [JENKINS-PIPELINE.md](docs/JENKINS-PIPELINE.md) - Jenkins setup guide
- 📖 [GITHUB-JENKINS-WEBHOOK.md](docs/GITHUB-JENKINS-WEBHOOK.md) - GitHub webhook setup

---

## ☸️ Kubernetes Deployment

### Deploy to Kubernetes

```bash
cd kube_manifests

# Configure kubectl for your cluster
kubectl config use-context <your-cluster>

# Create namespace
kubectl apply -f 00-namespace.yaml

# Deploy infrastructure
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secrets.yaml
kubectl apply -f 03-postgres-statefulset.yaml
kubectl apply -f 04-hpa.yaml
kubectl apply -f 05-resource-quotas.yaml
kubectl apply -f 06-network-policies.yaml
kubectl apply -f 07-ingress.yaml

# Deploy with a specific strategy
kubectl apply -f strategies/rolling-update/

# Check deployment status
kubectl get all -n aceest-fitness

# Access application via LoadBalancer
kubectl get service aceest-web-service -n aceest-fitness
```

### Available Deployment Strategies

All strategies work with **native Kubernetes** (no Istio required):

| Strategy | Implementation | Traffic Control | Rollback Method |
|----------|----------------|-----------------|-----------------|
| **Rolling Update** | Native K8s RollingUpdate | Gradual pod replacement | `kubectl rollout undo` |
| **Blue-Green** | Dual deployments + service selector | Instant switch | Change service selector |
| **Canary** | Replica-based scaling | Approximate % via pod count | Scale canary to 0 |
| **A/B Testing** | Dual deployments + replica scaling | Approximate % via pod count | Scale variant B to 0 |
| **Shadow** | Parallel deployment | No traffic (manual testing) | Delete shadow deployment |

**Key Features:**
- ✅ No service mesh dependency (Istio optional)
- ✅ Replica-based traffic distribution
- ✅ Automatic cleanup between strategy switches
- ✅ Resource-optimized for 2-node clusters
- ✅ PostgreSQL StatefulSet for data persistence

**Resource Specifications (per 2-node cluster):**
- Total Capacity: 4 CPU cores, 8GB RAM
- Per Pod: 250m CPU request, 256Mi memory request
- Strategy Usage: 750m-1250m CPU, 768Mi-1280Mi memory

**Documentation:**
- 📖 [CLUSTER-RESOURCES.md](docs/CLUSTER-RESOURCES.md) - Resource optimization guide
- 📖 [DEPLOYMENT-STRATEGIES.md](docs/DEPLOYMENT-STRATEGIES.md) - Strategy details

---

## 🏗️ Infrastructure as Code

### Terraform - Azure AKS Deployment

```bash
cd terraform

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply infrastructure
terraform apply

# Get AKS credentials
az aks get-credentials \
  --resource-group aceest-fitness-rg \
  --name aceest-fitness-aks
```

**Resources Created:**
- Azure Resource Group
- Virtual Network & Subnets
- AKS Cluster (2 nodes, Standard_DS2_v2)
- Azure Container Registry (ACR)
- Application Gateway Ingress Controller
- Managed Identities

---

## 🧪 Testing

### Test Coverage

- **35+ automated tests** across 5 test files
- **45% minimum code coverage** enforced in CI/CD
- Unit tests, integration tests, and API tests

```bash
# Run specific test file
pytest tests/test_auth.py -v

# Run with markers
pytest -m unit -v

# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Test Categories

- ✅ **Authentication** (10 tests) - Registration, login, password hashing
- ✅ **Workouts** (10 tests) - CRUD operations, access control
- ✅ **API Endpoints** (7 tests) - Health checks, page loads
- ✅ **Models** (8 tests) - User/Workout models, relationships

**CI/CD Integration:**
- Automated test execution in Jenkins pipeline
- Coverage reports published to Jenkins
- Quality gate: minimum 45% coverage
- Test results archived as JUnit XML

---

## 📊 Code Quality

### SonarQube Analysis

```bash
# Run SonarQube scanner
sonar-scanner \
  -Dsonar.projectKey=aceest-fitness-gym \
  -Dsonar.sources=app \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.login=<token>
```

**Quality Gate Criteria:**
- Code Coverage ≥ 45%
- Bugs: 0
- Vulnerabilities: 0
- Code Smells < 50
- Duplications < 3%
- Security Hotspots: Reviewed

---

## 🔐 Security

### Implemented Security Measures

- ✅ **Password Hashing** - Werkzeug password hashing
- ✅ **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries
- ✅ **CSRF Protection** - Flask-WTF CSRF tokens
- ✅ **Session Management** - Secure Flask sessions
- ✅ **Input Validation** - WTForms validation
- ✅ **Docker Security** - Non-root user, multi-stage builds
- ✅ **K8s Security** - Network policies, resource quotas, RBAC
- ✅ **Secrets Management** - Kubernetes secrets, environment variables
- ✅ **Vulnerability Scanning** - Trivy image scanning in CI/CD

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT-STRATEGIES.md](docs/DEPLOYMENT-STRATEGIES.md) | Complete guide to all 5 deployment strategies |
| [JENKINS-PARAMETERS.md](docs/JENKINS-PARAMETERS.md) | Pipeline parameters reference and examples |
| [DEPLOYMENT-IMPLEMENTATION.md](docs/DEPLOYMENT-IMPLEMENTATION.md) | Implementation details and usage guide |
| [DEPLOYMENT-DIAGRAM.md](docs/DEPLOYMENT-DIAGRAM.md) | Visual diagrams for each strategy |
| [CLUSTER-RESOURCES.md](docs/CLUSTER-RESOURCES.md) | Resource optimization for 2-node clusters |
| [JENKINS-PIPELINE.md](docs/JENKINS-PIPELINE.md) | Complete Jenkins CI/CD setup guide |
| [JENKINS-QUICKSTART.md](docs/JENKINS-QUICKSTART.md) | Quick start guide for Jenkins |
| [GITHUB-JENKINS-WEBHOOK.md](docs/GITHUB-JENKINS-WEBHOOK.md) | GitHub webhook integration setup |
| [PIPELINE_DEBUG_SUMMARY.md](docs/PIPELINE_DEBUG_SUMMARY.md) | Pipeline debugging and troubleshooting |

---

## 🔄 Deployment Workflow

```
Developer → Git Push (develop branch)
    ↓
GitHub Webhook → Jenkins Trigger
    ↓
Jenkins Pipeline:
    ├─ 1. Branch Information & Configuration
    ├─ 2. Checkout Code
    ├─ 3. Setup Python Environment (venv)
    ├─ 4. Run Tests (Pytest with coverage)
    ├─ 5. SonarQube Analysis
    ├─ 6. Quality Gate Check
    ├─ 7. Build Docker Image
    ├─ 8. Security Scan (Trivy)
    ├─ 9. Push to Docker Hub
    ├─ 10. Manual Approval (if enabled)
    ├─ 11. Save Pre-Deployment State
    ├─ 12. Cleanup Other Strategies
    └─ 13. Deploy to Kubernetes
        ├─ Strategy Selection (auto → canary for develop)
        ├─ Apply Manifests
        ├─ Verify Deployment
        ├─ Health Checks
        └─ Rollback (if failure + auto-rollback enabled)
    ↓
Application Live on Kubernetes
    ├─ Canary: Gradual traffic shift (10% → 50% → 100%)
    ├─ Monitoring at each step
    └─ Automatic rollback on health check failure
```

**Key Features:**
- 🔄 Automatic strategy selection based on branch
- 🧹 Cleanup of previous strategy resources
- 🔙 Automatic rollback on deployment failure
- 🚦 Manual approval gates for production
- 📊 Comprehensive health checks and verification

---

## 🌟 Key Highlights

### DevOps Best Practices

✅ **Containerization** - Docker multi-stage builds, optimized images (Python 3.13-slim)  
✅ **Orchestration** - Kubernetes with 5 deployment strategies (native K8s, no Istio required)  
✅ **CI/CD** - Jenkins parameterized pipeline with 9 configurable parameters  
✅ **Deployment Strategies** - Blue-Green, Canary, Rolling Update, A/B Testing, Shadow  
✅ **Resource Management** - Optimized for 2-node clusters (2 CPU, 4GB RAM per node)  
✅ **Auto-Cleanup** - Automatic scaling down of previous strategy resources  
✅ **Rollback** - Automatic rollback on failure with pre-deployment state capture  
✅ **IaC** - Terraform for Azure infrastructure provisioning  
✅ **Testing** - 35+ automated tests with 45% minimum coverage  
✅ **Code Quality** - SonarQube integration with quality gates  
✅ **Security** - Trivy vulnerability scanning, secrets management, RBAC  
✅ **Monitoring** - Health checks, readiness/liveness probes, HPA  
✅ **Documentation** - 9 comprehensive markdown guides in docs/ folder  
✅ **Database** - PostgreSQL StatefulSet with persistent volumes  
✅ **Network Security** - Network policies, resource quotas, namespace isolation  

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Student ID:** 2024ht66019  
**Course:** DevOps Assignment - BITS Pilani  
**Project:** ACEest Fitness - Full-Stack DevOps Implementation

---

## 📧 Support

For issues, questions, or contributions:
- 📫 Open an issue on GitHub
- 📖 Check documentation in [/docs](docs/)
- 🔍 Review troubleshooting in [PIPELINE_DEBUG_SUMMARY.md](docs/PIPELINE_DEBUG_SUMMARY.md)
- 📚 Read deployment guides in [DEPLOYMENT-STRATEGIES.md](docs/DEPLOYMENT-STRATEGIES.md)

---

## 🙏 Acknowledgments

- Flask framework and community
- Docker and Kubernetes documentation
- Azure AKS team
- Jenkins CI/CD community
- SonarQube for code quality tools

---
