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
├── flask_app/                    # Main Flask application
│   ├── app.py                    # Application factory
│   ├── config.py                 # Configuration settings
│   ├── run.py                    # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── models/                   # Database models
│   │   ├── user.py              # User model
│   │   └── workout.py           # Workout model
│   ├── routes/                   # Application routes
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Main routes
│   │   ├── workouts.py          # Workout routes
│   │   └── analytics.py         # Analytics routes
│   ├── templates/                # HTML templates
│   ├── static/                   # CSS, JS, images
│   ├── Dockerfile                # Multi-stage Docker build
│   ├── docker-compose.yml        # Multi-container setup
│   └── nginx.conf                # Nginx reverse proxy config
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
│   ├── 03-postgres-statefulset.yaml  # Database
│   ├── 04-hpa.yaml              # Horizontal Pod Autoscaler
│   ├── 05-resource-quotas.yaml  # Resource limits
│   ├── 06-network-policies.yaml # Network security
│   ├── 07-ingress.yaml          # Ingress controller
│   ├── strategies/              # Deployment strategies
│   │   ├── rolling-update/
│   │   ├── blue-green/
│   │   ├── canary/
│   │   ├── ab-testing/
│   │   └── shadow/
│   └── deploy.sh                # Deployment automation script
│
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                  # Main Terraform configuration
│   ├── terraform.tfvars         # Variable values
│   └── modules/
│       ├── aks/                 # AKS cluster module
│       └── networking/          # Network module
│
├── .github/workflows/            # GitHub Actions
│   └── notify-jenkins.yml       # Jenkins webhook trigger
│
├── Jenkinsfile                   # Single-branch CI/CD pipeline
├── Jenkinsfile.multibranch      # Multi-branch CI/CD pipeline
├── pytest.ini                    # Pytest configuration
├── sonar-project.properties     # SonarQube settings
├── requirements-test.txt        # Test dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Git

### Local Development

```bash
# Clone the repository
git clone https://github.com/2024ht66019/ACEest_Fitness.git
cd ACEest_Fitness/flask_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Access the application
# http://localhost:5000
```

### Docker Deployment

```bash
cd flask_app

# Build and run with Docker Compose
docker-compose up -d

# Access the application
# http://localhost:80 (via Nginx)
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
pytest -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 🔧 CI/CD Pipeline

### Jenkins Multi-branch Pipeline

The project includes two Jenkins pipeline configurations:

1. **Jenkinsfile** - Traditional parameterized pipeline
2. **Jenkinsfile.multibranch** - Automated multi-branch pipeline

**Pipeline Stages:**
1. ✅ Checkout & Setup
2. ✅ Run Tests (Pytest with 70% coverage)
3. ✅ SonarQube Analysis & Quality Gate
4. ✅ Docker Build & Security Scan (Trivy)
5. ✅ Push to Docker Hub
6. ✅ Deploy to AKS (strategy-based)
7. ✅ Health Checks & Smoke Tests

**Branch Strategy:**
- `main` → Production (blue-green deployment)
- `develop` → Staging (canary deployment)
- `feature/*` → Dev (rolling update, manual)
- `hotfix/*` → Production (rolling update, manual)

**Setup Guide:** [GITHUB-JENKINS-WEBHOOK.md](GITHUB-JENKINS-WEBHOOK.md)

---

## ☸️ Kubernetes Deployment

### Deploy to AKS

```bash
cd kube_manifests

# Configure kubectl for AKS
az aks get-credentials --resource-group <rg> --name <cluster>

# Deploy with a specific strategy
./deploy.sh rolling-update deploy

# Or deploy all infrastructure
./deploy.sh all deploy

# Check deployment status
kubectl get all -n aceest-fitness

# Access application via LoadBalancer
kubectl get service aceest-web-service -n aceest-fitness
```

### Available Deployment Strategies

| Strategy | Use Case | Traffic Split | Rollback |
|----------|----------|---------------|----------|
| **Rolling Update** | Standard deployments | Gradual | `kubectl rollout undo` |
| **Blue-Green** | Zero-downtime releases | Instant switch | Service selector change |
| **Canary** | Gradual rollout | 10% canary / 90% stable | Scale canary to 0 |
| **A/B Testing** | Feature testing | Header-based routing | Scale version B to 0 |
| **Shadow** | Production testing | Mirror traffic | Remove shadow deployment |

**Detailed Guide:** [kube_manifests/README.md](kube_manifests/README.md)

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
- **70% minimum code coverage** enforced
- Unit tests, integration tests, and API tests

```bash
# Run specific test file
pytest tests/test_auth.py -v

# Run with markers
pytest -m unit -v

# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term
```

### Test Categories

- ✅ **Authentication** (10 tests) - Registration, login, validation
- ✅ **Workouts** (10 tests) - CRUD operations, access control
- ✅ **API Endpoints** (7 tests) - Health checks, page loads
- ✅ **Models** (8 tests) - User/Workout models, relationships

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
- Code Coverage ≥ 70%
- Bugs: 0
- Vulnerabilities: 0
- Code Smells < 50
- Duplications < 3%

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
| [QUICKSTART.md](flask_app/QUICKSTART.md) | Quick start guide for Flask app |
| [DOCKER.md](flask_app/DOCKER.md) | Docker setup and deployment |
| [README.md](kube_manifests/README.md) | Kubernetes deployment guide |
| [AKS-GUIDE.md](kube_manifests/AKS-GUIDE.md) | Azure AKS specific configuration |
| [JENKINS-PIPELINE.md](JENKINS-PIPELINE.md) | Complete Jenkins CI/CD guide |
| [GITHUB-JENKINS-WEBHOOK.md](GITHUB-JENKINS-WEBHOOK.md) | GitHub webhook setup |

---

## 🔄 Deployment Workflow

```
Developer → Git Push
    ↓
GitHub Webhook → Jenkins
    ↓
Jenkins Pipeline:
    ├─ Checkout Code
    ├─ Run Tests (Pytest)
    ├─ SonarQube Analysis
    ├─ Quality Gate Check
    ├─ Build Docker Image
    ├─ Security Scan (Trivy)
    ├─ Push to Docker Hub
    └─ Deploy to AKS
        ├─ Update Manifests
        ├─ Apply Deployment
        ├─ Health Checks
        └─ Smoke Tests
    ↓
Application Live on AKS
```

---

## 🌟 Key Highlights

### DevOps Best Practices

✅ **Containerization** - Docker multi-stage builds, optimized images  
✅ **Orchestration** - Kubernetes with 5 deployment strategies  
✅ **CI/CD** - Jenkins multi-branch pipeline with automated testing  
✅ **IaC** - Terraform for Azure infrastructure  
✅ **Testing** - 35+ automated tests with 70% coverage  
✅ **Code Quality** - SonarQube integration with quality gates  
✅ **Security** - Vulnerability scanning, secrets management  
✅ **Monitoring** - Health checks, readiness/liveness probes  
✅ **Documentation** - Comprehensive guides for all components  

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
- 📖 Check documentation in `/docs`
- 🔍 Review troubleshooting guides

---

## 🙏 Acknowledgments

- Flask framework and community
- Docker and Kubernetes documentation
- Azure AKS team
- Jenkins CI/CD community
- SonarQube for code quality tools

---
