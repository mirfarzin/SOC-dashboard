"""
Automated UI Screenshot Capture for PS02 React + FastAPI SOC Dashboard.
Launches the FastAPI server serving React SPA, connects via Headless Edge/Chrome CDP,
and captures full-resolution screenshots of all 6 views into outputs/screenshots/react_dashboard/.
"""

import os
import sys
import time
import json
import base64
import urllib.request
import subprocess
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "outputs" / "screenshots" / "react_dashboard"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return None


def run_server():
    import uvicorn
    from src.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def wait_for_server(url="http://127.0.0.1:8000/api/health", timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def cdp_send(ws_url, method, params=None, msg_id=1):
    import urllib.request
    # Simple WebSocket client via Python or direct HTTP endpoints
    # Actually, CDP over simple HTTP endpoints or websocket:
    pass


def main():
    browser_exe = find_browser()
    if not browser_exe:
        print("[ERROR] Neither Edge nor Chrome found on system.")
        sys.exit(1)

    print(f"[1/5] Starting FastAPI backend server in background...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    if not wait_for_server():
        print("[ERROR] Server failed to start on port 8000")
        sys.exit(1)
    print("      FastAPI is healthy on http://127.0.0.1:8000")

    # Start Edge with remote debugging
    debug_port = 9222
    user_data = BASE_DIR / ".browser_profile"
    cmd = [
        browser_exe,
        "--headless=new",
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        "--window-size=1440,960",
        "http://127.0.0.1:8000/",
    ]

    print(f"[2/5] Launching headless browser: {browser_exe}")
    browser_proc = subprocess.Popen(cmd)

    # Wait for CDP endpoint
    time.sleep(3)
    tab_list_url = f"http://127.0.0.1:{debug_port}/json"
    ws_url = None
    for _ in range(20):
        try:
            with urllib.request.urlopen(tab_list_url, timeout=2) as resp:
                tabs = json.loads(resp.read().decode())
                if tabs and len(tabs) > 0:
                    ws_url = tabs[0].get("webSocketDebuggerUrl")
                    if ws_url:
                        break
        except Exception:
            time.sleep(0.5)

    if not ws_url:
        print("[ERROR] Could not connect to browser CDP WebSocket")
        browser_proc.kill()
        sys.exit(1)

    print(f"[3/5] Connected to browser via CDP: {ws_url}")

    # Use websocket to send CDP commands
    # Python 3.14 includes websockets or standard sockets
    import socket
    # We can use simple websocket client or python urllib / http
    # Let's use simple socket-based framing or python-websocket if available, or write a minimal ws helper
    from urllib.parse import urlparse

    parsed = urlparse(ws_url)
    ws_host = parsed.hostname
    ws_port = parsed.port
    ws_path = parsed.path

    # Minimal WebSocket Client for CDP
    s = socket.create_connection((ws_host, ws_port), timeout=10)
    key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET {ws_path} HTTP/1.1\r\n"
        f"Host: {ws_host}:{ws_port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(handshake.encode())
    resp = s.recv(4096)
    if b"101 " not in resp:
        print("[ERROR] WebSocket handshake failed:", resp.decode(errors='ignore'))
        browser_proc.kill()
        sys.exit(1)

    msg_counter = [0]

    def send_cdp(method, params=None):
        msg_counter[0] += 1
        payload = json.dumps({"id": msg_counter[0], "method": method, "params": params or {}}).encode()
        # Create unmasked/masked frame (client to server must be masked)
        mask = os.urandom(4)
        length = len(payload)
        frame = bytearray([0x81])  # text frame, fin=1
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, "big"))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, "big"))
        frame.extend(mask)
        masked_payload = bytearray(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame.extend(masked_payload)
        s.sendall(frame)

        # Receive response matching id
        target_id = msg_counter[0]
        buf = bytearray()
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
            # Try to parse frame
            while len(buf) >= 2:
                b1 = buf[0]
                b2 = buf[1]
                payload_len = b2 & 0x7F
                offset = 2
                if payload_len == 126:
                    if len(buf) < 4:
                        break
                    payload_len = int.from_bytes(buf[2:4], "big")
                    offset = 4
                elif payload_len == 127:
                    if len(buf) < 10:
                        break
                    payload_len = int.from_bytes(buf[2:10], "big")
                    offset = 10

                if len(buf) < offset + payload_len:
                    break

                raw_msg = buf[offset:offset+payload_len]
                buf = buf[offset+payload_len:]

                try:
                    msg_obj = json.loads(raw_msg.decode("utf-8", errors="ignore"))
                    if msg_obj.get("id") == target_id:
                        return msg_obj.get("result", {})
                except Exception:
                    pass

    # Configure viewport
    send_cdp("Emulation.setDeviceMetricsOverride", {
        "width": 1440,
        "height": 960,
        "deviceScaleFactor": 1,
        "mobile": False,
    })

    # Wait 3s for React SPA to fully mount and fetch dashboard
    time.sleep(3)

    views = [
        ("01_soc_overview.png", "document.querySelectorAll('aside nav button')[0].click()", "Overview"),
        ("02_telemetry_ingestion.png", "document.querySelectorAll('aside nav button')[1].click()", "Telemetry Ingestion"),
        ("03_correlated_incidents.png", "document.querySelectorAll('aside nav button')[2].click()", "Correlated Incidents"),
        ("04_incident_deep_dive.png", "document.querySelectorAll('aside nav button')[3].click()", "Incident Deep Dive"),
        ("05_evaluation_metrics.png", "document.querySelectorAll('aside nav button')[4].click()", "Evaluation Metrics"),
        ("06_system_configuration.png", "document.querySelectorAll('aside nav button')[5].click()", "System Configuration"),
    ]

    print("[4/5] Capturing high-resolution screenshots...")
    for filename, js_click, label in views:
        # Click tab
        send_cdp("Runtime.evaluate", {"expression": js_click})
        time.sleep(1.2)  # Wait for transition/render

        # Capture screenshot
        result = send_cdp("Page.captureScreenshot", {"format": "png"})
        if result and "data" in result:
            img_data = base64.b64decode(result["data"])
            out_file = SCREENSHOTS_DIR / filename
            out_file.write_bytes(img_data)
            print(f"      ✓ Captured {label} -> {out_file.name} ({len(img_data)//1024} KB)")
        else:
            print(f"      ✗ Failed capturing {label}")

    print("[5/5] Cleaning up processes...")
    try:
        s.close()
    except Exception:
        pass
    browser_proc.kill()
    print("Done! Screenshots saved to:", SCREENSHOTS_DIR)


if __name__ == "__main__":
    main()
