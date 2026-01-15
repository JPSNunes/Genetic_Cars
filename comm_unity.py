# comm_unity.py
import json
import time
from websocket import (
    create_connection,
    WebSocketTimeoutException,
    WebSocketConnectionClosedException
)

class UnityComm:
    def __init__(self, url="ws://localhost:8080", timeout=10, retries=2, retry_delay=1.0):
        self.url = url
        self.timeout = timeout
        self.ws = None
        self.retries = retries
        self.retry_delay = retry_delay

    def connect(self):
        attempt = 0
        while attempt <= self.retries:
            try:
                self.ws = create_connection(self.url, timeout=self.timeout)
                return
            except Exception:
                attempt += 1
                if attempt > self.retries:
                    raise
                time.sleep(self.retry_delay)

    def close(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None

    # NEW: send full population at once
    def send_evaluate_batch(self, generation, population):
        """
        population: iterable of (id, genes)
        """
        if self.ws is None:
            raise RuntimeError("WebSocket not connected")

        msg = {
            "type": "evaluate_batch",
            "generation": int(generation),
            "population_size": len(population),
            "individuals": [
                {
                    "id": int(idx),
                    "genes": [float(x) for x in genes]
                }
                for idx, genes in population
            ]
        }

        payload = json.dumps(msg)

        attempt = 0
        while attempt <= self.retries:
            try:
                self.ws.send(payload)
                return
            except (WebSocketConnectionClosedException, Exception):
                attempt += 1
                try:
                    self.connect()
                except Exception:
                    if attempt > self.retries:
                        raise
                time.sleep(self.retry_delay)

    def receive_result(self, timeout=None):
        """
        Receives the next JSON message from Unity.
        Expected types:
          - fitness
          - results_batch
        """
        if self.ws is None:
            raise RuntimeError("WebSocket not connected")

        if timeout is None:
            timeout = self.timeout

        start = time.time()
        while True:
            try:
                raw = self.ws.recv()
                if not raw:
                    continue
                return json.loads(raw)

            except WebSocketTimeoutException:
                raise TimeoutError("Timeout waiting for Unity result")

            except Exception:
                time.sleep(0.01)

            if time.time() - start > timeout:
                raise TimeoutError("Timeout waiting for Unity result")
