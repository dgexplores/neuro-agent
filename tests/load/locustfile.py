"""
Locust Load Testing Script for NeuroAgent API

Phase 8-1: Performance Testing
Target: 100 concurrent users, p95 < 2 seconds

Usage:
    locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
"""

from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import json
import random
import time
from datetime import datetime

from test_data_generator import (
    generate_diagnosis_payload,
    generate_drug_interaction_payload,
    generate_image_file,
    AUTH_TOKEN
)


class NeuroAgentUser(FastHttpUser):
    """
    Simulated user for NeuroAgent API load testing

    Task Distribution:
    - 60% diagnosis requests (most common)
    - 30% drug interaction checks
    - 10% image uploads
    """

    wait_time = between(2, 5)  # Wait 2-5 seconds between requests

    def on_start(self):
        """Initialize user session"""
        self.auth_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        self.request_count = 0
        self.slow_requests = []

    @task(6)  # 60% weight
    def submit_diagnosis(self):
        """
        Test POST /api/v1/diagnosis endpoint

        Performance target: p95 < 2000ms
        """
        payload = generate_diagnosis_payload()

        start_time = time.time()

        with self.client.post(
            "/api/v1/diagnosis",
            json=payload,
            headers=self.auth_headers,
            catch_response=True,
            name="POST /api/v1/diagnosis"
        ) as response:
            elapsed_ms = (time.time() - start_time) * 1000

            # Check response status
            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
                return

            # Check response time
            if elapsed_ms > 2000:
                self.slow_requests.append({
                    "endpoint": "diagnosis",
                    "elapsed_ms": elapsed_ms,
                    "timestamp": datetime.now().isoformat()
                })
                response.failure(f"Response too slow: {elapsed_ms:.0f}ms > 2000ms")
                return

            # Validate response structure
            try:
                data = response.json()
                required_fields = ["case_id", "diagnosis", "confidence", "recommendations"]
                if not all(field in data for field in required_fields):
                    response.failure("Missing required fields in response")
                    return

                response.success()
            except json.JSONDecodeError:
                response.failure("Invalid JSON response")

    @task(3)  # 30% weight
    def check_drug_interactions(self):
        """
        Test POST /api/v1/drug-interactions endpoint

        Performance target: p95 < 500ms (lighter endpoint)
        """
        payload = generate_drug_interaction_payload()

        start_time = time.time()

        with self.client.post(
            "/api/v1/drug-interactions",
            json=payload,
            headers=self.auth_headers,
            catch_response=True,
            name="POST /api/v1/drug-interactions"
        ) as response:
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
                return

            if elapsed_ms > 500:
                response.failure(f"Response too slow: {elapsed_ms:.0f}ms > 500ms")
                return

            try:
                data = response.json()
                if "interactions" not in data:
                    response.failure("Missing interactions in response")
                    return

                response.success()
            except json.JSONDecodeError:
                response.failure("Invalid JSON response")

    @task(1)  # 10% weight
    def upload_image(self):
        """
        Test POST /api/v1/upload-image endpoint

        Performance target: p95 < 3000ms (image processing is slower)
        """
        image_file = generate_image_file()

        start_time = time.time()

        with self.client.post(
            "/api/v1/upload-image",
            files={"file": ("test_brain_mri.jpg", image_file, "image/jpeg")},
            headers=self.auth_headers,
            catch_response=True,
            name="POST /api/v1/upload-image"
        ) as response:
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
                return

            if elapsed_ms > 3000:
                response.failure(f"Response too slow: {elapsed_ms:.0f}ms > 3000ms")
                return

            try:
                data = response.json()
                if "image_id" not in data:
                    response.failure("Missing image_id in response")
                    return

                response.success()
            except json.JSONDecodeError:
                response.failure("Invalid JSON response")

    @task(1)  # 10% weight - health check
    def health_check(self):
        """Test GET /health endpoint (should be very fast)"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
            else:
                response.success()


class SpikeTestUser(FastHttpUser):
    """
    User class for spike testing

    Simulates sudden traffic spike to test system stability
    """

    wait_time = between(1, 2)  # Aggressive request rate

    def on_start(self):
        self.auth_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    @task
    def rapid_diagnosis_requests(self):
        """Rapid-fire diagnosis requests"""
        payload = generate_diagnosis_payload()

        with self.client.post(
            "/api/v1/diagnosis",
            json=payload,
            headers=self.auth_headers,
            catch_response=True,
            name="SPIKE /api/v1/diagnosis"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed during spike: {response.status_code}")
            else:
                response.success()


# Event hooks for custom reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    print("\n" + "="*80)
    print("🚀 NeuroAgent Load Test Starting")
    print(f"Target: {environment.parsed_options.num_users} users")
    print(f"Spawn rate: {environment.parsed_options.spawn_rate} users/s")
    print(f"Host: {environment.host}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate final report"""
    print("\n" + "="*80)
    print("📊 NeuroAgent Load Test Complete")
    print("="*80)

    # Get statistics
    stats = environment.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    avg_response_time = stats.total.avg_response_time
    p95_response_time = stats.total.get_response_time_percentile(0.95)
    p99_response_time = stats.total.get_response_time_percentile(0.99)
    rps = stats.total.total_rps

    print(f"\n📈 Performance Metrics:")
    print(f"   Total Requests: {total_requests}")
    print(f"   Failed Requests: {total_failures} ({(total_failures/total_requests*100):.2f}%)")
    print(f"   Requests/Second: {rps:.2f}")
    print(f"   Average Response Time: {avg_response_time:.0f}ms")
    print(f"   p95 Response Time: {p95_response_time:.0f}ms")
    print(f"   p99 Response Time: {p99_response_time:.0f}ms")

    # Check performance targets
    print(f"\n✅ Performance Target Analysis:")
    target_met = p95_response_time < 2000
    status = "✅ PASS" if target_met else "❌ FAIL"
    print(f"   p95 < 2000ms: {status} (actual: {p95_response_time:.0f}ms)")

    error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0
    error_target_met = error_rate < 1.0
    error_status = "✅ PASS" if error_target_met else "❌ FAIL"
    print(f"   Error Rate < 1%: {error_status} (actual: {error_rate:.2f}%)")

    rps_target_met = rps >= 50
    rps_status = "✅ PASS" if rps_target_met else "❌ FAIL"
    print(f"   Throughput ≥ 50 req/s: {rps_status} (actual: {rps:.2f} req/s)")

    print("\n" + "="*80 + "\n")


# Custom test scenarios
class ConstantLoadScenario(HttpUser):
    """
    Constant load scenario for endurance testing

    Maintains consistent load over extended period
    """
    wait_time = between(5, 10)
    auth_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    @task
    def constant_diagnosis_load(self):
        """Steady diagnosis requests"""
        payload = generate_diagnosis_payload()
        self.client.post(
            "/api/v1/diagnosis",
            json=payload,
            headers=self.auth_headers
        )


if __name__ == "__main__":
    print("""
    NeuroAgent Load Testing Script

    Run with:
        locust -f locustfile.py --host=http://localhost:8000

    Test Scenarios:
    1. Standard Load Test:
       locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 5m

    2. Spike Test:
       locust -f locustfile.py --users 200 --spawn-rate 50 --run-time 2m

    3. Endurance Test:
       locust -f locustfile.py --users 50 --spawn-rate 5 --run-time 30m

    Performance Targets:
    - p95 response time < 2 seconds
    - Error rate < 1%
    - Throughput ≥ 50 req/s
    """)
