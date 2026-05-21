import os
import logging
from celery import shared_task
import httpx
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://api:8000")
@shared_task(bind=True)
def prime_endpoints(self, endpoints=None):
    """Hit a list of GET endpoints to warm caches.

    endpoints: list of path strings, e.g. ['/farms/summary']
    """
    if endpoints is None:
        endpoints = [
            "/farms/summary",
            "/farms/top",
            "/crops/yield-efficiency",
            "/crops/seasonal-trend",
            "/markets/price-comparison",
        ]

    results = {}
    with httpx.Client(timeout=10.0) as client:
        for path in endpoints:
            url = API_URL.rstrip("/") + path
            try:
                r = client.get(url)
                results[path] = {"status_code": r.status_code}
            except Exception as e:
                logger.exception("Error priming %s", url)
                results[path] = {"error": str(e)}

    return results
