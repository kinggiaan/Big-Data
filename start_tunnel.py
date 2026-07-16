import os
import sys
import platform
import urllib.request
import subprocess
import re
import shutil

ES_URL = "http://localhost:9200"

def get_cloudflared_path():
    # Check if cloudflared is already in PATH
    path = shutil.which("cloudflared")
    if path:
        return path
    
    # Check if downloaded locally
    local_name = "cloudflared.exe" if platform.system() == "Windows" else "./cloudflared"
    if os.path.exists(local_name):
        return local_name
        
    return None

def download_cloudflared(target_path):
    print("Cloudflared not found. Downloading the latest version...")
    system = platform.system()
    if system == "Windows":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif system == "Linux":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    else:
        print(f"Unsupported OS: {system}. Please install cloudflared manually.")
        sys.exit(1)
        
    print(f"Downloading from {url}...")
    try:
        # User-agent header to avoid blocked requests
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        if system != "Windows":
            os.chmod(target_path, 0o755)
        print("Download complete!")
    except Exception as e:
        print(f"Failed to download: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("        Elasticsearch Cloudflare Tunnel Starter")
    print("=" * 60)
    
    # Get or download cloudflared
    bin_path = get_cloudflared_path()
    if not bin_path:
        local_bin = "cloudflared.exe" if platform.system() == "Windows" else "cloudflared"
        download_cloudflared(local_bin)
        bin_path = "./" + local_bin if platform.system() != "Windows" else local_bin
        
    print(f"Using cloudflared binary: {bin_path}")
    print(f"Tunneling Elasticsearch at {ES_URL}...")
    print("Starting tunnel, please wait...")
    print("Press Ctrl+C to stop the tunnel.")
    print("-" * 60)
    
    # Start the tunnel process
    # cloudflared prints logs to stderr
    process = subprocess.Popen(
        [bin_path, "tunnel", "--url", ES_URL],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Monitor stderr in a loop to capture the URL
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    try:
        while True:
            # Read stderr line by line
            line = process.stderr.readline()
            if not line:
                break
                
            # Also print the raw logs so the user knows what's happening
            print(line.strip())
            
            # Look for the URL
            match = url_pattern.search(line)
            if match:
                url = match.group(0)
                print("\n" + "=" * 60)
                print("🎉 SUCCESS! Cloudflare Tunnel is active!")
                print(f"🔗 Public URL: {url}")
                print("Use this URL in your frontend or API calls.")
                print("=" * 60 + "\n")
                
            # If the process exited, break
            if process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\nStopping tunnel...")
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Tunnel stopped.")

if __name__ == "__main__":
    main()
