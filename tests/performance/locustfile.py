from locust import HttpUser, task, between

class CommanderAPIUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def check_health(self):
        self.client.get("/api/health")

    @task(3)
    def inject_crisis(self):
        payload = {
            "query": "Simulated load test crisis payload.",
            "priority": "HIGH"
        }
        self.client.post("/api/crisis/report", json=payload)
