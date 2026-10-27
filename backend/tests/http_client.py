"""HTTP integration harness using the production ASGI server on loopback only.

Provider mocks remain in the same process as the application. Using real HTTP
avoids coupling endpoint contracts to Starlette's blocking test-client bridge.
"""
from contextlib import contextmanager
import socket
import threading
import time

import httpx
import uvicorn


@contextmanager
def api_client(app):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(
        app, host="127.0.0.1", port=port, loop="asyncio",
        lifespan="on", log_level="warning", access_log=False,
        timeout_graceful_shutdown=2,
    ))
    worker = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    worker.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started:
            if not worker.is_alive() or time.monotonic() >= deadline:
                raise RuntimeError("The loopback API test server did not start")
            time.sleep(0.01)
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False) as client:
            yield client
    finally:
        server.should_exit = True
        worker.join(timeout=5)
        listener.close()
        if worker.is_alive():
            raise RuntimeError("The loopback API test server did not stop")
