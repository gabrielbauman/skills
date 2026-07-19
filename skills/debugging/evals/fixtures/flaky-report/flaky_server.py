"""Local mock of the flaky report service.

Serves GET /report as JSON, but randomly resets a fraction of
connections mid-request the way the real upstream does. Run it, point
fetch_report.py at it, and the intermittent ConnectionResetError is
reproducible on demand.

Usage: python3 flaky_server.py [port] [reset_rate]
Defaults: port 8321, reset_rate 0.4
"""

import json
import random
import socket
import struct
import sys


def serve(port=8321, reset_rate=0.4):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen(16)
    print(f"flaky report server on http://127.0.0.1:{port}/report "
          f"(reset rate {reset_rate:.0%})", flush=True)
    while True:
        conn, _ = listener.accept()
        try:
            conn.recv(65536)  # read the request; content doesn't matter
            if random.random() < reset_rate:
                # SO_LINGER(on, 0) makes close() send RST, not FIN: the
                # client sees ConnectionResetError, same as production.
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                struct.pack("ii", 1, 0))
                conn.close()
                continue
            body = json.dumps({"report": "ok", "rows": 42}).encode()
            conn.sendall(b"HTTP/1.1 200 OK\r\n"
                         b"Content-Type: application/json\r\n"
                         b"Content-Length: " + str(len(body)).encode() +
                         b"\r\nConnection: close\r\n\r\n" + body)
            conn.close()
        except OSError:
            pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8321
    rate = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
    serve(port, rate)
