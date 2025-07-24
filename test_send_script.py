from pyonesend import send_files_or_folders

# Developer example: send 'Profile' folder, allow 2 downloads, use ngrok, name zip 'archive.zip'
local_url, public_url, token = send_files_or_folders(
    ['Profile'],
    max_downloads=2,
    tunnel_ngrok=True,
    output='archive.zip'
)

print("Local download URL:", local_url)
print("Public ngrok URL:", public_url)
print("Token:", token)

input("\nServer is running. Press Enter to exit and close the tunnel...") 