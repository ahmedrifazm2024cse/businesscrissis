# Agentverse Enterprise Deployment Guide

## Prerequisites
- Docker Engine 24+
- Docker Compose v2+
- 16GB RAM minimum (24 containers will be launched)

## 1. Environment Configuration
Create a `.env` file in the root directory:
```env
ENV=production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=super_secret
JWT_SECRET_KEY=generate-a-secure-random-key
```

## 2. Running Locally with Docker Compose
To launch the entire platform:
```bash
# Windows
.\deployment\scripts\start-prod.ps1

# Linux/Mac
cd deployment/docker
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 3. Kubernetes Deployment (Cloud Native)
If deploying to EKS, AKS, or GKE, use the provided YAML manifests.
```bash
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/secret.yaml
kubectl apply -f deployment/kubernetes/services.yaml
kubectl apply -f deployment/kubernetes/deployments.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml
```

## 4. Verification
Run the health check script to ensure all 24 services are online:
```bash
.\deployment\scripts\health-check.ps1
```
