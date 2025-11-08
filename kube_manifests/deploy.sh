#!/bin/bash
# Deployment script for ACEest Fitness Kubernetes manifests
# Usage: ./deploy.sh [strategy] [action]

set -e

NAMESPACE="aceest-fitness"
STRATEGIES=("rolling-update" "blue-green" "canary" "ab-testing" "shadow")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_usage() {
    echo -e "${BLUE}ACEest Fitness Kubernetes Deployment Script${NC}"
    echo ""
    echo "Usage: $0 [strategy] [action]"
    echo ""
    echo "Strategies:"
    echo "  rolling-update  - Standard rolling update deployment"
    echo "  blue-green      - Blue-green deployment"
    echo "  canary          - Canary release deployment"
    echo "  ab-testing      - A/B testing deployment"
    echo "  shadow          - Shadow deployment"
    echo "  all             - Deploy base infrastructure only"
    echo ""
    echo "Actions:"
    echo "  deploy          - Deploy the selected strategy"
    echo "  delete          - Delete the deployment"
    echo "  status          - Show deployment status"
    echo "  switch          - Switch traffic (blue-green only)"
    echo ""
    echo "Examples:"
    echo "  $0 rolling-update deploy"
    echo "  $0 blue-green deploy"
    echo "  $0 canary deploy"
    echo "  $0 all deploy          # Deploy base infrastructure"
}

deploy_base() {
    echo -e "${YELLOW}Deploying base infrastructure...${NC}"
    
    # Create namespace
    kubectl apply -f 00-namespace.yaml
    
    # Wait for namespace
    kubectl wait --for=jsonpath='{.status.phase}'=Active namespace/$NAMESPACE --timeout=60s
    
    # Deploy ConfigMap and Secrets
    kubectl apply -f 01-configmap.yaml
    kubectl apply -f 02-secrets.yaml
    
    # Deploy PostgreSQL
    kubectl apply -f 03-postgres-statefulset.yaml
    
    # Wait for PostgreSQL to be ready
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    
    # Deploy supporting resources
    kubectl apply -f 04-hpa.yaml 2>/dev/null || true
    kubectl apply -f 05-resource-quotas.yaml
    kubectl apply -f 06-network-policies.yaml
    kubectl apply -f 07-ingress.yaml 2>/dev/null || true
    
    echo -e "${GREEN}✓ Base infrastructure deployed successfully${NC}"
}

deploy_strategy() {
    local strategy=$1
    
    if [[ ! " ${STRATEGIES[@]} " =~ " ${strategy} " ]]; then
        echo -e "${RED}Error: Invalid strategy '${strategy}'${NC}"
        print_usage
        exit 1
    fi
    
    echo -e "${YELLOW}Deploying ${strategy} strategy...${NC}"
    
    # Deploy base if not exists
    if ! kubectl get namespace $NAMESPACE &>/dev/null; then
        deploy_base
    fi
    
    # Deploy strategy-specific manifests
    kubectl apply -f strategies/${strategy}/deployment.yaml
    
    echo -e "${GREEN}✓ ${strategy} strategy deployed${NC}"
    
    # Show status
    sleep 5
    show_status $strategy
}

delete_strategy() {
    local strategy=$1
    
    if [[ "$strategy" == "all" ]]; then
        echo -e "${RED}Deleting entire namespace...${NC}"
        read -p "Are you sure? This will delete all resources. (yes/no): " confirm
        if [[ "$confirm" == "yes" ]]; then
            kubectl delete namespace $NAMESPACE
            echo -e "${GREEN}✓ Namespace deleted${NC}"
        else
            echo "Cancelled"
        fi
        return
    fi
    
    echo -e "${YELLOW}Deleting ${strategy} deployment...${NC}"
    kubectl delete -f strategies/${strategy}/deployment.yaml --ignore-not-found=true
    echo -e "${GREEN}✓ ${strategy} deployment deleted${NC}"
}

show_status() {
    local strategy=$1
    
    echo -e "${BLUE}=== Deployment Status ===${NC}"
    echo ""
    
    echo -e "${GREEN}Namespace:${NC}"
    kubectl get namespace $NAMESPACE
    echo ""
    
    echo -e "${GREEN}Deployments:${NC}"
    kubectl get deployments -n $NAMESPACE
    echo ""
    
    echo -e "${GREEN}Pods:${NC}"
    kubectl get pods -n $NAMESPACE -o wide
    echo ""
    
    echo -e "${GREEN}Services:${NC}"
    kubectl get services -n $NAMESPACE
    echo ""
    
    if [[ -n "$strategy" ]] && [[ "$strategy" != "all" ]]; then
        echo -e "${GREEN}Strategy-specific resources (${strategy}):${NC}"
        kubectl get all -n $NAMESPACE -l strategy=${strategy}
    fi
}

switch_traffic() {
    local target=$1
    
    if [[ "$target" != "blue" ]] && [[ "$target" != "green" ]]; then
        echo -e "${RED}Error: Target must be 'blue' or 'green'${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Switching traffic to ${target}...${NC}"
    kubectl patch service aceest-web-service -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"version\":\"${target}\"}}}"
    echo -e "${GREEN}✓ Traffic switched to ${target}${NC}"
    
    # Show current status
    echo ""
    kubectl get service aceest-web-service -n $NAMESPACE -o yaml | grep -A 3 "selector:"
}

# Main script
if [[ $# -lt 2 ]]; then
    print_usage
    exit 1
fi

STRATEGY=$1
ACTION=$2

case "$ACTION" in
    deploy)
        if [[ "$STRATEGY" == "all" ]]; then
            deploy_base
        else
            deploy_strategy $STRATEGY
        fi
        ;;
    delete)
        delete_strategy $STRATEGY
        ;;
    status)
        show_status $STRATEGY
        ;;
    switch)
        if [[ "$STRATEGY" != "blue-green" ]]; then
            echo -e "${RED}Error: Switch action only available for blue-green strategy${NC}"
            exit 1
        fi
        if [[ -z "$3" ]]; then
            echo -e "${RED}Error: Please specify target (blue or green)${NC}"
            echo "Usage: $0 blue-green switch [blue|green]"
            exit 1
        fi
        switch_traffic $3
        ;;
    *)
        echo -e "${RED}Error: Invalid action '${ACTION}'${NC}"
        print_usage
        exit 1
        ;;
esac
