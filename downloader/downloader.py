import os
import requests
import time
from datetime import datetime
from urllib.parse import urlparse

from config import BASE_DOWNLOAD_DIR, REQUEST_TIMEOUT
from utils.file_utils import valid_file
from utils.hash_utils import sha256_file
from logger import logger


class Downloader:
    def __init__(self, db):
        self.db = db

    def download(self, item):
        url = item.get("url")
        if not url or self.db.exists(url):
            return

        filename = item.get("filename")
        if not valid_file(filename):
            return

        repo = item.get("repository", "unknown")
        project_id = "".join(c for c in urlparse(url).path if c.isalnum())[:16]
        local_dir = os.path.join(BASE_DOWNLOAD_DIR, repo, project_id)

        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        # We will attempt the download up to 3 times if the server blocks us
        for attempt in range(3):
            try:
                # The Magic Politeness Delay - Prevents [Errno 61]
                time.sleep(1.5)

                logger.info(f"Downloading {filename} (Attempt {attempt + 1})")

                # We disguise the downloader as a standard Chrome web browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

                r = requests.get(url, stream=True, headers=headers, timeout=REQUEST_TIMEOUT)

                if r.status_code == 429:  # 429 means "Too Many Requests"
                    logger.warning(f"Rate limited by {repo}. Sleeping for 15 seconds...")
                    time.sleep(15)
                    continue

                if r.status_code != 200:
                    return

                with open(local_path, "wb") as f:
                    for chunk in r.iter_content(65536):
                        f.write(chunk)

                file_hash = sha256_file(local_path)

                data = (
                    url, datetime.now().isoformat(), repo, filename, local_dir,
                    item.get("license", ""), item.get("uploader", ""), os.path.splitext(filename)[1],
                    file_hash, item.get("metadata", ""), "", ""
                )

                self.db.insert(data)
                return  # If successful, break out of the retry loop

            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection refused by {repo}. Giving the server a 10-second break...")
                time.sleep(10)
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
                return
