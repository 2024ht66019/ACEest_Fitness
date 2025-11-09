# AKS-Specific Configuration Guide

## Azure Kubernetes Service (AKS) Compatibility

All manifests have been configured for AKS deployment. This guide covers AKS-specific configurations.

---

## 🔧 AKS-Specific Components

### 1. Storage Classes

**Azure Disk (managed-csi)** - Used for PostgreSQL persistent storage
```yaml
storageClassName: managed-csi
```

**Available AKS Storage Classes:**
- `managed-csi` - Azure Disk CSI (default, recommended)
- `managed-csi-premium` - Premium SSD
- `azurefile-csi` - Azure Files (for ReadWriteMany)
- `azurefile-csi-premium` - Premium Azure Files

**Check available storage classes:**
```bash
kubectl get storageclass
```

**Change storage class if needed:**
```bash
# Edit postgres statefulset
kubectl edit statefulset postgres -n aceest-fitness
```

---

### 2. Ingress Controllers

**Two options for AKS:**

#### Option A: Azure Application Gateway Ingress Controller (AGIC)
Already configured in `07-ingress.yaml` as default:
```yaml
ingressClassName: azure-application-gateway
annotations:
  kubernetes.io/ingress.class: azure/application-gateway
```

**Enable AGIC in AKS:**
```bash
# Enable AGIC addon
az aks enable-addons \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --addons ingress-appgw \
  --appgw-name <appgw-name> \
  --appgw-subnet-cidr "10.225.0.0/16"
```

#### Option B: Nginx Ingress Controller
For A/B testing and canary features:
```bash
# Install Nginx Ingress on AKS
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
```

**Switch to Nginx:**
```yaml
# Uncomment nginx lines in 07-ingress.yaml
ingressClassName: nginx
kubernetes.io/ingress.class: nginx
```

---

### 3. Load Balancer

AKS automatically provisions Azure Load Balancer for `type: LoadBalancer` services.

**Service configuration:**
```yaml
spec:
  type: LoadBalancer
  # Azure-specific annotations (optional)
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "false"  # Public LB
    service.beta.kubernetes.io/azure-load-balancer-resource-group: "<rg-name>"
```

**Get external IP:**
```bash
kubectl get service aceest-web-service -n aceest-fitness
# Wait for EXTERNAL-IP to be assigned (may take 2-3 minutes)
```

---

### 4. Azure CNI Networking

AKS uses Azure CNI by default. Network policies are supported.

**Network policies are enabled** in `06-network-policies.yaml`.

**Verify CNI:**
```bash
az aks show --resource-group <rg> --name <cluster> --query networkProfile
```

---

### 5. Managed Identity

AKS uses managed identities for Azure resource access.

**For Azure Container Registry (ACR) integration:**
```bash
# Attach ACR to AKS cluster
az aks update \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --attach-acr <acr-name>
```

This eliminates need for image pull secrets.

---

## 🚀 AKS Deployment Steps

### Prerequisites

1. **AKS Cluster** (already provisioned via Terraform)
```bash
# Verify cluster access
az aks get-credentials \
  --resource-group <resource-group> \
  --name <aks-cluster>

kubectl get nodes
```

2. **ACR Access** (if using Azure Container Registry)
```bash
# Login to ACR
az acr login --name <acr-name>

# Tag and push image
docker tag dharmalakshmi15/aceest-fitness-gym:latest <acr-name>.azurecr.io/aceest-fitness-gym:latest
docker push <acr-name>.azurecr.io/aceest-fitness-gym:latest
```

3. **Update image references** in manifests:
```bash
# Replace dockerhub image with ACR image
find strategies/ -name "deployment.yaml" -exec sed -i \
  's|dharmalakshmi15/aceest-fitness-gym|<acr-name>.azurecr.io/aceest-fitness-gym|g' {} +
```

### Deploy to AKS

```bash
# 1. Deploy base infrastructure
./deploy.sh all deploy

# 2. Verify PostgreSQL is running
kubectl get statefulset postgres -n aceest-fitness
kubectl get pvc -n aceest-fitness  # Check Azure disk is bound

# 3. Deploy application (choose strategy)
./deploy.sh rolling-update deploy

# 4. Get external IP (wait 2-3 minutes)
kubectl get service aceest-web-service -n aceest-fitness -w

# 5. Access application
curl http://<EXTERNAL-IP>
```

---

## 🔍 AKS-Specific Monitoring

### Azure Monitor for Containers

**Enable container insights:**
```bash
az aks enable-addons \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --addons monitoring
```

**View logs in Azure Portal:**
```
Portal → AKS Cluster → Logs → Container Logs
```

### Metrics Server (for HPA)

**Verify metrics server:**
```bash
kubectl get deployment metrics-server -n kube-system
```

**If not installed:**
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Test HPA:**
```bash
kubectl get hpa -n aceest-fitness
kubectl top pods -n aceest-fitness
```

---

## 🔐 AKS Security

### Azure Policy

**Enable Azure Policy addon:**
```bash
az aks enable-addons \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --addons azure-policy
```

### Secrets Management

**Option 1: Azure Key Vault (Recommended)**
```bash
# Enable Key Vault addon
az aks enable-addons \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --addons azure-keyvault-secrets-provider
```

Then create SecretProviderClass to sync secrets from Key Vault.

**Option 2: Kubernetes Secrets** (current implementation)
Already configured in `02-secrets.yaml`.

⚠️ **Important:** Update secrets before production deployment:
```bash
kubectl create secret generic aceest-secrets \
  --from-literal=SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -base64 32)" \
  --from-literal=DATABASE_URL="postgresql://aceest_user:<password>@postgres-service:5432/aceest_fitness" \
  -n aceest-fitness \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## 📊 AKS Resource Limits

### Node Pool Configuration

**Check node resources:**
```bash
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**Our resource requests per pod:**
- CPU: 250m (0.25 cores)
- Memory: 256Mi

**Maximum pods per node:**
- Standard_DS2_v2: ~30 pods
- Standard_DS3_v2: ~110 pods
- Standard_D4s_v3: ~110 pods

### Cluster Autoscaler

**Enable cluster autoscaler:**
```bash
az aks update \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 5
```

Works with our HPA configuration (3-10 pods).

---

## 🌐 DNS and Custom Domains

### Azure DNS Zone

**Create DNS record for ingress:**
```bash
# Get ingress external IP
INGRESS_IP=$(kubectl get ingress aceest-web-ingress -n aceest-fitness -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create A record in Azure DNS
az network dns record-set a add-record \
  --resource-group <dns-rg> \
  --zone-name <your-domain.com> \
  --record-set-name aceest-fitness \
  --ipv4-address $INGRESS_IP
```

**Update ingress manifest:**
```yaml
spec:
  rules:
  - host: aceest-fitness.your-domain.com  # Update this
```

### SSL/TLS with cert-manager

**Install cert-manager:**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml
```

**Create Let's Encrypt issuer:**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Ingress already configured with cert-manager annotation.

---

## 🔧 Troubleshooting AKS

### Storage Issues

**PVC pending:**
```bash
kubectl describe pvc postgres-storage-postgres-0 -n aceest-fitness

# Check if storageClassName exists
kubectl get storageclass
```

**Solution:**
```bash
# Use different storage class
kubectl patch pvc postgres-storage-postgres-0 -n aceest-fitness \
  -p '{"spec":{"storageClassName":"managed-csi-premium"}}'
```

### Load Balancer Issues

**Service stuck in Pending:**
```bash
kubectl describe service aceest-web-service -n aceest-fitness
```

**Check AKS permissions:**
```bash
# Verify AKS has permission to create LB
az aks show --resource-group <rg> --name <cluster> --query identity
```

### Image Pull Issues

**If using ACR:**
```bash
# Verify ACR attachment
az aks show --resource-group <rg> --name <cluster> --query acrProfile

# Reattach if needed
az aks update --resource-group <rg> --name <cluster> --attach-acr <acr-name>
```

### Node Issues

**Check node status:**
```bash
kubectl get nodes
kubectl describe node <node-name>
```

**Scale node pool:**
```bash
az aks scale \
  --resource-group <resource-group> \
  --name <aks-cluster> \
  --node-count 3
```

---

## 📝 AKS Best Practices Implemented

✅ **Azure Disk CSI** for persistent storage  
✅ **Azure Load Balancer** integration  
✅ **Network Policies** for pod security  
✅ **Resource Quotas** to prevent resource exhaustion  
✅ **HPA** for automatic scaling  
✅ **Health Checks** (liveness & readiness)  
✅ **Init Containers** for database initialization  
✅ **Non-root containers** for security  
✅ **Multiple deployment strategies** for flexibility  

---

## 🔗 Additional Resources

- [AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Azure Application Gateway Ingress Controller](https://docs.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)
- [AKS Storage Options](https://docs.microsoft.com/en-us/azure/aks/concepts-storage)
- [AKS Networking](https://docs.microsoft.com/en-us/azure/aks/concepts-network)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)

---

**Status:** ✅ Manifests optimized for AKS  
**Storage:** Azure Disk (managed-csi)  
**Ingress:** Azure Application Gateway / Nginx  
**Load Balancer:** Azure Load Balancer
