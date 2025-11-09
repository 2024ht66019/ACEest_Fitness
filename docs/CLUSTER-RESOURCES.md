# Cluster Resource Optimization

## Cluster Specifications

**Infrastructure:**
- **Nodes**: 2
- **CPU per node**: 2 cores
- **RAM per node**: 4 GiB
- **Total capacity**: 4 CPU cores, 8 GiB RAM

**Available for workloads (after system overhead ~20%):**
- **CPU**: ~3.2 cores
- **RAM**: ~6.4 GiB

---

## Resource Allocation Per Deployment Strategy

### Per-Pod Resources

Each application pod requests:
- **CPU**: 250m (0.25 cores)
- **Memory**: 256 MiB
- **CPU Limit**: 500m (0.5 cores)
- **Memory Limit**: 512 MiB

PostgreSQL pod:
- **CPU**: 250m (0.25 cores)
- **Memory**: 256 MiB
- **CPU Limit**: 1000m (1 core)
- **Memory Limit**: 1 GiB

---

## Strategy Resource Requirements (Optimized)

### 1. 🔄 Rolling Update (Lowest Resources)
**Replicas**: 2 + 1 surge during updates
**Total during update**: 3 app pods + 1 PostgreSQL

| Component | Pods | CPU Request | Memory Request |
|-----------|------|-------------|----------------|
| Application | 3 | 750m | 768 MiB |
| PostgreSQL | 1 | 250m | 256 MiB |
| **TOTAL** | **4** | **1000m (1 core)** | **1024 MiB (1 GiB)** |

✅ **Fits cluster**: Yes  
✅ **Recommended for**: Feature branches, dev environment

---

### 2. 🕯️ Canary (Low Resources)
**Replicas**: 2 stable + 1 canary
**Total**: 3 app pods + 1 PostgreSQL

| Component | Pods | CPU Request | Memory Request |
|-----------|------|-------------|----------------|
| Stable | 2 | 500m | 512 MiB |
| Canary | 1 | 250m | 256 MiB |
| PostgreSQL | 1 | 250m | 256 MiB |
| **TOTAL** | **4** | **1000m (1 core)** | **1024 MiB (1 GiB)** |

✅ **Fits cluster**: Yes  
✅ **Recommended for**: Develop branch, staging environment

---

### 3. 🔵🟢 Blue-Green (Medium Resources)
**Replicas**: 1 blue + 1 green (both running during deployment)
**Total**: 2 app pods + 1 PostgreSQL

| Component | Pods | CPU Request | Memory Request |
|-----------|------|-------------|----------------|
| Blue | 1 | 250m | 256 MiB |
| Green | 1 | 250m | 256 MiB |
| PostgreSQL | 1 | 250m | 256 MiB |
| **TOTAL** | **3** | **750m** | **768 MiB** |

✅ **Fits cluster**: Yes  
✅ **Recommended for**: Main/master branch, production environment  
⚠️ **Note**: Reduced to 1 replica per color (from 2) to fit cluster

---

### 4. 🔬 A/B Testing (Medium Resources)
**Replicas**: 1 variant-a + 1 variant-b
**Total**: 2 app pods + 1 PostgreSQL

| Component | Pods | CPU Request | Memory Request |
|-----------|------|-------------|----------------|
| Variant A | 1 | 250m | 256 MiB |
| Variant B | 1 | 250m | 256 MiB |
| PostgreSQL | 1 | 250m | 256 MiB |
| **TOTAL** | **3** | **750m** | **768 MiB** |

✅ **Fits cluster**: Yes  
✅ **Recommended for**: Experiments, feature comparison  
⚠️ **Note**: Reduced to 1 replica per variant (from 2) to fit cluster

---

### 5. 👤 Shadow (Higher Resources)
**Replicas**: 2 production + 2 shadow
**Total**: 4 app pods + 1 PostgreSQL

| Component | Pods | CPU Request | Memory Request |
|-----------|------|-------------|----------------|
| Production | 2 | 500m | 512 MiB |
| Shadow | 2 | 500m | 512 MiB |
| PostgreSQL | 1 | 250m | 256 MiB |
| **TOTAL** | **5** | **1250m (1.25 cores)** | **1280 MiB (1.25 GiB)** |

✅ **Fits cluster**: Yes  
⚠️ **Highest resource usage**  
⚠️ **Note**: Reduced to 2 replicas per version (from 3) to fit cluster  
✅ **Recommended for**: Performance testing, load comparison

---

## Resource Distribution Summary

```
┌─────────────────────┬──────────┬─────────────┬────────────────┬────────────┐
│ Strategy            │ App Pods │ CPU Request │ Memory Request │ Fits?      │
├─────────────────────┼──────────┼─────────────┼────────────────┼────────────┤
│ Rolling Update      │ 2-3      │ 1000m       │ 1024 MiB       │ ✅ Yes     │
│ Canary              │ 3        │ 1000m       │ 1024 MiB       │ ✅ Yes     │
│ Blue-Green          │ 2        │ 750m        │ 768 MiB        │ ✅ Yes     │
│ A/B Testing         │ 2        │ 750m        │ 768 MiB        │ ✅ Yes     │
│ Shadow              │ 4        │ 1250m       │ 1280 MiB       │ ✅ Yes     │
└─────────────────────┴──────────┴─────────────┴────────────────┴────────────┘
```

**All strategies fit within cluster capacity with optimized replica counts!**

---

## Optimizations Applied

### Before Optimization (Original)

| Strategy | Replicas | Total CPU | Total Memory | Fits 2-node? |
|----------|----------|-----------|--------------|--------------|
| Blue-Green | 2+2=4 | 1250m | 1280 MiB | ⚠️ Tight |
| Canary | 3+1=4 | 1250m | 1280 MiB | ⚠️ Tight |
| Shadow | 3+3=6 | 1750m | 1792 MiB | ❌ No |
| A/B Testing | 2+2=4 | 1250m | 1280 MiB | ⚠️ Tight |
| Rolling Update | 3+surge | 1250m | 1280 MiB | ⚠️ Tight |

### After Optimization (Current)

| Strategy | Replicas | Total CPU | Total Memory | Fits 2-node? |
|----------|----------|-----------|--------------|--------------|
| Blue-Green | 1+1=2 | 750m | 768 MiB | ✅ Yes |
| Canary | 2+1=3 | 1000m | 1024 MiB | ✅ Yes |
| Shadow | 2+2=4 | 1250m | 1280 MiB | ✅ Yes |
| A/B Testing | 1+1=2 | 750m | 768 MiB | ✅ Yes |
| Rolling Update | 2+surge | 1000m | 1024 MiB | ✅ Yes |

**All strategies now optimized for 2-node cluster!**

---

## Pod Distribution Across Nodes

Kubernetes will automatically distribute pods across both nodes for high availability:

### Example: Shadow Deployment (Highest Load)

```
Node 1 (2 CPU, 4 GiB):                Node 2 (2 CPU, 4 GiB):
┌──────────────────────┐              ┌──────────────────────┐
│ PostgreSQL           │              │ Production Pod #2    │
│ CPU: 250m            │              │ CPU: 250m            │
│ RAM: 256 MiB         │              │ RAM: 256 MiB         │
├──────────────────────┤              ├──────────────────────┤
│ Production Pod #1    │              │ Shadow Pod #2        │
│ CPU: 250m            │              │ CPU: 250m            │
│ RAM: 256 MiB         │              │ RAM: 256 MiB         │
├──────────────────────┤              ├──────────────────────┤
│ Shadow Pod #1        │              │ System Pods          │
│ CPU: 250m            │              │ (CoreDNS, etc.)      │
│ RAM: 256 MiB         │              │                      │
├──────────────────────┤              └──────────────────────┘
│ System Pods          │
│ (kube-proxy, etc.)   │
└──────────────────────┘

Total: ~750m CPU, ~768 MiB          Total: ~500m CPU, ~512 MiB
```

---

## High Availability Considerations

### Current Setup (2 nodes)
- ✅ Multiple replicas spread across nodes
- ✅ No single point of failure for app pods
- ⚠️ PostgreSQL runs on single node (acceptable for dev/staging)
- ⚠️ Some strategies use single replica (blue-green, a/b testing)

### Recommendations for Production (if scaling)

**Option 1: Increase Node Resources**
```yaml
# Upgrade to: 2 nodes × (4 CPU, 8 GiB)
# Allows:
- Blue-Green: 2+2=4 replicas
- Canary: 3+1=4 replicas
- Shadow: 3+3=6 replicas
- Better fault tolerance
```

**Option 2: Add More Nodes**
```yaml
# Scale to: 3 nodes × (2 CPU, 4 GiB)
# Allows:
- Better pod distribution
- True HA with replicas on separate nodes
- PostgreSQL replica (if configured)
```

**Option 3: Hybrid (Current + Spot Instances)**
```yaml
# 2 regular nodes + 1 spot node
# Use spot for non-critical workloads
# Cost-effective scaling
```

---

## Resource Monitoring

### Check Current Usage

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -n aceest-fitness

# Available resources
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### Expected Output

```
Node 1:
  CPU:    ~750m / 2000m  (37%)
  Memory: ~768Mi / 4Gi   (18%)

Node 2:
  CPU:    ~500m / 2000m  (25%)
  Memory: ~512Mi / 4Gi   (12%)
```

---

## Scaling Recommendations

### When to Scale Up

**Add nodes if:**
- CPU usage consistently > 70%
- Memory usage consistently > 75%
- Pods in Pending state due to insufficient resources
- Need higher replica counts for production HA

**Increase node size if:**
- Need to run resource-intensive workloads
- Want to reduce node count
- Need better per-pod performance

### Current Cluster is Sufficient For:

✅ **Development environment**  
✅ **Staging environment**  
✅ **Testing all deployment strategies**  
✅ **Low to medium traffic loads**  
✅ **Learning and experimentation**

### Consider Scaling For:

⚠️ **Production high-traffic workloads**  
⚠️ **Need for 3+ replicas per service**  
⚠️ **Running multiple applications**  
⚠️ **Database replication**  
⚠️ **Service mesh (Istio) overhead**

---

## Cost Optimization Tips

### Current Setup (Cost-Effective)

```yaml
Cluster: 2 nodes × (2 CPU, 4 GiB)
Cost: ~$70-100/month (depending on cloud provider)

✅ Suitable for:
- Development
- Staging
- Small production workloads
- CI/CD testing
```

### Keep Costs Low

1. **Use spot/preemptible instances** for non-critical nodes
2. **Auto-scale based on metrics** (HPA already configured)
3. **Right-size resource requests** (already optimized)
4. **Use resource quotas** (already configured)
5. **Monitor and adjust** based on actual usage

---

## Troubleshooting

### Pods Stuck in Pending

```bash
# Check why pod is pending
kubectl describe pod <pod-name> -n aceest-fitness

# Common causes:
# 1. Insufficient CPU/Memory
# 2. Node selector constraints
# 3. Persistent volume issues

# Solution: Check events
kubectl get events -n aceest-fitness --sort-by='.lastTimestamp'
```

### Out of Memory Issues

```bash
# Check pod memory usage
kubectl top pod <pod-name> -n aceest-fitness

# If approaching limits:
# 1. Check for memory leaks
# 2. Increase memory limits (if nodes can handle)
# 3. Optimize application code
```

### CPU Throttling

```bash
# Check if pods are being throttled
kubectl top pods -n aceest-fitness

# If CPU usage near limits:
# 1. Increase CPU requests/limits
# 2. Optimize application performance
# 3. Scale horizontally (more replicas)
```

---

## Summary

**Current Configuration:**
- ✅ All deployment strategies optimized for 2-node cluster
- ✅ Resource requests fit within available capacity
- ✅ High availability maintained where possible
- ✅ Room for growth and system overhead
- ✅ Cost-effective for dev/staging environments

**Next Steps:**
1. Monitor resource usage in real deployments
2. Adjust based on actual application behavior
3. Scale cluster if needed for production workloads
4. Consider implementing HPA for automatic scaling

**The cluster is ready for all deployment strategies! 🚀**
