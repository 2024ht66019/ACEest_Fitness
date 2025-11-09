terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.109"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}

# Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-aks-demo"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "aks-demo-cluster"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 2
}

variable "vm_size" {
  description = "Size of the VMs in the node pool"
  type        = string
  default     = "Standard_D2s_v3"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# Networking Module
module "networking" {
  source = "./modules/networking"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  vnet_name          = "vnet-aks"
  address_space      = ["10.0.0.0/16"]
  subnet_name        = "subnet-aks"
  subnet_prefix      = ["10.0.1.0/24"]
}

# AKS Module
module "aks" {
  source = "./modules/aks"

  cluster_name        = var.cluster_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dns_prefix          = var.cluster_name
  node_count          = var.node_count
  vm_size             = var.vm_size
  subnet_id           = module.networking.subnet_id

  depends_on = [module.networking]
}

# Outputs
output "kube_config" {
  value     = module.aks.kube_config
  sensitive = true
}

output "cluster_id" {
  value = module.aks.cluster_id
}

output "cluster_fqdn" {
  value = module.aks.cluster_fqdn
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}