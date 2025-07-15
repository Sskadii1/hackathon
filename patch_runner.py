import os
import subprocess
import requests
from logger import log

def download_patch(kbid, download_url, dest_folder="patches"):
    os.makedirs(dest_folder, exist_ok=True)
    local_path = os.path.join(dest_folder, f"{kbid}.msu")
    try:
        r = requests.get(download_url, stream=True, timeout=60)
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return local_path
    except Exception as e:
        log("ERROR", f"Download failed for {kbid}: {e}")
        return None

def run_patch(local_file, kbid):
    try:
        cmd = ["wusa.exe", local_file, "/quiet", "/norestart"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log("INFO", f"{kbid} installed successfully.")
            return True
        else:
            log("ERROR", f"{kbid} failed with exit code: {hex(result.returncode)}")
            return False
    except Exception as e:
        log("ERROR", f"{kbid} exception during patch: {e}")
        return False
