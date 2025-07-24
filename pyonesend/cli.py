"""
CLI entrypoint for py-onesend.
"""

import argparse
from pyonesend.server import OneSendServer, OneSendConfig
from pyonesend.utils import print_banner
import subprocess
import time
import requests
import os
import shutil
import tempfile


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="py-onesend: Secure one-time file transfer over HTTPS.")
    parser.add_argument('--file', required=True, nargs='+', help='Path(s) to the file(s) or folder(s) to send (space separated)')
    parser.add_argument('--port', type=int, default=8443, help='Port to run the HTTPS server on (default: 8443)')
    parser.add_argument('--password', help='Optional password for download')
    parser.add_argument('--cert', help='Path to SSL certificate (optional)')
    parser.add_argument('--key', help='Path to SSL key (optional)')
    parser.add_argument('--expire-after', type=int, help='Expire server after N seconds (optional)')
    parser.add_argument('--encrypt-zip', action='store_true', help='Encrypt file as ZIP (optional)')
    parser.add_argument('--show-qr', action='store_true', help='Show QR code for download link (optional)')
    parser.add_argument('--delete-after', action='store_true', default=True, help='Delete file after download (default: true)')
    parser.add_argument('--domain', help='Custom domain for download URL (optional)')
    parser.add_argument('--tunnel', choices=['ngrok'], help='Tunnel type for public URL (currently only ngrok supported)')
    parser.add_argument('--max-downloads', type=int, default=5, help='Maximum number of downloads allowed (default: 5)')
    parser.add_argument('--output', help='Optional output zip file name (e.g., myarchive.zip)')
    args = parser.parse_args()

    if args.encrypt_zip and not args.password:
        import getpass
        args.password = getpass.getpass('Enter password for encrypted zip: ')

    ngrok_proc = None
    public_url = None
    if args.tunnel == 'ngrok':
        ngrok_proc = subprocess.Popen(['ngrok', 'http', str(args.port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for ngrok to initialize
        time.sleep(3)
        try:
            resp = requests.get('http://localhost:4040/api/tunnels')
            tunnels = resp.json().get('tunnels', [])
            for t in tunnels:
                if t['proto'] == 'https':
                    public_url = t['public_url']
                    break
        except Exception as e:
            print(f"[!] Could not get ngrok public URL: {e}")

    # Handle single or multiple files/folders with smart auto-naming or user-specified output
    cleanup_zip = None
    file_paths = args.file
    output_zip = args.output
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
        folder_path = file_paths[0]
        parent_dir = os.path.dirname(os.path.abspath(folder_path))
        base_name = os.path.basename(os.path.abspath(folder_path))
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

    config = OneSendConfig(
        file_path=file_path,
        port=args.port,
        password=args.password,
        cert_path=args.cert,
        key_path=args.key,
        expire_after=args.expire_after,
        encrypt_zip=args.encrypt_zip if hasattr(args, 'encrypt_zip') else False,
        show_qr=args.show_qr if hasattr(args, 'show_qr') else False,
        delete_after=args.delete_after,
        domain=args.domain if hasattr(args, 'domain') else None
    )

    server = OneSendServer(config)
    server.max_downloads = args.max_downloads
    if public_url:
        time.sleep(1)
        print(f"\n[ngrok] Public download URL: {public_url}/download?token={server.token}\n")
    server.run()
    if cleanup_zip and os.path.exists(cleanup_zip):
        os.remove(cleanup_zip)
    if ngrok_proc:
        ngrok_proc.terminate()

if __name__ == "__main__":
    main() 