"""
Security utilities for py-onesend.
"""

import uuid
import base64
import ssl
import tempfile
import os
from http import HTTPStatus


def generate_token():
    """Generate a secure UUID token."""
    return str(uuid.uuid4())


def check_password(headers, expected_password):
    """Check HTTP Basic Auth password from headers."""
    auth = headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return False
    try:
        encoded = auth.split(' ', 1)[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        user, pwd = decoded.split(':', 1)
        return pwd == expected_password
    except Exception:
        return False


def generate_self_signed_cert():
    """Generate a self-signed SSL cert and key, return their paths (temp files)."""
    # For demo: use tempfile and OpenSSL if available, else fail gracefully
    import subprocess
    cert_fd, cert_path = tempfile.mkstemp(suffix='.crt')
    key_fd, key_path = tempfile.mkstemp(suffix='.key')
    os.close(cert_fd)
    os.close(key_fd)
    try:
        subprocess.check_call([
            'openssl', 'req', '-x509', '-nodes', '-days', '1',
            '-newkey', 'rsa:2048',
            '-keyout', key_path,
            '-out', cert_path,
            '-subj', '/CN=localhost'
        ])
        return cert_path, key_path
    except Exception:
        raise RuntimeError('OpenSSL is required for self-signed cert generation') 