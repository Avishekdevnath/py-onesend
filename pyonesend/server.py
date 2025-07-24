"""
HTTPS server for one-time file transfer.
"""

import os
import ssl
import threading
import socket
import http.server
from dataclasses import dataclass
from pyonesend.security import generate_token, check_password, generate_self_signed_cert
from pyonesend.utils import build_download_url, show_qr_code, start_expiry_timer

@dataclass
class OneSendConfig:
    file_path: str
    port: int = 8443
    password: str = None
    cert_path: str = None
    key_path: str = None
    expire_after: int = None
    encrypt_zip: bool = False
    show_qr: bool = False
    delete_after: bool = True
    domain: str = None

class OneSendServer:
    def __init__(self, config: OneSendConfig):
        self.config = config
        self.token = generate_token()
        self.cert_path, self.key_path = self._ensure_cert()
        self.download_count = 0
        self.max_downloads = 5
        self.httpd = None

    def _ensure_cert(self):
        if self.config.cert_path and self.config.key_path:
            return self.config.cert_path, self.config.key_path
        try:
            return generate_self_signed_cert()
        except Exception as e:
            print(f"[!] Warning: {e}. Running in HTTP (insecure) mode for local development.")
            return None, None

    def run(self):
        handler = self._make_handler()
        self.httpd = http.server.HTTPServer(("", self.config.port), handler)
        if self.cert_path and self.key_path:
            self.httpd.socket = ssl.wrap_socket(
                self.httpd.socket,
                certfile=self.cert_path,
                keyfile=self.key_path,
                server_side=True
            )
            url = build_download_url(self.config, self.token)
        else:
            url = build_download_url(self.config, self.token).replace('https://', 'http://')
            print("[!] Running without SSL. Use only for local development/testing.")
        print(f"\nDownload URL: {url}\n")
        if self.config.show_qr:
            show_qr_code(url)
        if self.config.expire_after:
            start_expiry_timer(self.httpd, self.config.expire_after)
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        finally:
            self.httpd.server_close()

    def _make_handler(self):
        server = self
        class OneTimeHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.path)
                if parsed.path != '/download':
                    self.send_error(404)
                    return
                qs = parse_qs(parsed.query)
                token = qs.get('token', [None])[0]
                if token != server.token:
                    self.send_error(403, "Invalid token")
                    return
                if server.download_count >= server.max_downloads:
                    self.send_error(410, "File download limit reached")
                    return
                if server.config.password:
                    if not check_password(self.headers, server.config.password):
                        self.send_response(401)
                        self.send_header('WWW-Authenticate', 'Basic realm="py-onesend"')
                        self.end_headers()
                        return
                try:
                    with open(server.config.file_path, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(server.config.file_path)}"')
                        self.end_headers()
                        self.wfile.write(f.read())
                    server.download_count += 1
                    if server.download_count >= server.max_downloads:
                        if server.config.delete_after:
                            os.remove(server.config.file_path)
                        threading.Thread(target=server.httpd.shutdown).start()
                except Exception as e:
                    self.send_error(500, str(e))
        return OneTimeHandler 