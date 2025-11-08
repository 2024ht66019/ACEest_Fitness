#!/usr/bin/env groovy
// Jenkins Multi-branch Pipeline - ACEest Fitness
// Last updated: 2025-11-08
/**
 * Jenkins Multi-branch Pipeline for ACEest Fitness Gym Management Application
 * 
 * Supports:
 * - Multi-branch pipeline with automatic branch discovery
 * - Branch-specific deployment strategies and environments
 * - Pull request validation
 * - Automated testing, SonarQube analysis, Docker build/push
 * - Kubernetes deployment to AKS
 * 
 * Branch Strategy:
 * - main/master    → production (blue-green deployment)
 * - develop        → staging (canary deployment)
 * - feature/*      → dev (rolling-update, manual deploy)
 * - hotfix/*       → production (rolling-update, manual approval)
 * - release/*      → staging (canary deployment)
 * - Pull Requests  → test only (no deployment)
 * 
 * Required Jenkins Credentials:
 * - dockerhub-credentials: Docker Hub username/password
 * - kubeconfig-aks: AKS cluster kubeconfig file
 * - sonarqube-token: SonarQube authentication token
 * - github-token: GitHub Personal Access Token
 */

pipeline {
    agent any
    
    environment {
        // Docker configuration
        DOCKER_IMAGE = 'dharmalakshmi15/aceest-fitness-gym'
        DOCKER_REGISTRY = 'docker.io'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        
        // Kubernetes configuration
        KUBECONFIG_CREDENTIAL = 'kubeconfig-aks'
        K8S_NAMESPACE = 'aceest-fitness'
        
        // SonarQube configuration
        SONARQUBE_URL = 'http://sonarqube:9000'
        SONAR_TOKEN = credentials('sonarqube-token')
        
        // Branch-based environment selection
        DEPLOY_ENV = "${env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' ? 'production' : env.BRANCH_NAME == 'develop' ? 'staging' : env.BRANCH_NAME.startsWith('release/') ? 'staging' : 'dev'}"
        
        // Branch-based deployment strategy
        DEPLOYMENT_STRATEGY = "${env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' ? 'blue-green' : env.BRANCH_NAME == 'develop' ? 'canary' : env.BRANCH_NAME.startsWith('release/') ? 'canary' : env.BRANCH_NAME.startsWith('hotfix/') ? 'rolling-update' : 'rolling-update'}"
        
        // Image tag strategy
        IMAGE_TAG = "${env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' ? 'latest' : env.BRANCH_NAME == 'develop' ? 'staging' : env.BRANCH_NAME.replaceAll('/', '-') + '-' + env.BUILD_NUMBER}"
        
        // Build metadata
        BUILD_VERSION = "${IMAGE_TAG}"
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        BUILD_TIMESTAMP = sh(returnStdout: true, script: 'date +%Y%m%d-%H%M%S').trim()
        
        // Python environment
        PYTHONUNBUFFERED = '1'
        PYTEST_ADDOPTS = '--color=yes'
        
        // Deployment control flags
        SHOULD_DEPLOY = "${(env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'develop' || env.BRANCH_NAME.startsWith('release/')) ? 'true' : 'false'}"
        IS_PR = "${env.CHANGE_ID != null ? 'true' : 'false'}"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '30'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        ansiColor('xterm')
    }
    
    stages {
        stage('Branch Information') {
            steps {
                script {
                    echo """
                    ╔═══════════════════════════════════════════════════════════╗
                    ║           ACEest Fitness CI/CD Pipeline                 ║
                    ╚═══════════════════════════════════════════════════════════╝
                    
                    🌿 Branch Information:
                    ├─ Branch: ${env.BRANCH_NAME}
                    ├─ Commit: ${GIT_COMMIT_SHORT}
                    ├─ Author: ${sh(returnStdout: true, script: 'git log -1 --pretty=%an').trim()}
                    └─ Message: ${sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim()}
                    
                    📦 Build Configuration:
                    ├─ Environment: ${DEPLOY_ENV}
                    ├─ Strategy: ${DEPLOYMENT_STRATEGY}
                    ├─ Image Tag: ${IMAGE_TAG}
                    ├─ Build Number: ${BUILD_NUMBER}
                    └─ Deploy: ${SHOULD_DEPLOY == 'true' ? '✅ Auto' : '❌ Manual Only'}
                    """
                    
                    if (env.CHANGE_ID) {
                        echo """
                        🔀 Pull Request Information:
                        ├─ PR Number: #${env.CHANGE_ID}
                        ├─ Source Branch: ${env.CHANGE_BRANCH}
                        ├─ Target Branch: ${env.CHANGE_TARGET}
                        ├─ PR Title: ${env.CHANGE_TITLE}
                        └─ PR Author: ${env.CHANGE_AUTHOR}
                        
                        ℹ️  This is a PR build - deployment skipped
                        """
                    }
                }
            }
        }
        
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Code already checked out by multi-branch pipeline"
                    checkout scm
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "🔧 Setting up Python environment..."
                    sh """
                        set -e
                        python3 --version
                        echo "Verifying python3-venv availability (no sudo escalation inside pipeline)"
                        if ! python3 -m venv --help >/dev/null 2>&1; then
                            echo "❌ python3-venv not available on agent. Install manually:"
                            echo "   sudo apt-get update && sudo apt-get install -y python3-venv python3-pip"
                            exit 1
                        fi

                        echo "If directory exists but activation script missing, treat as corrupted and recreate"
                        if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
                            echo "⚠️  Detected corrupted venv (missing bin/activate). Recreating..."
                            rm -rf venv
                        fi

                        echo "Creating venv if absent"
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                            echo "✅ Virtual environment created"
                        else
                            echo "ℹ️  Using existing virtual environment"
                        fi

                        echo "Activating virtual environment"
                        . venv/bin/activate || { echo "❌ Failed to activate venv"; ls -R venv || true; exit 1; }

                        echo "Ensuring pip exists (handle rare ensurepip omission)"
                        if ! command -v pip >/dev/null 2>&1; then
                            echo "⚠️  pip missing inside venv; running ensurepip..."
                            python3 -m ensurepip --upgrade || true
                        fi

                        pip --version || { echo "❌ pip still unavailable"; exit 1; }

                        echo "Upgrading base packaging tools (quiet, retry once on failure)"
                        pip install --upgrade pip setuptools wheel --quiet || pip install --upgrade pip setuptools wheel
                        
                        echo "Installing application dependencies"
                        pip install -r requirements.txt
                        
                        echo "✅ Environment setup complete"
                        echo "📁 venv contents summary:"; ls -1 venv | sed 's/^/   - /'
                    """
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "🧪 Running automated tests with Pytest..."
                    sh """
                        . venv/bin/activate
                        echo "Installing test requirements (file lives at repo root, not under flask_app)"
                        if [ -f requirements-test.txt ]; then
                            pip install -r requirements-test.txt
                        else
                            echo "❌ requirements-test.txt not found at repo root. Listing contents for diagnostics:"; ls -1 . | sed 's/^/   - /'
                            exit 1
                        fi
                        
                        echo "Ensuring test results directory exists (pytest won't create nested path automatically)"
                        mkdir -p test-results
                        
                        pytest \\
                            --verbose \\
                            --junit-xml=test-results/pytest-results.xml \\
                            --cov=. \\
                            --cov-report=html:htmlcov \\
                            --cov-report=xml:coverage.xml \\
                            --cov-report=term-missing \\
                            --cov-branch \\
                            --cov-fail-under=45 \\
                            || exit 1
                        
                        echo "✅ All tests passed!"
                    """
                }
            }
            post {
                always {
                    junit testResults: 'test-results/pytest-results.xml', allowEmptyResults: true
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
                failure {
                    echo "❌ Tests failed! Check the test report for details."
                }
            }
        }
        
        stage('SonarQube Analysis') {
            when {
                not { changeRequest() }  // Skip for PRs if desired, or keep for all
            }
            steps {
                script {
                    echo "📊 Running SonarQube code analysis..."
                    
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \\
                                -Dsonar.projectKey=aceest-fitness-gym \\
                                -Dsonar.sources=. \\
                                -Dsonar.tests=tests \\
                                -Dsonar.python.coverage.reportPaths=coverage.xml \\
                                -Dsonar.python.xunit.reportPath=test-results/pytest-results.xml \\
                                -Dsonar.projectVersion=${BUILD_VERSION} \\
                                -Dsonar.scm.revision=${GIT_COMMIT_SHORT} \\
                                -Dsonar.sourceEncoding=UTF-8 \\
                                -Dsonar.exclusions=venv/**,htmlcov/**,app_files/**,flask_app/**,kube_manifests/**,terraform/**
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                not { changeRequest() }
            }
            steps {
                script {
                    echo "🚦 Checking SonarQube Quality Gate..."
                    timeout(time: 5, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "❌ Quality Gate failed: ${qg.status}"
                        }
                        echo "✅ Quality Gate passed!"
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                not { changeRequest() }  // Skip for PRs
            }
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    
                    def buildArgs = [
                        "--build-arg BUILD_DATE=${env.BUILD_TIMESTAMP}",
                        "--build-arg VCS_REF=${env.GIT_COMMIT_SHORT}",
                        "--build-arg VERSION=${env.BUILD_VERSION}",
                        "--label org.opencontainers.image.created=${env.BUILD_TIMESTAMP}",
                        "--label org.opencontainers.image.revision=${env.GIT_COMMIT_SHORT}",
                        "--label org.opencontainers.image.version=${env.BUILD_VERSION}",
                        "--label jenkins.build.number=${env.BUILD_NUMBER}",
                        "--label jenkins.branch=${env.BRANCH_NAME}"
                    ].join(' ')
                    
                    sh """
                        docker build ${buildArgs} \
                            -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                            -f Dockerfile \
                            .
                        
                        echo "✅ Docker image built: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    """
                    
                    // Tag with additional tags for main/master branch
                    if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                        sh """
                            docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest
                            docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:production
                            echo "Tagged as 'latest' and 'production'"
                        """
                    }
                }
            }
        }
        
        stage('Security Scan') {
            when {
                not { changeRequest() }
            }
            steps {
                script {
                    echo "🔒 Scanning Docker image for vulnerabilities..."
                    sh """
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy..."
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
                            echo "deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
                            sudo apt-get update
                            sudo apt-get install trivy -y
                        fi
                        
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --format table \
                            --output trivy-report.txt \
                            ${DOCKER_IMAGE}:${IMAGE_TAG} || true
                        
                        cat trivy-report.txt
                        echo "✅ Security scan complete"
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                not { changeRequest() }
            }
            steps {
                script {
                    echo "📤 Pushing Docker image to Docker Hub..."
                    sh '''
                        echo "${DOCKERHUB_CREDENTIALS_PSW}" | docker login -u "${DOCKERHUB_CREDENTIALS_USR}" --password-stdin ${DOCKER_REGISTRY}
                        
                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                        echo "✅ Pushed ${DOCKER_IMAGE}:${IMAGE_TAG}"
                        
                        echo "Pushing additional tags for main branch if applicable"
                        if [ "${BRANCH_NAME}" = "main" ] || [ "${BRANCH_NAME}" = "master" ]; then
                            docker push ${DOCKER_IMAGE}:latest
                            docker push ${DOCKER_IMAGE}:production
                            echo "✅ Pushed latest and production tags"
                        fi
                        
                        docker logout ${DOCKER_REGISTRY}
                    '''
                }
            }
        }
        
        stage('Deploy to AKS') {
            when {
                expression { 
                    env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false'
                }
            }
            steps {
                script {
                    echo """
                    ☸️  Deploying to AKS cluster...
                    ├─ Environment: ${DEPLOY_ENV}
                    ├─ Strategy: ${DEPLOYMENT_STRATEGY}
                    ├─ Image: ${DOCKER_IMAGE}:${IMAGE_TAG}
                    └─ Namespace: ${K8S_NAMESPACE}
                    """
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        sh """
                            kubectl version --client
                            kubectl cluster-info
                            
                            kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            cd kube_manifests
                            
                            echo "📦 Deploying base infrastructure..."
                            kubectl apply -f 00-namespace.yaml
                            kubectl apply -f 01-configmap.yaml
                            kubectl apply -f 02-secrets.yaml
                            kubectl apply -f 03-postgres-statefulset.yaml
                            kubectl apply -f 04-hpa.yaml
                            kubectl apply -f 05-resource-quotas.yaml
                            kubectl apply -f 06-network-policies.yaml
                            kubectl apply -f 07-ingress.yaml
                            
                            echo "⏳ Waiting for PostgreSQL..."
                            kubectl wait --for=condition=ready pod -l app=postgres \
                                --namespace=${K8S_NAMESPACE} --timeout=300s || true
                            
                            echo "🚀 Deploying application (${DEPLOYMENT_STRATEGY})..."
                            find strategies/${DEPLOYMENT_STRATEGY}/ -name "*.yaml" -exec \
                                sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
                            
                            kubectl apply -f strategies/${DEPLOYMENT_STRATEGY}/
                            echo "✅ Deployment initiated"
                        """
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            when {
                expression { 
                    env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false'
                }
            }
            steps {
                script {
                    echo "🔍 Verifying deployment..."
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        sh """
                            echo "⏳ Waiting for pods to be ready..."
                            kubectl wait --for=condition=ready pod -l app=aceest-web \
                                --namespace=${K8S_NAMESPACE} --timeout=300s
                            
                            echo "📊 Deployment Status:"
                            kubectl get deployments -n ${K8S_NAMESPACE}
                            kubectl get pods -n ${K8S_NAMESPACE}
                            kubectl get services -n ${K8S_NAMESPACE}
                            kubectl get ingress -n ${K8S_NAMESPACE}
                        """
                    }
                }
            }
        }
        
        stage('Health Check') {
            when {
                expression { 
                    env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false'
                }
            }
            steps {
                script {
                    echo "🏥 Running health checks..."
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        retry(10) {
                            sleep 15
                            sh """
                                SERVICE_IP=\$(kubectl get service aceest-web-service \
                                    -n ${K8S_NAMESPACE} \
                                    -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                                
                                if [ -z "\$SERVICE_IP" ]; then
                                    echo "⏳ Waiting for LoadBalancer IP..."
                                    exit 1
                                fi
                                
                                HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" \
                                    --max-time 10 http://\$SERVICE_IP/health)
                                
                                if [ "\$HTTP_CODE" = "200" ]; then
                                    echo "✅ Health check passed (HTTP \$HTTP_CODE)"
                                else
                                    echo "⚠️  Health check returned HTTP \$HTTP_CODE"
                                    exit 1
                                fi
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                archiveArtifacts artifacts: '**/test-results/*.xml', allowEmptyArchive: true
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
                
                sh "docker image prune -f || true"
            }
        }
        
        success {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def status = env.IS_PR == 'true' ? 'PR Build' : 'Deployment'
                
                echo """
                ╔═══════════════════════════════════════════════════════════╗
                ║                  ✅ BUILD SUCCESS                        ║
                ╚═══════════════════════════════════════════════════════════╝
                
                📋 Build Details:
                ├─ Job: ${env.JOB_NAME}
                ├─ Build: #${env.BUILD_NUMBER}
                ├─ Duration: ${duration}
                ├─ Branch: ${env.BRANCH_NAME}
                ├─ Commit: ${env.GIT_COMMIT_SHORT}
                └─ Type: ${status}
                
                📦 Artifacts:
                ├─ Image: ${DOCKER_IMAGE}:${IMAGE_TAG}
                ├─ Environment: ${DEPLOY_ENV}
                └─ Strategy: ${DEPLOYMENT_STRATEGY}
                
                🔗 Links:
                ├─ Build: ${env.BUILD_URL}
                └─ Coverage: ${env.BUILD_URL}Coverage_Report/
                """
            }
        }
        
        failure {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                echo """
                ╔═══════════════════════════════════════════════════════════╗
                ║                   ❌ BUILD FAILED                        ║
                ╚═══════════════════════════════════════════════════════════╝
                
                📋 Build Details:
                ├─ Job: ${env.JOB_NAME}
                ├─ Build: #${env.BUILD_NUMBER}
                ├─ Duration: ${duration}
                ├─ Branch: ${env.BRANCH_NAME}
                └─ Commit: ${env.GIT_COMMIT_SHORT}
                
                🔍 Debug:
                ├─ Console: ${env.BUILD_URL}console
                └─ Logs: Check stage-specific logs above
                """
                
                if (env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false') {
                    echo "⚠️  Deployment may need rollback"
                }
            }
        }
    }
}
