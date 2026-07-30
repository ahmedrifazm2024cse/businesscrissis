# Agentverse Operations & Troubleshooting Manual

## 1. Centralized Logging
By default, Docker Compose routes all container logs to stdout. To view logs for a specific agent:
```bash
docker compose logs -f customer-agent
docker compose logs -f commander
```
In a production Kubernetes cluster, it is highly recommended to deploy a Fluentd/Elasticsearch/Kibana (ELK) stack to aggregate logs.

## 2. Scaling Agents
The platform is designed as a stateless 12-Factor App. To scale the Commander API Gateway or any specific Business Agent under heavy load:
```bash
docker compose up -d --scale commander=3 --scale market-agent=2
```
In Kubernetes, adjust the `replicas` field in the deployment manifest or configure the HorizontalPodAutoscaler (HPA).

## 3. Backups
**PostgreSQL Database:**
To backup the persistent state (Memory, Audit logs, Analytics):
```bash
docker exec -t <postgres_container_id> pg_dumpall -c -U postgres > dump_$(date +%Y-%m-%d).sql
```

## 4. Troubleshooting
**Symptom:** UI cannot connect to WebSocket (EventBus monitor blank).
**Fix:** Verify that the NGINX configuration (`deployment/nginx/nginx.conf`) has `proxy_set_header Upgrade $http_upgrade` configured properly and that the `commander` service is running.

**Symptom:** Agent responds with 401 Unauthorized.
**Fix:** Ensure the JWT token matches the `JWT_SECRET_KEY` defined in the `.env` or Kubernetes `secret.yaml`.
