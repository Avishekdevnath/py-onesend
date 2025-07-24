"""
py-onesend: Secure, one-time file transfer over HTTPS (no third-party dependencies)
"""

import os
import shutil
import tempfile
import subprocess
import time
import requests
from .server import OneSendServer, OneSendConfig

def send_files_or_folders(paths, port=9000, max_downloads=5, password=None, delete_after=True, tunnel_ngrok=False, output=None):
    """
    Programmatically send multiple files/folders as a single zip archive.
    If tunnel_ngrok=True, launches ngrok and returns the public URL.
    If output is given, use it as the zip name. Otherwise, use smart auto-naming.
    Returns (local_url, public_url, token)
    """
    import os
    import shutil
    import tempfile
    import subprocess
    import time
    import requests
    file_paths = paths
    output_zip = output
    if output_zip:
        zip_path = os.path.abspath(output_zip)
    elif len(file_paths) == 1 and os.path.isdir(file_paths[0]):
        zip_path = os.path.abspath('folder.zip')
    elif len(file_paths) == 1 and os.path.isfile(file_paths[0]):
        file_path = file_paths[0]
        zip_path = None
    else:
        zip_path = os.path.abspath(f'folder_and_{len(file_paths)-1}_more.zip')

    if len(file_paths) == 1 and os.path.isdir(file_paths[0]):
        folder_path = os.path.abspath(file_paths[0])
        parent_dir = os.path.dirname(folder_path)
        base_name = os.path.basename(folder_path)
        shutil.make_archive(zip_path[:-4], 'zip', root_dir=parent_dir, base_dir=base_name)
        print(f"[i] Zipped folder '{folder_path}' to '{zip_path}' for transfer.")
        file_path = zip_path
        cleanup_zip = zip_path if not output_zip else None
    elif len(file_paths) == 1 and os.path.isfile(file_paths[0]):
        file_path = file_paths[0]
        cleanup_zip = None
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            for path in file_paths:
                base = os.path.basename(path.rstrip(os.sep))
                dest = os.path.join(temp_dir, base)
                if os.path.isdir(path):
                    shutil.copytree(path, dest)
                else:
                    shutil.copy2(path, dest)
            shutil.make_archive(zip_path[:-4], 'zip', temp_dir)
        print(f"[i] Zipped files/folders {file_paths} to '{zip_path}' for transfer.")
        file_path = zip_path
        cleanup_zip = zip_path if not output_zip else None
    ngrok_proc = None
    public_url = None
    if tunnel_ngrok:
        port = 9000  # Force port to 9000 for both server and ngrok
        ngrok_proc = subprocess.Popen(['ngrok', 'http', str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(20):  # Retry up to 10 seconds (20 x 0.5s)
            time.sleep(0.5)
            try:
                resp = requests.get('http://localhost:4040/api/tunnels')
                tunnels = resp.json().get('tunnels', [])
                for t in tunnels:
                    if t['proto'] == 'https':
                        public_url = t['public_url']
                        break
                if public_url:
                    break
            except Exception:
                pass
        if not public_url:
            print(f"[!] Could not get ngrok public URL after waiting.")
    from .server import OneSendServer, OneSendConfig
    config = OneSendConfig(
        file_path=file_path,
        port=port,
        password=password,
        delete_after=delete_after
    )
    server = OneSendServer(config)
    server.max_downloads = max_downloads
    local_url = f"http://localhost:{port}/download?token={server.token}"
    print(f"Download URL: {local_url}")
    if public_url:
        print(f"[ngrok] Public download URL: {public_url}/download?token={server.token}")
    server.run()
    if cleanup_zip and os.path.exists(cleanup_zip):
        os.remove(cleanup_zip)
    if ngrok_proc:
        ngrok_proc.terminate()
    return local_url, (f"{public_url}/download?token={server.token}" if public_url else None), server.token 