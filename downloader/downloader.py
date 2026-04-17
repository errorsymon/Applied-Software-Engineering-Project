import os
import requests
import time
from urllib.parse import urlparse

from config import BASE_DOWNLOAD_DIR, REQUEST_TIMEOUT
from utils.file_utils import valid_file
from logger import logger

class Downloader:
    def __init__(self, db):
        self.db = db

    def download(self, item):
        url = item.get("url")
        filename = item.get("filename")
        
        if not url or not valid_file(filename):
            return

        repo = item.get("repository", "unknown")
        project_id_str = "".join(c for c in urlparse(url).path if c.isalnum())[:16]
        repo_dir = os.path.join(BASE_DOWNLOAD_DIR, repo)
        local_dir = os.path.join(repo_dir, project_id_str)
        os.makedirs(local_dir, exist_ok=True)
        
        # 1. Register the Project in the Database
        title = item.get("metadata", "Untitled Project")
        db_proj_id = self.db.get_or_create_project(
            repo=repo, 
            project_url=url, 
            title=title, 
            description=title, # Using title as desc if abstract missing
            dl_repo_folder=repo_dir, 
            dl_proj_folder=local_dir
        )
        
        # 2. Add Author and License tables
        if item.get("license"):
            self.db.add_license(db_proj_id, item.get("license"))
        if item.get("uploader"):
            self.db.add_person(db_proj_id, item.get("uploader"), "AUTHOR")

        local_path = os.path.join(local_dir, filename)
        
        # Extractor rule: file_type should just be the extension without the dot
        file_type = os.path.splitext(filename)[1].lstrip('.').lower()

        if os.path.exists(local_path):
            self.db.insert_file(db_proj_id, filename, file_type, "SUCCEEDED")
            return

        # 3. Download the file with tracking statuses
        for attempt in range(3):
            try:
                time.sleep(1.5) 
                logger.info(f"Downloading {filename} (Attempt {attempt + 1})")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
                r = requests.get(url, stream=True, headers=headers, timeout=REQUEST_TIMEOUT)

                if r.status_code == 429:
                    logger.warning(f"Rate limited by {repo}. Sleeping...")
                    time.sleep(15)
                    continue

                if r.status_code != 200:
                    self.db.insert_file(db_proj_id, filename, file_type, "FAILED_SERVER")
                    return

                with open(local_path,"wb") as f:
                    for chunk in r.iter_content(65536):
                        f.write(chunk)

                # Validation Rule: Enum must be 'SUCCEEDED'
                self.db.insert_file(db_proj_id, filename, file_type, "SUCCEEDED")
                return

            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection refused. Waiting...")
                time.sleep(10)
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
                # Validation Rule: Enum must be 'FAILED_SERVER'
                self.db.insert_file(db_proj_id, filename, file_type, "FAILED_SERVER")
                return
        
        self.db.insert_file(db_proj_id, filename, file_type, "FAILED_SERVER")
