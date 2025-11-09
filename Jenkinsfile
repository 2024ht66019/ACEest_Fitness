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
    
    parameters {
        choice(
            name: 'DEPLOYMENT_STRATEGY',
            choices: ['auto', 'blue-green', 'canary', 'rolling-update', 'shadow', 'ab-testing'],
            description: '''Deployment Strategy:
            • auto: Branch-based selection (main→blue-green, develop→canary, feature→rolling)
            • blue-green: Zero-downtime deployment with instant rollback
            • canary: Gradual traffic shift (10% → 50% → 100%)
            • rolling-update: Sequential pod replacement
            • shadow: Deploy alongside production for testing (no traffic)
            • ab-testing: Split traffic for A/B comparison'''
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution (not recommended for production)'
        )
        booleanParam(
            name: 'SKIP_SONAR',
            defaultValue: false,
            description: 'Skip SonarQube analysis'
        )
        booleanParam(
            name: 'SKIP_SECURITY_SCAN',
            defaultValue: false,
            description: 'Skip Trivy security scan'
        )
        choice(
            name: 'CANARY_TRAFFIC_STEPS',
            choices: ['10,50,100', '20,40,60,80,100', '25,75,100', '10,30,50,70,100'],
            description: 'Canary traffic distribution steps (percentages)'
        )
        string(
            name: 'CANARY_WAIT_TIME',
            defaultValue: '120',
            description: 'Seconds to wait between canary traffic steps (for monitoring)'
        )
        string(
            name: 'AB_TRAFFIC_SPLIT',
            defaultValue: '50',
            description: 'A/B Testing traffic split percentage for variant B (0-100)'
        )
        booleanParam(
            name: 'AUTO_ROLLBACK',
            defaultValue: true,
            description: 'Automatically rollback on deployment failure'
        )
        booleanParam(
            name: 'MANUAL_APPROVAL',
            defaultValue: false,
            description: 'Require manual approval before production deployment'
        )
    }
    
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
        
        // Deployment strategy resolution
        DEPLOYMENT_STRATEGY_RESOLVED = "${params.DEPLOYMENT_STRATEGY == 'auto' ? (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' ? 'blue-green' : env.BRANCH_NAME == 'develop' ? 'canary' : env.BRANCH_NAME.startsWith('release/') ? 'canary' : 'rolling-update') : params.DEPLOYMENT_STRATEGY}"
        
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
        
        // Rollback metadata
        PREVIOUS_DEPLOYMENT = ''
        ROLLBACK_AVAILABLE = 'false'
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
                    ├─ Strategy: ${DEPLOYMENT_STRATEGY_RESOLVED} ${params.DEPLOYMENT_STRATEGY == 'auto' ? '(auto-selected)' : '(manual)'}
                    ├─ Image Tag: ${IMAGE_TAG}
                    ├─ Build Number: ${BUILD_NUMBER}
                    └─ Deploy: ${SHOULD_DEPLOY == 'true' ? '✅ Auto' : '❌ Manual Only'}
                    
                    ⚙️  Pipeline Parameters:
                    ├─ Skip Tests: ${params.SKIP_TESTS}
                    ├─ Skip SonarQube: ${params.SKIP_SONAR}
                    ├─ Skip Security Scan: ${params.SKIP_SECURITY_SCAN}
                    ├─ Manual Approval: ${params.MANUAL_APPROVAL}
                    └─ Auto Rollback: ${params.AUTO_ROLLBACK}
                    """
                    
                    if (DEPLOYMENT_STRATEGY_RESOLVED == 'canary') {
                        echo """
                    🕯️  Canary Configuration:
                    ├─ Traffic Steps: ${params.CANARY_TRAFFIC_STEPS}%
                    └─ Wait Time: ${params.CANARY_WAIT_TIME}s between steps
                        """
                    }
                    
                    if (DEPLOYMENT_STRATEGY_RESOLVED == 'ab-testing') {
                        echo """
                    🔬 A/B Testing Configuration:
                    ├─ Variant A (current): ${100 - params.AB_TRAFFIC_SPLIT.toInteger()}%
                    └─ Variant B (new): ${params.AB_TRAFFIC_SPLIT}%
                        """
                    }
                    
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
            when {
                expression { !params.SKIP_TESTS }
            }
            steps {
                script {
                    echo "🧪 Running automated tests with Pytest..."
                    sh """
                        . venv/bin/activate
                        echo "Installing test requirements from repo root"
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
                allOf {
                    not { changeRequest() }
                    expression { !params.SKIP_SONAR }
                }
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
                                -Dsonar.sourceEncoding=UTF-8 \
                                -Dsonar.exclusions=venv/**,htmlcov/**,app_files/**,kube_manifests/**,terraform/**
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                allOf {
                    not { changeRequest() }
                    expression { !params.SKIP_SONAR }
                }
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
                allOf {
                    not { changeRequest() }
                    expression { !params.SKIP_SECURITY_SCAN }
                }
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
        
        stage('Manual Approval') {
            when {
                allOf {
                    expression { params.MANUAL_APPROVAL }
                    expression { env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false' }
                    expression { env.DEPLOY_ENV == 'production' }
                }
            }
            steps {
                script {
                    echo """
                    ⏸️  Manual Approval Required
                    ├─ Environment: ${DEPLOY_ENV}
                    ├─ Strategy: ${DEPLOYMENT_STRATEGY_RESOLVED}
                    ├─ Image: ${DOCKER_IMAGE}:${IMAGE_TAG}
                    └─ Waiting for approval...
                    """
                    
                    timeout(time: 30, unit: 'MINUTES') {
                        input message: "Deploy to ${DEPLOY_ENV} using ${DEPLOYMENT_STRATEGY_RESOLVED}?",
                              ok: 'Deploy',
                              submitter: 'admin,deployer'
                    }
                    echo "✅ Deployment approved"
                }
            }
        }
        
        stage('Save Pre-Deployment State') {
            when {
                expression { 
                    env.SHOULD_DEPLOY == 'true' && env.IS_PR == 'false' && params.AUTO_ROLLBACK
                }
            }
            steps {
                script {
                    echo "💾 Saving pre-deployment state for rollback..."
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        def deploymentExists = sh(
                            returnStatus: true,
                            script: "kubectl get deployment aceest-web -n ${K8S_NAMESPACE} 2>/dev/null"
                        )
                        
                        if (deploymentExists == 0) {
                            env.PREVIOUS_DEPLOYMENT = sh(
                                returnStdout: true,
                                script: """
                                    kubectl get deployment aceest-web -n ${K8S_NAMESPACE} \
                                        -o jsonpath='{.spec.template.spec.containers[0].image}'
                                """
                            ).trim()
                            env.ROLLBACK_AVAILABLE = 'true'
                            echo "✅ Saved current deployment: ${env.PREVIOUS_DEPLOYMENT}"
                        } else {
                            echo "ℹ️  No previous deployment found (first deployment)"
                            env.ROLLBACK_AVAILABLE = 'false'
                        }
                    }
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
                    ├─ Strategy: ${DEPLOYMENT_STRATEGY_RESOLVED}
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
                        """
                        
                        // Strategy-specific deployment
                        switch(DEPLOYMENT_STRATEGY_RESOLVED) {
                            case 'blue-green':
                                deployBlueGreen()
                                break
                            case 'canary':
                                deployCanary()
                                break
                            case 'rolling-update':
                                deployRollingUpdate()
                                break
                            case 'shadow':
                                deployShadow()
                                break
                            case 'ab-testing':
                                deployABTesting()
                                break
                            default:
                                error "Unknown deployment strategy: ${DEPLOYMENT_STRATEGY_RESOLVED}"
                        }
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
                                INGRESS_HOST=\$(kubectl get ingress aceest-web-ingress --no-headers \\
                                    --namespace=${K8S_NAMESPACE} \\
                                    | awk '{print \$3}')
                                
                                if [ -z "\$INGRESS_HOST" ]; then
                                    echo "⏳ Waiting for Ingress host..."
                                    exit 1
                                fi
                                
                                HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" \
                                    --max-time 10 http://\$INGRESS_HOST/health)
                                
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
        
        failure {
            script {
                if (params.AUTO_ROLLBACK && env.ROLLBACK_AVAILABLE == 'true' && env.SHOULD_DEPLOY == 'true') {
                    echo """
                    ⚠️  DEPLOYMENT FAILED - INITIATING ROLLBACK
                    ├─ Previous Image: ${env.PREVIOUS_DEPLOYMENT}
                    └─ Strategy: ${DEPLOYMENT_STRATEGY_RESOLVED}
                    """
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        try {
                            sh """
                                kubectl set image deployment/aceest-web \
                                    aceest-web=${env.PREVIOUS_DEPLOYMENT} \
                                    -n ${K8S_NAMESPACE}
                                
                                kubectl rollout status deployment/aceest-web \
                                    -n ${K8S_NAMESPACE} --timeout=300s
                            """
                            echo "✅ Rollback completed successfully"
                        } catch (Exception e) {
                            echo "❌ Rollback failed: ${e.message}"
                            echo "⚠️  Manual intervention required!"
                        }
                    }
                }
                
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
                └─ Strategy: ${DEPLOYMENT_STRATEGY_RESOLVED}
                
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

// ═══════════════════════════════════════════════════════════════════════
// DEPLOYMENT STRATEGY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════

/**
 * Blue-Green Deployment Strategy
 * - Deploy new version to "green" environment
 * - Test green environment
 * - Switch traffic from blue to green
 * - Keep blue for instant rollback
 */
def deployBlueGreen() {
    echo "🔵🟢 Executing Blue-Green Deployment..."
    
    sh """
        cd kube_manifests
        
        # Determine current active color
        CURRENT_COLOR=\$(kubectl get service aceest-web-service -n ${K8S_NAMESPACE} \
            -o jsonpath='{.spec.selector.color}' 2>/dev/null || echo 'blue')
        
        if [ "\$CURRENT_COLOR" = "blue" ]; then
            NEW_COLOR="green"
        else
            NEW_COLOR="blue"
        fi
        
        echo "📊 Current: \$CURRENT_COLOR → New: \$NEW_COLOR"
        
        # Deploy to new color
        echo "🚀 Deploying \$NEW_COLOR environment..."
        find strategies/blue-green/ -name "*.yaml" -exec \
            sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
        
        find strategies/blue-green/ -name "*.yaml" -exec \
            sed -i "s|color: blue|color: \$NEW_COLOR|g" {} +
        
        kubectl apply -f strategies/blue-green/
        
        # Wait for new deployment
        echo "⏳ Waiting for \$NEW_COLOR deployment..."
        kubectl wait --for=condition=available deployment/aceest-web-\$NEW_COLOR \
            -n ${K8S_NAMESPACE} --timeout=300s
        
        # Run health check on new deployment
        echo "🏥 Health checking \$NEW_COLOR..."
        sleep 10
        
        POD=\$(kubectl get pod -n ${K8S_NAMESPACE} -l color=\$NEW_COLOR -o jsonpath='{.items[0].metadata.name}')
        kubectl exec \$POD -n ${K8S_NAMESPACE} -- curl -f http://localhost:5000/health || {
            echo "❌ Health check failed on \$NEW_COLOR"
            exit 1
        }
        
        # Switch service to new color
        echo "🔄 Switching traffic to \$NEW_COLOR..."
        kubectl patch service aceest-web-service -n ${K8S_NAMESPACE} \
            -p '{"spec":{"selector":{"color":"'\$NEW_COLOR'"}}}'
        
        echo 'Blue-Green deployment complete!'
        echo "Old \$CURRENT_COLOR deployment kept for rollback"
    """
}

/**
 * Canary Deployment Strategy
 * - Deploy canary version alongside production
 * - Gradually shift traffic (10% → 50% → 100%)
 * - Monitor metrics at each step
 * - Rollback if issues detected
 */
def deployCanary() {
    echo "🕯️  Executing Canary Deployment..."
    
    def trafficSteps = params.CANARY_TRAFFIC_STEPS.split(',').collect { it.toInteger() }
    def waitTime = params.CANARY_WAIT_TIME.toInteger()
    
    sh """
        cd kube_manifests
        
        echo "🚀 Deploying canary version..."
        find strategies/canary/ -name "*.yaml" -exec \
            sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
        
        kubectl apply -f strategies/canary/
        
        echo "⏳ Waiting for canary deployment..."
        kubectl wait --for=condition=available deployment/aceest-web-canary \
            -n ${K8S_NAMESPACE} --timeout=300s
    """
    
    // Gradually shift traffic
    trafficSteps.each { percent ->
        echo "📊 Shifting ${percent}% traffic to canary..."
        
        sh """
            kubectl patch virtualservice aceest-web-vs -n ${K8S_NAMESPACE} --type merge -p '
            {
              "spec": {
                "http": [{
                  "route": [
                    {
                      "destination": {
                        "host": "aceest-web-stable",
                        "port": {"number": 5000}
                      },
                      "weight": ${ 100 - percent }
                    },
                    {
                      "destination": {
                        "host": "aceest-web-canary",
                        "port": {"number": 5000}
                      },
                      "weight": ${percent}
                    }
                  ]
                }]
              }
            }'
            
            echo "✅ Traffic shifted: ${percent}% to canary"
        """
        
        if (percent < 100) {
            echo "⏸️  Monitoring for ${waitTime}s before next step..."
            sleep waitTime
            
            // Check metrics/health
            def healthOk = sh(
                returnStatus: true,
                script: """
                    kubectl exec deployment/aceest-web-canary -n ${K8S_NAMESPACE} \
                        -- curl -sf http://localhost:5000/health
                """
            )
            
            if (healthOk != 0) {
                error "❌ Canary health check failed at ${percent}% traffic"
            }
        }
    }
    
    echo "Canary deployment complete! 100% traffic now on canary. Stable version can be removed after validation."
}

/**
 * Rolling Update Deployment Strategy
 * - Update pods gradually with zero downtime
 * - Default Kubernetes rolling update
 * - Automatic rollback on failure
 */
def deployRollingUpdate() {
    echo "🔄 Executing Rolling Update Deployment..."
    
    sh """
        cd kube_manifests
        
        echo "🚀 Applying rolling update..."
        find strategies/rolling-update/ -name "*.yaml" -exec \
            sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
        
        find strategies/rolling-update/ -name "*.yaml" -exec \
            sed -i "s|last_build: \"TIMESTAMP_PLACEHOLDER\"|last_build: \"${BUILD_TIMESTAMP}\"|g" {} +
        
        kubectl apply -f strategies/rolling-update/
        
        echo 'Monitoring rollout...'
        kubectl rollout status deployment/aceest-web -n ${K8S_NAMESPACE} --timeout=300s
        
        echo 'Rolling update complete!'
        kubectl get deployment aceest-web -n ${K8S_NAMESPACE}
    """
}

/**
 * Shadow Deployment Strategy
 * - Deploy new version alongside production
 * - Mirror production traffic to shadow (no user impact)
 * - Monitor shadow behavior and performance
 * - No traffic routing to shadow
 */
def deployShadow() {
    echo "👤 Executing Shadow Deployment..."
    
    sh """
        cd kube_manifests
        
        echo "🚀 Deploying shadow version..."
        find strategies/shadow/ -name "*.yaml" -exec \
            sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
        
        kubectl apply -f strategies/shadow/
        
        echo "⏳ Waiting for shadow deployment..."
        kubectl wait --for=condition=available deployment/aceest-web-shadow \
            -n ${K8S_NAMESPACE} --timeout=300s
        
        echo "🔍 Configuring traffic mirroring..."
        kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: aceest-web-mirror
  namespace: ${K8S_NAMESPACE}
spec:
  hosts:
  - aceest-web-service
  http:
  - route:
    - destination:
        host: aceest-web-production
        port:
          number: 5000
      weight: 100
    mirror:
      host: aceest-web-shadow
      port:
        number: 5000
    mirrorPercentage:
      value: 100
EOF
        
        echo 'Shadow deployment complete!'
        echo 'Production: 100% user traffic'
        echo 'Shadow: Receives mirrored traffic (no user impact)'
        echo 'Monitor shadow logs and metrics for validation'
    """
}

/**
 * A/B Testing Deployment Strategy
 * - Deploy variant B alongside variant A
 * - Split traffic based on parameter (e.g., 50/50)
 * - Use headers/cookies for consistent routing
 * - Compare metrics between variants
 */
def deployABTesting() {
    echo "🔬 Executing A/B Testing Deployment..."
    
    def trafficSplit = params.AB_TRAFFIC_SPLIT.toInteger()
    def variantA = 100 - trafficSplit
    
    sh """
        cd kube_manifests
        
        echo "🚀 Deploying A/B test variants..."
        find strategies/ab-testing/ -name "*.yaml" -exec \
            sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" {} +
        
        kubectl apply -f strategies/ab-testing/
        
        echo "⏳ Waiting for variant B deployment..."
        kubectl wait --for=condition=available deployment/aceest-web-variant-b \
            -n ${K8S_NAMESPACE} --timeout=300s
        
        echo "🎯 Configuring traffic split: A=${variantA}% / B=${trafficSplit}%"
        kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: aceest-web-ab-test
  namespace: ${K8S_NAMESPACE}
spec:
  hosts:
  - aceest-web-service
  http:
  - match:
    - headers:
        x-variant:
          exact: "B"
    route:
    - destination:
        host: aceest-web-variant-b
        port:
          number: 5000
  - route:
    - destination:
        host: aceest-web-variant-a
        port:
          number: 5000
      weight: ${variantA}
    - destination:
        host: aceest-web-variant-b
        port:
          number: 5000
      weight: ${trafficSplit}
EOF
        
        echo "A/B Testing deployment complete!"
        echo "Variant A (current): ${variantA}% traffic"
        echo "Variant B (new): ${trafficSplit}% traffic"
        echo 'Header routing: x-variant: B -> Variant B'
        echo 'Monitor conversion metrics and user behavior'
    """
}
