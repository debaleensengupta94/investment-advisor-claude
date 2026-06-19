from locust import HttpUser, between, task


class InvestmentAdvisorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def recommend_low_short(self):
        self.client.post(
            "/tools/get_recommendation",
            json={
                "age": 40,
                "monthly_income": 60000,
                "monthly_savings": 10000,
                "risk": "LOW",
                "goal": "SHORT",
            },
        )

    @task(2)
    def recommend_medium_medium(self):
        self.client.post(
            "/tools/get_recommendation",
            json={
                "age": 32,
                "monthly_income": 75000,
                "monthly_savings": 15000,
                "risk": "MEDIUM",
                "goal": "MEDIUM",
            },
        )

    @task(1)
    def get_knowledge(self):
        self.client.post(
            "/tools/get_knowledge",
            json={"query": "mutual funds risk"},
        )

    @task(1)
    def health(self):
        self.client.get("/health")
