# GitHub Webhook Integration with Jenkins Multi-branch Pipeline

## 📋 Overview

This guide shows how to set up a Jenkins Multi-branch Pipeline with GitHub webhooks for automatic builds on:
- ✅ Code pushes to any branch
- ✅ Pull request creation/updates
- ✅ New branch creation
- ✅ Branch deletion

**Works with personal GitHub accounts!** ✨

---

## 🎯 What is Multi-branch Pipeline?

A Multi-branch Pipeline automatically:
- **Discovers branches** in your repository
- **Creates pipeline jobs** for each branch with a Jenkinsfile
- **Builds automatically** when code is pushed
- **Tracks pull requests** and shows status
- **Cleans up** jobs when branches are deleted

**Branch Strategy:**
```
main/master     → Production deployments
develop         → Staging deployments  
feature/*       → Dev environment testing
hotfix/*        → Production hotfixes
release/*       → Release candidates
```

---

## 🔧 Prerequisites

### 1. Jenkins Requirements
- Jenkins 2.375+ with plugins:
  - **Multibranch Pipeline** (installed by default)
  - **GitHub Branch Source** (for GitHub integration)
  - **GitHub** (for webhooks)
  - **Pipeline: Multibranch** 
  - **Git** (for Git operations)

Install missing plugins:
```
Manage Jenkins → Manage Plugins → Available
Search: "GitHub Branch Source"
Install and restart
```

### 2. GitHub Personal Access Token

Generate a token for Jenkins to access your repository:

**Steps:**
1. Go to GitHub: **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Configure:
   - **Note**: `Jenkins Multi-branch Pipeline`
   - **Expiration**: 90 days (or No expiration for testing)
   - **Scopes** (select these):
     - ✅ `repo` (Full control of private repositories)
       - ✅ `repo:status` (Access commit status)
       - ✅ `repo_deployment` (Access deployment status)
       - ✅ `public_repo` (if using public repo only)
     - ✅ `admin:repo_hook` (Full control of repository hooks)
       - ✅ `write:repo_hook`
       - ✅ `read:repo_hook`
4. Click **Generate token**
5. **Copy the token** (you won't see it again!)

**Example token**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🚀 Setup Instructions

### Option 1: Jenkins is Publicly Accessible (Recommended)

If your Jenkins server has a public URL (e.g., `https://jenkins.example.com`):

#### Step 1: Add GitHub Credentials to Jenkins

1. Go to **Manage Jenkins → Manage Credentials**
2. Click **(global)** domain
3. Click **Add Credentials**
4. Configure:
   - **Kind**: `Username with password`
   - **Username**: Your GitHub username (e.g., `dharmalakshmi15`)
   - **Password**: Paste the GitHub Personal Access Token
   - **ID**: `github-token`
   - **Description**: `GitHub Personal Access Token for webhooks`
5. Click **Create**

#### Step 2: Create Multi-branch Pipeline Job

1. Go to Jenkins Dashboard
2. Click **New Item**
3. Configure:
   - **Name**: `aceest-fitness-multibranch`
   - **Type**: Select **Multibranch Pipeline**
   - Click **OK**

#### Step 3: Configure Branch Sources

In the job configuration:

**Branch Sources:**
1. Click **Add source → GitHub**
2. Configure:
   - **Credentials**: Select `github-token`
   - **Repository HTTPS URL**: `https://github.com/your-username/aceest-fitness.git`
     - Replace `your-username` with your GitHub username
   - **Behaviors** (click Add):
     - ✅ **Discover branches** (Strategy: All branches)
     - ✅ **Discover pull requests from origin** (Strategy: Merging the pull request with current target branch revision)
     - ✅ **Discover pull requests from forks** (optional)
     - ✅ **Filter by name (with regular expression)**:
       - Include: `main|develop|feature/.*|hotfix/.*|release/.*`

**Build Configuration:**
- **Mode**: `by Jenkinsfile`
- **Script Path**: `Jenkinsfile`

**Scan Multibranch Pipeline Triggers:**
- ✅ Enable **Periodically if not otherwise run**
  - Interval: `1 hour` (fallback if webhook fails)
- ✅ Enable **Scan by webhook** (see below for token)

**Orphaned Item Strategy:**
- ✅ **Discard old items**
  - Days to keep: `7`
  - Max # of old items: `10`

**Property Strategy:**
- Select **All branches get the same properties**

Click **Save**

#### Step 4: Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings → Webhooks → Add webhook**
3. Configure:
   - **Payload URL**: 
     ```
     https://jenkins.example.com/github-webhook/
     ```
     - Replace with your Jenkins URL
     - **Important**: Include trailing slash `/`
   - **Content type**: `application/json`
   - **Secret**: Leave empty (or add shared secret for security)
   - **Which events**:
     - Select **Let me select individual events**
     - Check:
       - ✅ Pushes
       - ✅ Pull requests
       - ✅ Branch or tag creation
       - ✅ Branch or tag deletion
   - ✅ **Active**
4. Click **Add webhook**

#### Step 5: Test the Webhook

1. Push a commit to any branch:
   ```bash
   git add .
   git commit -m "Test webhook"
   git push origin main
   ```

2. Check webhook delivery:
   - GitHub: **Settings → Webhooks → Recent Deliveries**
   - Should show green checkmark ✅
   - Response: HTTP 200

3. Check Jenkins:
   - Job should trigger automatically
   - Branch should appear under `aceest-fitness-multibranch`

---

### Option 2: Jenkins Behind Firewall/NAT (Alternative)

If Jenkins is not publicly accessible (localhost, private network, behind NAT):

#### Option A: Use ngrok (Quick Testing)

**Expose Jenkins temporarily:**
```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at https://ngrok.com and get auth token
ngrok config add-authtoken <your-token>

# Expose Jenkins (default port 8080)
ngrok http 8080
```

**Output:**
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8080
```

**Use the ngrok URL** for webhook:
```
https://abc123.ngrok.io/github-webhook/
```

**⚠️ Warning**: ngrok free tier has limitations and URL changes on restart.

#### Option B: GitHub Actions Trigger (Recommended for Private Jenkins)

Use GitHub Actions to notify Jenkins instead of webhooks.

**Setup:**

1. **Create GitHub Secrets** (in your repository):
   - `JENKINS_URL`: Your Jenkins URL (can be internal IP like `http://192.168.1.100:8080`)
   - `JENKINS_USER`: Jenkins username
   - `JENKINS_TOKEN`: Jenkins API token

   **Get Jenkins API Token:**
   ```
   Jenkins → User (top right) → Configure → API Token → Add new Token
   ```

2. **GitHub Actions workflow** is already created: `.github/workflows/notify-jenkins.yml`

3. **Commit and push** the workflow file:
   ```bash
   git add .github/workflows/notify-jenkins.yml
   git commit -m "Add Jenkins notification workflow"
   git push
   ```

Now, every push/PR triggers GitHub Actions → GitHub Actions calls Jenkins → Jenkins builds!

#### Option C: Polling (Fallback)

Let Jenkins poll GitHub periodically (not ideal, but works):

**In Multi-branch job configuration:**
- **Scan Multibranch Pipeline Triggers**:
  - ✅ **Periodically if not otherwise run**
  - Interval: `5 minutes` (or `1 hour` to reduce API calls)

Jenkins will check for changes every 5 minutes.

---

## 🎛️ Branch-Specific Configuration

### Jenkinsfile with Branch Detection

Modify your Jenkinsfile to handle different branches:

```groovy
pipeline {
    agent any
    
    parameters {
        // Parameters only for manual builds
        choice(
            name: 'DEPLOYMENT_STRATEGY',
            choices: ['rolling-update', 'blue-green', 'canary', 'ab-testing', 'shadow'],
            description: 'Deployment strategy (auto-selected for branches)'
        )
    }
    
    environment {
        DOCKER_IMAGE = 'dharmalakshmi15/aceest-fitness-gym'
        
        // Branch-based environment selection
        DEPLOY_ENV = "${env.BRANCH_NAME == 'main' ? 'production' : 
                       env.BRANCH_NAME == 'develop' ? 'staging' : 'dev'}"
        
        // Branch-based deployment strategy
        STRATEGY = "${env.BRANCH_NAME == 'main' ? 'blue-green' : 
                     env.BRANCH_NAME == 'develop' ? 'canary' : 'rolling-update'}"
        
        // Image tag based on branch
        IMAGE_TAG = "${env.BRANCH_NAME == 'main' ? 'latest' : 
                     env.BRANCH_NAME == 'develop' ? 'staging' : 
                     env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Branch Info') {
            steps {
                script {
                    echo """
                    🌿 Branch: ${env.BRANCH_NAME}
                    📦 Environment: ${DEPLOY_ENV}
                    🚀 Strategy: ${STRATEGY}
                    🏷️  Image Tag: ${IMAGE_TAG}
                    """
                    
                    // Different behavior for PRs
                    if (env.CHANGE_ID) {
                        echo "🔀 Pull Request #${env.CHANGE_ID}"
                        echo "   Source: ${env.CHANGE_BRANCH}"
                        echo "   Target: ${env.CHANGE_TARGET}"
                    }
                }
            }
        }
        
        // ... rest of your stages ...
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo "Deploying ${DEPLOY_ENV} with ${STRATEGY}..."
                // Deploy logic
            }
        }
    }
}
```

### Branch Strategy Recommendations

| Branch Pattern | Environment | Strategy | Deploy? |
|---------------|-------------|----------|---------|
| `main` / `master` | production | blue-green | ✅ Auto |
| `develop` | staging | canary | ✅ Auto |
| `feature/*` | dev | rolling-update | ❌ Manual |
| `hotfix/*` | production | rolling-update | ⚠️ Manual approval |
| `release/*` | staging | canary | ✅ Auto |
| Pull Requests | - | - | ❌ Test only |

---

## 🔍 Verification & Testing

### 1. Test Branch Discovery

**Scan Repository Now:**
```
Jenkins → aceest-fitness-multibranch → Scan Multibranch Pipeline Now
```

**Expected Result:**
- Jenkins discovers all branches with `Jenkinsfile`
- Creates sub-jobs for each branch
- Example: `aceest-fitness-multibranch/main`, `aceest-fitness-multibranch/develop`

### 2. Test Webhook

**Method 1: Push commit**
```bash
git commit --allow-empty -m "Test webhook"
git push origin main
```

**Method 2: GitHub UI**
- Settings → Webhooks → Edit webhook → Recent Deliveries
- Click a delivery → Click "Redeliver"

**Expected Result:**
- GitHub webhook shows ✅ green checkmark
- Jenkins job triggers within seconds
- Build appears in Jenkins

### 3. Test Pull Request

**Create PR:**
```bash
git checkout -b feature/test-webhook
echo "test" >> README.md
git add README.md
git commit -m "Test PR webhook"
git push origin feature/test-webhook
```

Go to GitHub → Create Pull Request

**Expected Result:**
- Jenkins creates job: `aceest-fitness-multibranch/PR-X`
- Jenkins comment appears on PR with build status
- PR shows Jenkins status check

---

## 🔐 Security Best Practices

### 1. Use GitHub App (Advanced, Optional)

Instead of Personal Access Token, create a GitHub App for better security:

**Benefits:**
- Fine-grained permissions
- Per-repository installation
- Better audit logs

**Setup**: See [Jenkins GitHub App documentation](https://github.com/jenkinsci/github-branch-source-plugin/blob/master/docs/github-app.adoc)

### 2. Webhook Secret

Add shared secret for webhook authentication:

**Jenkins:**
1. Generate secret: `openssl rand -hex 32`
2. In Multi-branch config → **Add** → **GitHub hook trigger**
3. Enter secret

**GitHub:**
1. Webhook → Edit
2. **Secret**: Paste the same secret
3. Save

### 3. Restrict Jenkins Access

Configure firewall to only allow GitHub webhook IPs:

**GitHub Webhook IPs**: [GitHub Meta API](https://api.github.com/meta)
```bash
curl https://api.github.com/meta | jq -r '.hooks[]'
```

**Firewall rule example:**
```bash
# Allow GitHub webhooks (example IPs, check current list)
sudo ufw allow from 140.82.112.0/20 to any port 8080
sudo ufw allow from 143.55.64.0/20 to any port 8080
sudo ufw allow from 192.30.252.0/22 to any port 8080
```

### 4. HTTPS for Jenkins

Always use HTTPS for Jenkins in production:

**Options:**
- Nginx reverse proxy with Let's Encrypt
- Jenkins HTTPS directly
- Cloud load balancer with SSL termination

---

## 📊 Jenkins Blue Ocean UI (Optional)

Better visualization for Multi-branch pipelines:

**Install:**
```
Manage Jenkins → Manage Plugins → Available → Blue Ocean
```

**Access:**
```
http://jenkins.example.com/blue/organizations/jenkins/aceest-fitness-multibranch/
```

**Features:**
- Visual pipeline editor
- Branch/PR comparison
- Better logs and UI

---

## 🐛 Troubleshooting

### Webhook Not Triggering

**Check GitHub:**
1. Settings → Webhooks → Recent Deliveries
2. Look for errors (red X)
3. Check response:
   - **200**: Success ✅
   - **301/302**: Redirect (check URL has trailing `/`)
   - **403**: Forbidden (check Jenkins security)
   - **404**: Not found (wrong URL)
   - **500**: Jenkins error (check Jenkins logs)

**Check Jenkins:**
1. Manage Jenkins → System Log
2. Look for webhook events
3. Check GitHub plugin logs

**Common Issues:**
```
Issue: 302 Redirect
Solution: Add trailing slash → /github-webhook/

Issue: 403 Forbidden
Solution: Enable anonymous read access:
  Manage Jenkins → Security → Authorization
  Add "Anonymous" user with "Job/Read" permission

Issue: Webhook not received
Solution: Check firewall, use ngrok, or GitHub Actions alternative
```

### Branches Not Appearing

**Check:**
1. Scan logs: `aceest-fitness-multibranch → Scan Multibranch Pipeline Log`
2. Verify Jenkinsfile exists in branch
3. Check branch regex filter includes your branch
4. Check GitHub credentials are valid

**Force scan:**
```
aceest-fitness-multibranch → Scan Multibranch Pipeline Now
```

### Pull Request Builds Not Working

**Enable PR discovery:**
1. Multi-branch job → Configure
2. Branch Sources → Behaviors
3. Add → **Discover pull requests from origin**
4. Strategy: **Merging the pull request with current target branch revision**
5. Save and scan

### Authentication Issues

**GitHub API rate limits:**
- Anonymous: 60 requests/hour
- Authenticated: 5,000 requests/hour

**Solution**: Always use GitHub token for authentication.

**Check rate limit:**
```bash
curl -H "Authorization: token ghp_your_token" https://api.github.com/rate_limit
```

---

## 📈 Monitoring & Notifications

### Email Notifications

Add to Jenkinsfile:
```groovy
post {
    success {
        emailext (
            subject: "✅ Build Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: "Branch: ${env.BRANCH_NAME}\nCommit: ${env.GIT_COMMIT}",
            to: 'team@example.com'
        )
    }
    failure {
        emailext (
            subject: "❌ Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: "Branch: ${env.BRANCH_NAME}\nCommit: ${env.GIT_COMMIT}",
            to: 'team@example.com'
        )
    }
}
```

### Slack Notifications

```groovy
post {
    always {
        slackSend (
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
            message: "${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME}"
        )
    }
}
```

### GitHub Status Checks

Automatic with GitHub Branch Source plugin:
- ✅ Shows build status on commits
- ✅ Blocks PR merge if build fails (configurable in GitHub)
- ✅ Shows Jenkins logs link

---

## 📝 Example Repository Structure

```
aceest-fitness/
├── .github/
│   └── workflows/
│       └── notify-jenkins.yml      # GitHub Actions fallback
├── Jenkinsfile                     # Main pipeline (auto-detected)
├── kube_manifests/                 # Kubernetes manifests
├── tests/                          # Pytest tests
├── app/                            # Flask application
└── README.md
```

**All branches with `Jenkinsfile` are auto-built!**

---

## ✅ Success Checklist

- [ ] GitHub Personal Access Token created
- [ ] Jenkins credentials configured (`github-token`)
- [ ] Multi-branch pipeline job created
- [ ] Branch source configured (GitHub repo URL)
- [ ] Branch discovery enabled (all branches + PRs)
- [ ] Scan triggers configured (webhook + periodic)
- [ ] GitHub webhook created (or GitHub Actions workflow)
- [ ] Webhook tested (push commit)
- [ ] Branch appears in Jenkins
- [ ] Build triggers automatically
- [ ] Pull request builds work
- [ ] GitHub shows commit status

---

## 🎉 You're All Set!

Now your Jenkins Multi-branch pipeline will:
- ✅ **Auto-discover** all branches
- ✅ **Auto-build** on every push
- ✅ **Test pull requests** automatically
- ✅ **Show status** on GitHub commits/PRs
- ✅ **Deploy** based on branch strategy
- ✅ **Clean up** old branches

**Works perfectly with personal GitHub accounts!** 🚀

---

## 📚 Additional Resources

- [Jenkins Multi-branch Pipeline](https://www.jenkins.io/doc/book/pipeline/multibranch/)
- [GitHub Branch Source Plugin](https://plugins.jenkins.io/github-branch-source/)
- [GitHub Webhooks](https://docs.github.com/en/webhooks)
- [Jenkinsfile Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)

---

**Questions?** Check troubleshooting section or Jenkins/GitHub documentation.
