#!/usr/bin/env python3
"""Relay the authorized Odin screen feed over SSH to a loopback OBS media URL.

Capture starts when a viewer connects and stops after the last viewer leaves.
No video is saved. Slow viewers are disconnected rather than accumulating delay.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import queue
import selectors
import signal
import subprocess
import threading
import time


class Relay:
    def __init__(self, host):
        self.host = host
        self.clients = set()
        self.lock = threading.Lock()
        self.thread = None
        self.process = None
        self.stopping = threading.Event()
        self.bytes = 0
        state = Path.home() / ".local/state/odin-obs-stream"
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.log = state / "capture.log"

    def subscribe(self):
        client = queue.Queue(maxsize=96)
        with self.lock:
            self.clients.add(client)
            if self.thread is None:
                self.thread = threading.Thread(target=self.run, daemon=True)
                self.thread.start()
        return client

    def unsubscribe(self, client):
        with self.lock:
            self.clients.discard(client)

    def status(self):
        with self.lock:
            return {"viewers": len(self.clients), "capture_active": self.process is not None,
                    "bytes_relayed": self.bytes}

    @staticmethod
    def end(client):
        while True:
            try:
                client.get_nowait()
            except queue.Empty:
                break
        client.put_nowait(None)

    def run(self):
        proc = None
        try:
            with self.log.open("ab", buffering=0) as diagnostics:
                proc = subprocess.Popen([
                    "ssh", "-T", "-o", "Compression=no", self.host,
                    "systemd-run --user --quiet --wait --pipe --collect "
                    "--unit=odin-obs-capture /usr/local/bin/odin-obs-capture",
                ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=diagnostics)
                with self.lock:
                    self.process = proc
                selector = selectors.DefaultSelector()
                selector.register(proc.stdout, selectors.EVENT_READ)
                idle_since = None
                try:
                    while not self.stopping.is_set():
                        with self.lock:
                            has_viewers = bool(self.clients)
                        if has_viewers:
                            idle_since = None
                        elif idle_since is None:
                            idle_since = time.monotonic()
                        elif time.monotonic() - idle_since > 2:
                            break
                        if not selector.select(timeout=0.5):
                            continue
                        chunk = proc.stdout.read1(188 * 32)
                        if not chunk:
                            break
                        with self.lock:
                            self.bytes += len(chunk)
                            for client in list(self.clients):
                                try:
                                    client.put_nowait(chunk)
                                except queue.Full:
                                    self.clients.discard(client)
                                    self.end(client)
                finally:
                    selector.close()
        finally:
            if proc is not None:
                proc.stdout.close()
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
            with self.lock:
                for client in self.clients:
                    self.end(client)
                self.clients.clear()
                self.process = None
                self.thread = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def write_headers(self, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def do_HEAD(self):
        if self.path == "/odin.ts":
            self.write_headers("video/mp2t")
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/status":
            data = json.dumps(self.server.relay.status()).encode()
            self.write_headers("application/json")
            self.wfile.write(data)
            return
        if self.path != "/odin.ts":
            self.send_error(404)
            return
        self.connection.settimeout(10)
        client = self.server.relay.subscribe()
        try:
            self.write_headers("video/mp2t")
            while not self.server.relay.stopping.is_set():
                try:
                    chunk = client.get(timeout=1)
                except queue.Empty:
                    continue
                if chunk is None:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (OSError, TimeoutError):
            pass
        finally:
            self.server.relay.unsubscribe(client)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="odin2")
    parser.add_argument("--port", type=int, default=17855)
    args = parser.parse_args()
    relay = Relay(args.host)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    server.relay = relay
    def shutdown(*_):
        relay.stopping.set()
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    print(f"Odin OBS media URL: http://127.0.0.1:{args.port}/odin.ts", flush=True)
    try:
        server.serve_forever()
    finally:
        relay.stopping.set()
        if relay.thread is not None:
            relay.thread.join(timeout=5)
        server.server_close()


if __name__ == "__main__":
    main()
