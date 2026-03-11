#!/usr/bin/env python3
import random
import re
import socket
import string
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PORT = random.randint(4000, 4999)
NAME = "T" + "".join(random.choices(string.ascii_lowercase, k=7))
PASSWORD = "secret1"


def recv_until(sock: socket.socket, patterns, timeout=20):
    if isinstance(patterns, str):
        patterns = [patterns]
    end = time.time() + timeout
    data = ""
    sock.settimeout(0.5)
    while time.time() < end:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            continue
        if not chunk:
            break
        data += chunk.decode("latin1", errors="ignore")
        lower = data.lower()
        if any(p.lower() in lower for p in patterns):
            return data
    raise RuntimeError(f"Timed out waiting for {patterns}. Last output:\n{data[-1000:]}")


def send_line(sock: socket.socket, line: str):
    sock.sendall((line + "\n").encode())


def current_total(screen: str):
    m = re.search(r"Total: \[(\d+)/(\d+)\]", screen)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def create_new_character(sock: socket.socket):
    recv_until(sock, ["Please enter your name:", "Enter your name please:", "By what name do you wish to be known?", "What is your name?", "Who do you think you are?!?"])
    send_line(sock, NAME)
    recv_until(sock, "(Y/N)?")
    send_line(sock, "Y")
    recv_until(sock, "Give me a password")
    send_line(sock, PASSWORD)
    recv_until(sock, "Please retype password")
    send_line(sock, PASSWORD)

    recv_until(sock, "Character Creation Menu")

    send_line(sock, "1")
    recv_until(sock, ["sex?", "Sex", "What IS your sex", "Please Select M/F/N"])
    send_line(sock, "M")
    recv_until(sock, "Character Creation Menu")

    send_line(sock, "2")
    recv_until(sock, ["Please Select Your Race", "Race (Abr)"])
    send_line(sock, "Hmn")
    recv_until(sock, "Character Creation Menu")

    send_line(sock, "3")
    recv_until(sock, ["Total:", "Please Select:"])
    stats = ["str", "int", "wis", "dex", "con"]
    for idx in range(600):
        send_line(sock, f"+{stats[idx % len(stats)]}")
        recv_until(sock, ["Total:", "already have", "already at max", "Please Select"]) 
        if idx % 10 == 9:
            send_line(sock, "a")
            screen = recv_until(sock, ["Character Creation Menu", "Please finish", "Please Select"])
            if "character creation menu" in screen.lower():
                break
    else:
        raise RuntimeError("Could not finish stat allocation")

    send_line(sock, "4")
    recv_until(sock, "Order:")
    send_line(sock, "CLE WAR MAG THI PSI")
    recv_until(sock, "Character Creation Menu")

    send_line(sock, "5")
    recv_until(sock, ["Welcome to", "Welcome New Player", "welcome", "Reconnecting.", "> "], timeout=30)


def login_existing_character(sock: socket.socket):
    recv_until(sock, ["Please enter your name:", "Enter your name please:", "By what name do you wish to be known?", "What is your name?", "Who do you think you are?!?"])
    send_line(sock, NAME)
    recv_until(sock, "Password:")
    send_line(sock, PASSWORD)
    recv_until(sock, ["Welcome to", "Welcome New Player", "welcome", "Reconnecting.", "> "], timeout=30)


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
            create_new_character(s1)
            time.sleep(1)
            send_line(s1, "quit")

        with socket.create_connection(("127.0.0.1", PORT), timeout=10) as s2:
            login_existing_character(s2)
            time.sleep(8)
            send_line(s2, "quit")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
