"""
download_more_loghub_datasets.py - Fetches BGL Supercomputer, Thunderbird, Spark, Windows, and Android production logs.
"""

import os
import urllib.request

LOGHUB_BASE_URL = "https://raw.githubusercontent.com/logpai/loghub/master/"

ADDITIONAL_DATASETS = {
    "bgl_supercomputer/BGL_2k.log": "BGL/BGL_2k.log",
    "thunderbird/Thunderbird_2k.log": "Thunderbird/Thunderbird_2k.log",
    "spark_cluster/Spark_2k.log": "Spark/Spark_2k.log",
    "windows_events/Windows_2k.log": "Windows/Windows_2k.log",
    "android_system/Android_2k.log": "Android/Android_2k.log"
}

TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))

def download_more():
    print("=========================================================")
    print("DOWNLOADING ADDITIONAL PRODUCTION LOG DATASETS (BGL, Thunderbird, Spark, Windows, Android)")
    print("=========================================================")
    
    for rel_path, remote_path in ADDITIONAL_DATASETS.items():
        local_path = os.path.join(TARGET_DIR, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        url = LOGHUB_BASE_URL + remote_path
        print(f"[Downloading] {url} -> {rel_path}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response, open(local_path, "wb") as out_file:
                out_file.write(response.read())
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            print(f"[OK] Successfully added {len(lines)} log lines to {rel_path}.")
        except Exception as e:
            print(f"[Error] Failed to download {url}: {e}")
            
    print("=========================================================")
    print("ADDITIONAL DATASETS INGESTION COMPLETE!")
    print("=========================================================")

if __name__ == "__main__":
    download_more()
