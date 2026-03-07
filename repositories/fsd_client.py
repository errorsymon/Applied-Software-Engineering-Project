import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class FSDClient:
    # Using the HTML catalogue endpoint provided in the project document
    BASE_URL = "https://services.fsd.tuni.fi/catalogue/index"

    def search(self, query):
        tasks = []
        try:
            # Query parameters specifically targeting Qualitative data in English
            params = {
                "lang": "en",
                "q": query,
                "data_kind_string_facet": "Qualitative",
                "limit": 50
            }

            # Added timeout to prevent pipeline hanging
            r = requests.get(self.BASE_URL, params=params, timeout=15)
            r.raise_for_status()

            # Parse the HTML response
            soup = BeautifulSoup(r.text, 'html.parser')

            # Extract links from the search results
            for a in soup.find_all('a', href=True):
                href = a['href']

                # Filter for links that look like study/dataset pages or direct files
                if "/catalogue/study/" in href or "/download" in href.lower():
                    full_url = urljoin(self.BASE_URL, href)

                    # FSD filenames are often hidden behind dataset pages,
                    # so we generate a safe fallback name based on the URL
                    safe_name = href.split('/')[-1] if not href.endswith('/') else "fsd_dataset"

                    tasks.append({
                        "url": full_url,
                        "filename": safe_name,
                        "repository": "fsd"
                    })

        except Exception as e:
            # Catching the error cleanly so it returns an empty list instead of crashing
            print(f"FSD error for query '{query}': {e}")

        # Deduplicate tasks based on URL to avoid downloading the same page twice
        unique_tasks = {t['url']: t for t in tasks}.values()
        return list(unique_tasks)