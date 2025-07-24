# pyonesend

**pyonesend** is a Python package and CLI tool for secure, one-time or limited-use file and folder sharing. Instantly generate a public download link (via ngrok) for any file or folder on your machine—no third-party dependencies required.

---

## Why pyonesend?
- **Share files/folders securely** with a single command or function call.
- **One-time or limited-use links**: Download is allowed only as many times as you specify.
- **No cloud upload**: Your files never leave your machine until downloaded.
- **Works globally**: Public link via ngrok, accessible from anywhere.
- **No dependencies**: Pure Python, ngrok is optional.

---

## Features
- One-time or limited-use download links
- Public link via ngrok (works globally)
- Password protection (optional)
- Smart or custom zip naming
- CLI and importable API
- Download limit
- No third-party dependencies (except optional ngrok)

---

## Installation

**Install from PyPI:**
```sh
pip install pyonesend
```

**For local development:**
```sh
pip install .
```

---

## CLI Usage

**Send a folder, allow 2 downloads, get a public link:**
```sh
python -m pyonesend.cli --file Profile --tunnel ngrok --max-downloads 2 --output archive.zip
```

**Send multiple files/folders:**
```sh
python -m pyonesend.cli --file Profile Docs file.txt --output myfiles.zip --tunnel ngrok
```

**Password-protect a download:**
```sh
python -m pyonesend.cli --file Profile --password secret123 --tunnel ngrok
```

---

## Import/API Usage

```python
from pyonesend import send_files_or_folders

local_url, public_url, token = send_files_or_folders(
    ['Profile'],
    max_downloads=2,
    tunnel_ngrok=True,
    output='archive.zip',
    password='secret123'
)
print("Local download URL:", local_url)
print("Public ngrok URL:", public_url)
print("Token:", token)
input("\nServer is running. Press Enter to exit and close the tunnel...")
```

---

## API Reference

### `send_files_or_folders(paths, max_downloads=1, tunnel_ngrok=False, output=None, password=None, delete_after=True)`

Send one or more files/folders as a one-time or limited-use download link, with optional ngrok public URL and custom zip naming.

**Parameters:**
- `paths` (`List[str]`): List of file or folder paths to send.
- `max_downloads` (`int`, default `1`): Maximum number of downloads allowed before the link expires.
- `tunnel_ngrok` (`bool`, default `False`): If `True`, launches ngrok and returns a public URL.
- `output` (`str`, optional): Output zip file name. If not provided, a smart name is chosen.
- `password` (`str`, optional): Password required to download the file (HTTP Basic Auth).
- `delete_after` (`bool`, default `True`): Delete the zip after transfer (unless a custom output name is used).

**Returns:**
- `local_url` (`str`): The local download URL.
- `public_url` (`str` or `None`): The ngrok public download URL, or `None` if not using ngrok.
- `token` (`str`): The secure token for the download.

**Example return:**
```python
(
  'http://localhost:9000/download?token=abc123',
  'https://xxxx.ngrok-free.app/download?token=abc123',
  'abc123'
)
```

**Raises:**
- `FileNotFoundError` if any path does not exist.
- `RuntimeError` if ngrok is not installed or fails to start.

---

## Windows Firewall: Open Port 9000

To allow downloads from other devices, you must open port 9000 in Windows Firewall:

1. Open **Windows Defender Firewall with Advanced Security**.
2. Click **Inbound Rules** > **New Rule...**
3. Select **Port** > **Next**
4. Select **TCP** and enter **9000** > **Next**
5. Allow the connection > **Next**
6. Check all profiles (Domain, Private, Public) > **Next**
7. Name the rule (e.g., `pyonesend 9000`) > **Finish**

Or, run this in an **Administrator Command Prompt**:
```sh
netsh advfirewall firewall add rule name="pyonesend 9000" dir=in action=allow protocol=TCP localport=9000
```

---

## ngrok Setup

1. **Download ngrok:**  
   https://ngrok.com/download
2. **Install ngrok:**  
   Unzip and place `ngrok.exe` in a folder in your PATH (e.g., `C:\Windows` or your project folder).
3. **(Optional) Authenticate ngrok:**  
   Sign up at ngrok.com, get your auth token, and run:
   ```sh
   ngrok config add-authtoken <YOUR_AUTH_TOKEN>
   ```
4. **No need to run ngrok manually** – pyonesend will launch it for you!

---

## Security Notes
- By default, runs over HTTP (insecure). For production, use real SSL certs.
- ngrok links are public; anyone with the link can download until the limit is reached.
- No files are kept after transfer unless you specify an output zip name.

---

## FAQ / Troubleshooting

**Q: Why do I get ERR_NGROK_8012 or 3200?**  
A: Make sure the server is running and ngrok is tunneling the correct port (default: 9000). Only one ngrok process per port.

**Q: Why do I get 'Invalid token'?**  
A: Use the download link and token from the current server run. Restart the server for a new link.

**Q: How do I keep the server running for manual testing?**  
A: Use the import example with `input("Press Enter to exit...")` to keep the tunnel alive.

---

## License
MIT 