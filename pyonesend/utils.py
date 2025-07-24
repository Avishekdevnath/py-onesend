"""
Utility functions for py-onesend.
"""

import socket
import threading
import time

def print_banner():
    print("""
====================================
   py-onesend: Secure File Transfer
====================================
    """)

def build_download_url(config, token):
    host = config.domain or get_local_ip()
    return f"https://{host}:{config.port}/download?token={token}"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def show_qr_code(url):
    try:
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make()
        qr.print_ascii()
    except ImportError:
        print("[!] qrcode module not found. Showing URL only:")
        print(url)

def start_expiry_timer(httpd, seconds):
    def shutdown():
        time.sleep(seconds)
        print(f"\n[!] Server expired after {seconds} seconds.")
        httpd.shutdown()
    threading.Thread(target=shutdown, daemon=True).start() 