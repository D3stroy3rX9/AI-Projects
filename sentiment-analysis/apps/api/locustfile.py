"""
Load testing with Locust

Run with:
  locust -f locustfile.py --host=http://localhost:8000

Or headless:
  locust -f locustfile.py --host=http://localhost:8000 --headless --users 100 --spawn-rate 10 --run-time 60s
"""

from locust import HttpUser, task, between, tag
import random
import json


# Sample texts for testing
POSITIVE_TEXTS = [
    "This product is absolutely fantastic! Exceeded all my expectations.",
    "I'm so happy with this purchase. Best decision ever!",
    "Amazing quality and great customer service. Highly recommended!",
    "Love it! Works perfectly and arrived quickly.",
    "Excellent experience from start to finish. Will buy again!",
]

NEUTRAL_TEXTS = [
    "The product arrived on time as expected.",
    "It's okay, nothing special but does the job.",
    "Average quality, meets basic requirements.",
    "Delivered as described. No complaints.",
    "Standard product, no surprises good or bad.",
]

NEGATIVE_TEXTS = [
    "Terrible experience. Would not recommend to anyone.",
    "Very disappointed with the quality. Complete waste of money.",
    "Poor customer service and defective product.",
    "Broke after one use. Total disappointment.",
    "Horrible! Nothing like the description.",
]

ALL_TEXTS = POSITIVE_TEXTS + NEUTRAL_TEXTS + NEGATIVE_TEXTS


class SentimentAnalysisUser(HttpUser):
    """Simulated user for sentiment analysis API"""

    # Wait 1-5 seconds between tasks
    wait_time = between(1, 5)

    def on_start(self):
        """Called when user starts"""
        # Health check to ensure API is up
        self.client.get("/health")

    @task(10)
    @tag('analyze')
    def analyze_single_text(self):
        """Analyze a single text (most common operation)"""
        text = random.choice(ALL_TEXTS)

        with self.client.post(
            "/analyze",
            json={
                "text": text,
                "include_emotions": random.choice([True, False]),
                "include_explanation": False
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Validate response structure
                if "sentiment" in data and "predicted_label" in data:
                    response.success()
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(3)
    @tag('analyze', 'batch')
    def analyze_batch_small(self):
        """Analyze a small batch (10 texts)"""
        texts = [random.choice(ALL_TEXTS) for _ in range(10)]

        with self.client.post(
            "/analyze/batch",
            json={
                "texts": texts,
                "source": "api"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("total_count") == 10:
                    response.success()
                else:
                    response.failure("Incorrect batch count")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    @tag('analyze', 'batch', 'large')
    def analyze_batch_large(self):
        """Analyze a larger batch (100 texts)"""
        texts = [random.choice(ALL_TEXTS) for _ in range(100)]

        with self.client.post(
            "/analyze/batch",
            json={
                "texts": texts,
                "source": "api"
            },
            catch_response=True,
            timeout=30  # Longer timeout for large batch
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data:
                    response.success()
                else:
                    response.failure("Missing total_count")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(2)
    @tag('analytics')
    def get_trends(self):
        """Get sentiment trends"""
        time_range = random.choice([
            "LAST_24_HOURS",
            "LAST_7_DAYS",
            "LAST_30_DAYS"
        ])

        with self.client.get(
            f"/analytics/trends?time_range={time_range}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "data_points" in data:
                    response.success()
                else:
                    response.failure("Missing data_points")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(2)
    @tag('analytics')
    def get_summary(self):
        """Get analytics summary"""
        with self.client.get(
            "/analytics/summary",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "total_analyzed" in data and "sentiment_distribution" in data:
                    response.success()
                else:
                    response.failure("Invalid summary structure")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    @tag('models')
    def list_models(self):
        """List available models"""
        with self.client.get(
            "/models",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    response.success()
                else:
                    response.failure("Missing models list")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    @tag('models')
    def get_active_model(self):
        """Get active model info"""
        with self.client.get(
            "/models/active",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:  # 404 if no active model
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    @tag('training')
    def list_training_data(self):
        """List training data"""
        skip = random.randint(0, 100)
        limit = random.choice([10, 20, 50])

        with self.client.get(
            f"/training-data?skip={skip}&limit={limit}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data:
                    response.success()
                else:
                    response.failure("Invalid training data response")
            else:
                response.failure(f"Got status {response.status_code}")


class HighLoadUser(HttpUser):
    """User for high-load testing (only analyze endpoints)"""

    wait_time = between(0.1, 0.5)  # Much shorter wait time

    @task(20)
    @tag('analyze', 'stress')
    def rapid_analyze(self):
        """Rapid single text analysis"""
        text = random.choice(ALL_TEXTS)

        self.client.post(
            "/analyze",
            json={"text": text},
            timeout=5
        )

    @task(1)
    @tag('analyze', 'batch', 'stress')
    def rapid_batch_analyze(self):
        """Rapid batch analysis"""
        texts = [random.choice(ALL_TEXTS) for _ in range(50)]

        self.client.post(
            "/analyze/batch",
            json={"texts": texts, "source": "api"},
            timeout=15
        )


class ReadOnlyUser(HttpUser):
    """User that only reads data (no writes)"""

    wait_time = between(0.5, 2)

    @task(5)
    @tag('analytics', 'readonly')
    def get_trends(self):
        """Get trends data"""
        self.client.get("/analytics/trends?time_range=LAST_7_DAYS")

    @task(3)
    @tag('analytics', 'readonly')
    def get_summary(self):
        """Get summary"""
        self.client.get("/analytics/summary")

    @task(2)
    @tag('models', 'readonly')
    def list_models(self):
        """List models"""
        self.client.get("/models")

    @task(1)
    @tag('training', 'readonly')
    def list_training_data(self):
        """List training data"""
        self.client.get("/training-data?skip=0&limit=20")


# Custom load shapes for different scenarios
from locust import LoadTestShape


class StepLoadShape(LoadTestShape):
    """
    Step load pattern: gradually increase load in steps

    Step 1: 10 users for 1 minute
    Step 2: 50 users for 1 minute
    Step 3: 100 users for 1 minute
    Step 4: 200 users for 1 minute
    """

    step_time = 60  # Seconds per step
    step_load = 10  # Initial users
    spawn_rate = 10
    time_limit = 240  # Total 4 minutes

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = run_time // self.step_time
        users = self.step_load * (2 ** current_step)  # Exponential growth

        return (users, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load pattern: sudden spikes in traffic

    Normal: 20 users
    Spike: 200 users for 30 seconds every 2 minutes
    """

    def tick(self):
        run_time = self.get_run_time()

        if run_time > 600:  # 10 minutes total
            return None

        # Spike every 120 seconds for 30 seconds
        cycle_time = run_time % 120

        if cycle_time < 30:
            return (200, 50)  # Spike
        else:
            return (20, 10)  # Normal load
