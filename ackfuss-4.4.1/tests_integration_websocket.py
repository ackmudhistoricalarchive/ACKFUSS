#!/usr/bin/env python3
import base64
import hashlib
import os
import random
import socket
import string
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PORT = random.randint(5000, 5999)
NAME = "W" + "".join(random.choices(string.ascii_lowercase, k=7))
PASSWORD = "secret1"


def recv_exact(sock: socket.socket, pending: bytearray, n: int) -> bytes:
    while len(pending) < n:
        pending.extend(sock.recv(4096))
        if not pending:
            raise RuntimeError("Connection closed while reading frame")
    out = bytes(pending[:n])
    del pending[:n]
    return out


def recv_ws_text(sock: socket.socket, pending: bytearray, timeout=20) -> str:
    end = time.time() + timeout
    sock.settimeout(1)
    while time.time() < end:
        try:
            b1, b2 = recv_exact(sock, pending, 2)
        except socket.timeout:
            continue
        fin = (b1 & 0x80) != 0
        opcode = b1 & 0x0F
        masked = (b2 & 0x80) != 0
        plen = b2 & 0x7F
        if plen == 126:
            plen = int.from_bytes(recv_exact(sock, pending, 2), "big")
        elif plen == 127:
            plen = int.from_bytes(recv_exact(sock, pending, 8), "big")
        if masked:
            mask = recv_exact(sock, pending, 4)
        payload = recv_exact(sock, pending, plen)
        if masked:
            payload = bytes(payload[i] ^ mask[i % 4] for i in range(plen))

        if opcode == 0x9:
            send_ws_frame(sock, payload, opcode=0xA)
            continue
        if opcode == 0x1 and fin:
            return payload.decode("latin1", errors="ignore")
        if opcode == 0x8:
            raise RuntimeError("Server closed websocket")
    raise RuntimeError("Timed out waiting for websocket text frame")


def recv_until(sock: socket.socket, pending: bytearray, patterns, timeout=20):
    if isinstance(patterns, str):
        patterns = [patterns]
    end = time.time() + timeout
    data = ""
    while time.time() < end:
        data += recv_ws_text(sock, pending, timeout=5)
        lower = data.lower()
        if any(p.lower() in lower for p in patterns):
            return data
    raise RuntimeError(f"Timed out waiting for {patterns}. Last output:\n{data[-1000:]}")


def send_ws_frame(sock: socket.socket, payload: bytes, opcode=0x1):
    header = bytearray()
    header.append(0x80 | (opcode & 0x0F))
    plen = len(payload)
    if plen < 126:
        header.append(0x80 | plen)
    elif plen <= 0xFFFF:
        header.append(0x80 | 126)
        header.extend(plen.to_bytes(2, "big"))
    else:
        header.append(0x80 | 127)
        header.extend(plen.to_bytes(8, "big"))
    mask = os.urandom(4)
    header.extend(mask)
    masked = bytes(payload[i] ^ mask[i % 4] for i in range(plen))
    sock.sendall(header + masked)


def send_ws_line(sock: socket.socket, line: str):
    send_ws_frame(sock, (line + "\n").encode("latin1"))


def perform_handshake(sock: socket.socket) -> bytearray:
    pending = bytearray()
    key = base64.b64encode(os.urandom(16)).decode()
    req = (
        "GET / HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{PORT}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(req.encode("latin1"))

    raw = bytearray()
    sock.settimeout(5)
    while b"\r\n\r\n" not in raw:
        raw.extend(sock.recv(4096))
    header, rest = raw.split(b"\r\n\r\n", 1)
    response = header.decode("latin1", errors="ignore")

    if "101 Switching Protocols" not in response:
        raise RuntimeError(f"Handshake failed:\n{response}")
    accept = [l for l in response.split("\r\n") if l.lower().startswith("sec-websocket-accept:")]
    if not accept:
        raise RuntimeError(f"Missing Sec-WebSocket-Accept:\n{response}")
    expected = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    got = accept[0].split(":", 1)[1].strip()
    if got != expected:
        raise RuntimeError(f"Bad Sec-WebSocket-Accept: {got} != {expected}")

    pending.extend(rest)
    return pending


def create_new_character(sock: socket.socket, pending: bytearray):
    recv_until(sock, pending, ["Please enter your name:", "Enter your name please:", "By what name do you wish to be known?", "What is your name?", "Who do you think you are?!?"])
    send_ws_line(sock, NAME)
    recv_until(sock, pending, "(Y/N)?")
    send_ws_line(sock, "Y")
    recv_until(sock, pending, "Give me a password")
    send_ws_line(sock, PASSWORD)
    recv_until(sock, pending, "Please retype password")
    send_ws_line(sock, PASSWORD)

    recv_until(sock, pending, "Character Creation Menu")

    send_ws_line(sock, "1")
    recv_until(sock, pending, ["sex?", "Sex", "What IS your sex", "Please Select M/F/N"])
    send_ws_line(sock, "M")
    recv_until(sock, pending, "Character Creation Menu")

    send_ws_line(sock, "2")
    recv_until(sock, pending, ["Please Select Your Race", "Race (Abr)"])
    send_ws_line(sock, "Hmn")
    recv_until(sock, pending, "Character Creation Menu")

    send_ws_line(sock, "3")
    recv_until(sock, pending, ["Total:", "Please Select:"])
    stats = ["str", "int", "wis", "dex", "con"]
    for idx in range(600):
        send_ws_line(sock, f"+{stats[idx % len(stats)]}")
        recv_until(sock, pending, ["Total:", "already have", "already at max", "Please Select"])
        if idx % 10 == 9:
            send_ws_line(sock, "a")
            screen = recv_until(sock, pending, ["Character Creation Menu", "Please finish", "Please Select"])
            if "character creation menu" in screen.lower():
                break
    else:
        raise RuntimeError("Could not finish stat allocation")

    send_ws_line(sock, "4")
    recv_until(sock, pending, "Order:")
    send_ws_line(sock, "CLE WAR MAG THI PSI")
    recv_until(sock, pending, "Character Creation Menu")

    send_ws_line(sock, "5")
    recv_until(sock, pending, ["Welcome to", "Welcome New Player", "welcome", "Reconnecting.", "> "], timeout=30)


def login_existing_character(sock: socket.socket, pending: bytearray):
    recv_until(sock, pending, ["Please enter your name:", "Enter your name please:", "By what name do you wish to be known?", "What is your name?", "Who do you think you are?!?"])
    send_ws_line(sock, NAME)
    recv_until(sock, pending, "Password:")
    send_ws_line(sock, PASSWORD)
    recv_until(sock, pending, ["Welcome to", "Welcome New Player", "welcome", "Reconnecting.", "> "], timeout=30)


def main():
    for dirname in ["player", "npc", "mail", "log", "report", "src/o"]:
        (ROOT / dirname).mkdir(parents=True, exist_ok=True)

    server = subprocess.Popen(["./ack", str(PORT)], cwd=SRC, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        for _ in range(40):
            if server.poll() is not None:
                out = (server.stdout.read() or b"").decode(errors="ignore")
                raise RuntimeError(f"Server exited early:\n{out}")
            try:
                with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                    break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("Server did not start listening in time")

        with socket.create_connection(("127.0.0.1", PORT), timeout=10) as s1:
            pending1 = perform_handshake(s1)
            create_new_character(s1, pending1)
            time.sleep(1)
            send_ws_line(s1, "quit")

        with socket.create_connection(("127.0.0.1", PORT), timeout=10) as s2:
            pending2 = perform_handshake(s2)
            login_existing_character(s2, pending2)
            time.sleep(1)
            send_ws_line(s2, "quit")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
