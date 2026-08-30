"""
fetch_kaggle_loghub_datasets.py - Downloads real-world production log datasets from Loghub / Kaggle benchmark repositories.
"""

import os
import urllib.request

LOGHUB_BASE_URL = "https://raw.githubusercontent.com/logpai/loghub/master/"

DATASETS = {
    "openssh/OpenSSH_2k.log": "OpenSSH/OpenSSH_2k.log",
    "apache/Apache_2k.log": "Apache/Apache_2k.log",
    "linux_syslog/Linux_2k.log": "Linux/Linux_2k.log",
    "hdfs/HDFS_2k.log": "HDFS/HDFS_2k.log",
    "zookeeper/ZooKeeper_2k.log": "ZooKeeper/ZooKeeper_2k.log"
}

TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))

def download_datasets():
    print("=========================================================")
    print("DOWNLOADING AUTHENTIC KAGGLE / LOGHUB PRODUCTION LOG DATASETS")
    print("=========================================================")
    
    for rel_path, remote_path in DATASETS.items():
        local_path = os.path.join(TARGET_DIR, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        url = LOGHUB_BASE_URL + remote_path
        print(f"[Downloading] {url} -> {rel_path}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response, open(local_path, "wb") as out_file:
                out_file.write(response.read())
            # Count lines
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            print(f"[OK] Downloaded {len(lines)} authentic log lines to {rel_path}.")
        except Exception as e:
            print(f"[Error] Failed to download {url}: {e}")
            
    print("=========================================================")
    print("KAGGLE / LOGHUB DATASETS DOWNLOAD COMPLETED!")
    print("=========================================================")

if __name__ == "__main__":
    download_datasets()
