import os
import requests
from datetime import datetime
from urllib.parse import urlparse

from config import BASE_DOWNLOAD_DIR, REQUEST_TIMEOUT
from utils.file_utils import valid_file
from utils.hash_utils import sha256_file
from logger import logger


class Downloader:

    def __init__(self, db):

        self.db = db
        self.session = requests.Session()

    def download(self, item):

        url = item["url"]

        if not url:
            return

        if self.db.exists(url):
            return

        filename = item["filename"]

        if not valid_file(filename):
            return

        repo = item["repository"]

        project_id = "".join(c for c in urlparse(url).path if c.isalnum())[:16]

        local_dir = os.path.join(BASE_DOWNLOAD_DIR, repo, project_id)

        os.makedirs(local_dir, exist_ok=True)

        local_path = os.path.join(local_dir, filename)

        try:

            logger.info(f"Downloading {filename}")

            r = self.session.get(url, stream=True, timeout=REQUEST_TIMEOUT)

            if r.status_code != 200:
                return

            with open(local_path,"wb") as f:

                for chunk in r.iter_content(65536):
                    f.write(chunk)

            file_hash = sha256_file(local_path)

            data = (
                url,
                datetime.now().isoformat(),
                repo,
                filename,
                local_dir,
                item.get("license",""),
                item.get("uploader",""),
                os.path.splitext(filename)[1],
                file_hash
            )

            self.db.insert(data)

        except Exception as e:

            logger.error(e)