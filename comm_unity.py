# comm_unity.py
import json
import time
from websocket import create_connection, WebSocketTimeoutException, WebSocketConnectionClosedException

class UnityComm:
    def __init__(self, url="ws://localhost:8765", timeout=10, retries=2, retry_delay=1.0):
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
            except Exception as e:
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

    def send_individual(self, generation, idx, genes):
        if self.ws is None:
            raise RuntimeError("WebSocket not connected")
        msg = {
            "type": "evaluate",
            "generation": int(generation),
            "id": int(idx),
            "genes": [float(x) for x in genes]
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

    def send_evaluate_done(self, generation, pop_size):
        """
        Informa o servidor que já enviámos todos os 'evaluate' para a geração.
        O servidor mock usa isto para saber quando enviar o batch.
        """
        if self.ws is None:
            raise RuntimeError("WebSocket not connected")
        msg = {"type": "evaluate_done", "generation": int(generation), "pop_size": int(pop_size)}
        payload = json.dumps(msg)
        try:
            self.ws.send(payload)
        except Exception:
            # tenta reconectar e reenviar
            try:
                self.connect()
                self.ws.send(payload)
            except Exception:
                raise

    def receive_result(self, timeout=None):
        """
        Recebe a próxima mensagem JSON do servidor e devolve o dicionário.
        Pode ser um 'result' individual ou um 'results_batch'.
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
                data = json.loads(raw)
                return data
            except WebSocketTimeoutException:
                raise TimeoutError("Timeout waiting for Unity result")
            except Exception:
                time.sleep(0.01)
            if time.time() - start > timeout:
                raise TimeoutError("Timeout waiting for Unity result")
