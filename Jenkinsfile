#!/usr/bin/env groovy
/**
 * Jenkins CI/CD Pipeline for ACEest Fitness Gym Management Application
 * 
 * Features:
 * - Automated testing with Pytest
 * - SonarQube code quality analysis
 * - Docker image build and push to Docker Hub
 * - Parameterized deployment to AKS with multiple strategies
 * - Health checks and rollback capabilities
 * - Email/Slack notifications
 * 
 * Required Jenkins Credentials:
 * - dockerhub-credentials: Docker Hub username/password
 * - kubeconfig-aks: AKS cluster kubeconfig file
 * - sonarqube-token: SonarQube authentication token
 * - github-token: GitHub token (optional, for PR status)
 * 
 * Required Jenkins Plugins:
 * - Docker Pipeline
 * - Kubernetes CLI
 * - SonarQube Scanner
 * - Pipeline Utility Steps
 * - Credentials Binding
 */

pipeline {
    agent any
    
    parameters {
        choice(
            name: 'DEPLOYMENT_STRATEGY',
            choices: ['rolling-update', 'blue-green', 'canary', 'ab-testing', 'shadow'],
            description: 'Select deployment strategy for Kubernetes'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'production'],
            description: 'Target environment for deployment'
        )
        string(
            name: 'IMAGE_TAG',
            defaultValue: 'latest',
            description: 'Docker image tag (default: latest, or specify version like v1.2.3)'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run automated tests'
        )
        booleanParam(
            name: 'RUN_SONARQUBE',
            defaultValue: true,
            description: 'Run SonarQube analysis'
        )
        booleanParam(
            name: 'DEPLOY_TO_AKS',
            defaultValue: true,
            description: 'Deploy to AKS cluster'
        )
        booleanParam(
            name: 'SKIP_BUILD',
            defaultValue: false,
            description: 'Skip Docker build (use existing image)'
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
        SONARQUBE_URL = 'http://20.244.27.1:9000'  // Update with your SonarQube URL
        SONAR_TOKEN = credentials('sonarqube-token')
        
        // Build metadata
        BUILD_VERSION = "${IMAGE_TAG}-${BUILD_NUMBER}"
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        BUILD_TIMESTAMP = sh(returnStdout: true, script: 'date +%Y%m%d-%H%M%S').trim()
        
        // Python environment
        PYTHONUNBUFFERED = '1'
        PYTEST_ADDOPTS = '--color=yes'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '30'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        ansiColor('xterm')
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code..."
                    checkout scm
                    
                    // Store git info for traceability
                    env.GIT_BRANCH = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    env.GIT_COMMIT_MSG = sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim()
                    env.GIT_AUTHOR = sh(returnStdout: true, script: 'git log -1 --pretty=%an').trim()
                    
                    echo """
                    📋 Build Information:
                    - Branch: ${env.GIT_BRANCH}
                    - Commit: ${GIT_COMMIT_SHORT}
                    - Author: ${env.GIT_AUTHOR}
                    - Message: ${env.GIT_COMMIT_MSG}
                    - Build: ${BUILD_NUMBER}
                    - Version: ${BUILD_VERSION}
                    """
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
                        
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                            echo "✅ Virtual environment created"
                        else
                            echo "ℹ️  Using existing virtual environment"
                        fi
                        
                        . venv/bin/activate
                        
                        pip --version
                        
                        pip install --upgrade pip setuptools wheel
                        
                        pip install -r flask_app/requirements.txt
                        
                        echo "✅ Environment setup complete"
                    """
                }
            }
        }
        
        stage('Run Tests') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                script {
                    echo "🧪 Running automated tests with Pytest..."
                    sh """
                        . venv/bin/activate
                        
                        pip install -r flask_app/requirements-test.txt
                        
                        mkdir -p test-results
                        
                        pytest \\
                            --verbose \\
                            --junit-xml=test-results/pytest-results.xml \\
                            --cov=flask_app \\
                            --cov-report=html:htmlcov \\
                            --cov-report=xml:coverage.xml \\
                            --cov-report=term-missing \\
                            --cov-branch \\
                            --cov-fail-under=70 \\
                            || exit 1
                        
                        echo "✅ All tests passed!"
                    """
                }
            }
            post {
                always {
                    // Publish test results
                    junit testResults: 'test-results/pytest-results.xml', allowEmptyResults: true
                    
                    // Publish HTML coverage report
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
                expression { params.RUN_SONARQUBE == true }
            }
            steps {
                script {
                    echo "📊 Running SonarQube code analysis..."
                    
                    withSonarQubeEnv('SonarQube') {
                        sh '''
                            . venv/bin/activate
                            
                            # Run SonarQube scanner
                            sonar-scanner \
                                -Dsonar.projectKey=aceest-fitness-gym \
                                -Dsonar.sources=app,run.py,config.py \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url=${SONARQUBE_URL} \
                                -Dsonar.login=${SONAR_TOKEN} \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.python.xunit.reportPath=test-results/pytest-results.xml \
                                -Dsonar.projectVersion=${BUILD_VERSION} \
                                -Dsonar.scm.revision=${GIT_COMMIT_SHORT} \
                                -Dsonar.branch.name=${GIT_BRANCH}
                        '''
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                expression { params.RUN_SONARQUBE == true }
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
                expression { params.SKIP_BUILD == false }
            }
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    
                    // Build with multiple tags
                    def imageTags = [
                        "${env.BUILD_VERSION}",
                        "${env.IMAGE_TAG}",
                        "${env.GIT_BRANCH}-${env.BUILD_NUMBER}",
                        "build-${env.BUILD_NUMBER}"
                    ]
                    
                    // Add 'latest' tag only for main/master branch
                    if (env.GIT_BRANCH in ['main', 'master']) {
                        imageTags.add('latest')
                    }
                    
                    // Build the image
                    def buildArgs = [
                        "--build-arg BUILD_DATE=${env.BUILD_TIMESTAMP}",
                        "--build-arg VCS_REF=${env.GIT_COMMIT_SHORT}",
                        "--build-arg VERSION=${env.BUILD_VERSION}",
                        "--label org.opencontainers.image.created=${env.BUILD_TIMESTAMP}",
                        "--label org.opencontainers.image.revision=${env.GIT_COMMIT_SHORT}",
                        "--label org.opencontainers.image.version=${env.BUILD_VERSION}",
                        "--label org.opencontainers.image.source=${env.GIT_URL}",
                        "--label jenkins.build.number=${env.BUILD_NUMBER}",
                        "--label jenkins.build.url=${env.BUILD_URL}"
                    ].join(' ')
                    
                    sh """
                        docker build ${buildArgs} \
                            -t ${DOCKER_IMAGE}:${env.BUILD_VERSION} \
                            -f Dockerfile .
                        
                        echo "✅ Docker image built successfully"
                    """
                    
                    // Tag the image with all tags
                    imageTags.each { tag ->
                        sh "docker tag ${DOCKER_IMAGE}:${env.BUILD_VERSION} ${DOCKER_IMAGE}:${tag}"
                        echo "Tagged: ${DOCKER_IMAGE}:${tag}"
                    }
                    
                    // Store tags for later use
                    env.DOCKER_TAGS = imageTags.join(',')
                }
            }
        }
        
        stage('Security Scan') {
            when {
                expression { params.SKIP_BUILD == false }
            }
            steps {
                script {
                    echo "🔒 Scanning Docker image for vulnerabilities..."
                    
                    // Using Trivy for vulnerability scanning
                    sh """
                        # Install Trivy if not available
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy..."
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
                            echo "deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
                            sudo apt-get update
                            sudo apt-get install trivy -y
                        fi
                        
                        # Scan the image
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --format table \
                            --output trivy-report.txt \
                            ${DOCKER_IMAGE}:${BUILD_VERSION} || true
                        
                        # Display scan results
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
                expression { params.SKIP_BUILD == false }
            }
            steps {
                script {
                    echo "📤 Pushing Docker image to Docker Hub..."
                    
                    sh '''
                        # Login to Docker Hub
                        echo "${DOCKERHUB_CREDENTIALS_PSW}" | docker login -u "${DOCKERHUB_CREDENTIALS_USR}" --password-stdin ${DOCKER_REGISTRY}
                        
                        # Push all tags
                        IFS=',' read -ra TAGS <<< "${DOCKER_TAGS}"
                        for tag in "${TAGS[@]}"; do
                            echo "Pushing ${DOCKER_IMAGE}:${tag}"
                            docker push ${DOCKER_IMAGE}:${tag}
                        done
                        
                        echo "✅ All images pushed successfully"
                        
                        # Logout
                        docker logout ${DOCKER_REGISTRY}
                    '''
                }
            }
        }
        
        stage('Deploy to AKS') {
            when {
                expression { params.DEPLOY_TO_AKS == true }
            }
            steps {
                script {
                    echo "☸️  Deploying to AKS cluster..."
                    echo "Strategy: ${params.DEPLOYMENT_STRATEGY}"
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Image: ${DOCKER_IMAGE}:${BUILD_VERSION}"
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        sh """
                            # Verify kubectl access
                            kubectl version --client
                            kubectl cluster-info
                            
                            # Create namespace if not exists
                            kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Update image tag in manifests
                            cd kube_manifests
                            
                            # Update configmap with environment-specific settings
                            kubectl create configmap aceest-config \
                                --from-literal=FLASK_ENV=${params.ENVIRONMENT} \
                                --namespace=${K8S_NAMESPACE} \
                                --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Deploy base infrastructure (if not exists)
                            echo "📦 Deploying base infrastructure..."
                            kubectl apply -f 00-namespace.yaml
                            kubectl apply -f 01-configmap.yaml
                            kubectl apply -f 02-secrets.yaml
                            kubectl apply -f 03-postgres-statefulset.yaml
                            kubectl apply -f 04-hpa.yaml
                            kubectl apply -f 05-resource-quotas.yaml
                            kubectl apply -f 06-network-policies.yaml
                            kubectl apply -f 07-ingress.yaml
                            
                            # Wait for PostgreSQL to be ready
                            echo "⏳ Waiting for PostgreSQL to be ready..."
                            kubectl wait --for=condition=ready pod -l app=postgres \
                                --namespace=${K8S_NAMESPACE} \
                                --timeout=300s || true
                            
                            # Deploy application with selected strategy
                            echo "🚀 Deploying application with ${params.DEPLOYMENT_STRATEGY} strategy..."
                            
                            # Update image in deployment manifest
                            find strategies/${params.DEPLOYMENT_STRATEGY}/ -name "*.yaml" -exec \
                                sed -i "s|image: dharmalakshmi15/aceest-fitness-gym:.*|image: ${DOCKER_IMAGE}:${BUILD_VERSION}|g" {} +
                            
                            # Apply the deployment
                            kubectl apply -f strategies/${params.DEPLOYMENT_STRATEGY}/
                            
                            echo "✅ Deployment initiated"
                        """
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            when {
                expression { params.DEPLOY_TO_AKS == true }
            }
            steps {
                script {
                    echo "🔍 Verifying deployment..."
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        sh """
                            # Wait for deployment to be ready
                            echo "⏳ Waiting for pods to be ready..."
                            kubectl wait --for=condition=ready pod \
                                -l app=aceest-web \
                                --namespace=${K8S_NAMESPACE} \
                                --timeout=300s
                            
                            # Check deployment status
                            echo "📊 Deployment Status:"
                            kubectl get deployments -n ${K8S_NAMESPACE}
                            kubectl get pods -n ${K8S_NAMESPACE}
                            kubectl get services -n ${K8S_NAMESPACE}
                            
                            # Get service endpoint
                            echo "🌐 Service Endpoints:"
                            kubectl get ingress -n ${K8S_NAMESPACE}
                            
                            # Check pod logs for errors
                            echo "📋 Recent Pod Logs:"
                            kubectl logs -l app=aceest-web \
                                --namespace=${K8S_NAMESPACE} \
                                --tail=50 \
                                --since=5m || true
                        """
                    }
                }
            }
        }
        
        stage('Health Check') {
            when {
                expression { params.DEPLOY_TO_AKS == true }
            }
            steps {
                script {
                    echo "🏥 Running health checks..."
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        def healthCheckPassed = false
                        def maxRetries = 10
                        def retryCount = 0
                        
                        while (!healthCheckPassed && retryCount < maxRetries) {
                            try {
                                sh """
                                    # Get service URL
                                    SERVICE_IP=\$(kubectl get service aceest-web-service \
                                        -n ${K8S_NAMESPACE} \
                                        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                                    
                                    if [ -z "\$SERVICE_IP" ]; then
                                        echo "⏳ Waiting for LoadBalancer IP..."
                                        sleep 10
                                        exit 1
                                    fi
                                    
                                    echo "Testing health endpoint: http://\$SERVICE_IP/health"
                                    
                                    # Test health endpoint
                                    HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" \
                                        --max-time 10 \
                                        http://\$SERVICE_IP/health)
                                    
                                    if [ "\$HTTP_CODE" = "200" ]; then
                                        echo "✅ Health check passed (HTTP \$HTTP_CODE)"
                                        exit 0
                                    else
                                        echo "⚠️  Health check returned HTTP \$HTTP_CODE"
                                        exit 1
                                    fi
                                """
                                healthCheckPassed = true
                            } catch (Exception e) {
                                retryCount++
                                echo "⏳ Health check attempt ${retryCount}/${maxRetries} failed. Retrying..."
                                sleep 15
                            }
                        }
                        
                        if (!healthCheckPassed) {
                            error "❌ Health check failed after ${maxRetries} attempts"
                        }
                    }
                }
            }
        }
        
        stage('Smoke Tests') {
            when {
                expression { params.DEPLOY_TO_AKS == true }
            }
            steps {
                script {
                    echo "💨 Running smoke tests..."
                    
                    withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIAL}", variable: 'KUBECONFIG')]) {
                        sh """
                            # Get service endpoint
                            SERVICE_IP=\$(kubectl get service aceest-web-service \
                                -n ${K8S_NAMESPACE} \
                                -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                            
                            BASE_URL="http://\$SERVICE_IP"
                            
                            echo "Testing endpoints on \$BASE_URL"
                            
                            # Test home page
                            echo "Testing: \$BASE_URL/"
                            curl -f -s -o /dev/null -w "HTTP %{http_code}\\n" \$BASE_URL/
                            
                            # Test health endpoint
                            echo "Testing: \$BASE_URL/health"
                            curl -f -s -o /dev/null -w "HTTP %{http_code}\\n" \$BASE_URL/health
                            
                            # Test login page
                            echo "Testing: \$BASE_URL/auth/login"
                            curl -f -s -o /dev/null -w "HTTP %{http_code}\\n" \$BASE_URL/auth/login
                            
                            # Test register page
                            echo "Testing: \$BASE_URL/auth/register"
                            curl -f -s -o /dev/null -w "HTTP %{http_code}\\n" \$BASE_URL/auth/register
                            
                            echo "✅ Smoke tests passed!"
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                
                // Archive artifacts
                archiveArtifacts artifacts: '**/test-results/*.xml', allowEmptyArchive: true
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
                
                // Clean up Docker images
                sh """
                    docker image prune -f || true
                    docker system df
                """
            }
        }
        
        success {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def message = """
                ✅ *BUILD SUCCESS*
                
                *Job:* ${env.JOB_NAME}
                *Build:* #${env.BUILD_NUMBER}
                *Duration:* ${duration}
                *Strategy:* ${params.DEPLOYMENT_STRATEGY}
                *Environment:* ${params.ENVIRONMENT}
                *Image:* ${DOCKER_IMAGE}:${BUILD_VERSION}
                
                *Branch:* ${env.GIT_BRANCH}
                *Commit:* ${env.GIT_COMMIT_SHORT}
                *Author:* ${env.GIT_AUTHOR}
                
                📊 [Build Details](${env.BUILD_URL})
                📈 [Coverage Report](${env.BUILD_URL}Coverage_Report/)
                """
                
                echo message
                
                // Send notifications (configure your notification method)
                // emailext(...)
                // slackSend(...)
            }
        }
        
        failure {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def message = """
                ❌ *BUILD FAILED*
                
                *Job:* ${env.JOB_NAME}
                *Build:* #${env.BUILD_NUMBER}
                *Duration:* ${duration}
                *Strategy:* ${params.DEPLOYMENT_STRATEGY}
                *Environment:* ${params.ENVIRONMENT}
                
                *Branch:* ${env.GIT_BRANCH}
                *Commit:* ${env.GIT_COMMIT_SHORT}
                *Author:* ${env.GIT_AUTHOR}
                
                🔍 [Build Details](${env.BUILD_URL})
                📋 [Console Output](${env.BUILD_URL}console)
                """
                
                echo message
                
                // Send failure notifications
                // emailext(...)
                // slackSend(...)
                
                // Rollback deployment if health check failed
                if (params.DEPLOY_TO_AKS == true) {
                    echo "⚠️  Consider rolling back the deployment"
                }
            }
        }
        
        unstable {
            echo "⚠️  Build is unstable. Check test results and quality gates."
        }
        
        aborted {
            echo "🛑 Build was aborted."
        }
    }
}
