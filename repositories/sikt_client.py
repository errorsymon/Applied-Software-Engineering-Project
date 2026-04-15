import requests
from bs4 import BeautifulSoup
import time


class FSDClient:
    BASE_URL = "https://services.fsd.tuni.fi/catalogue/index"

    def search(self, query):
        tasks = []
        page = 1

        print(f"Starting FSD search for: {query}")

        # FSD drops requests from Python bots. We must mimic a real browser!
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        while page <= 10:
            try:
                params = {
                    "lang": "en",
                    "q": query,
                    "data_kind_string_facet": "Qualitative",
                    "page": page
                }

                r = requests.get(self.BASE_URL, params=params, headers=headers, timeout=15)
                if r.status_code != 200:
                    break

                soup = BeautifulSoup(r.text, 'html.parser')
                study_links = soup.select('a[href^="/catalogue/study/FSD"]')

                if not study_links:
                    break

                for a in study_links:
                    href = a['href']
                    study_id = href.split('/')[-1]
                    title = a.text.strip()

                    xml_url = f"https://services.fsd.tuni.fi/catalogue/{study_id}/DDI/{study_id}_eng.xml"

                    tasks.append({
                        "url": xml_url,
                        "filename": f"{study_id}_metadata.xml",
                        "repository": "fsd",
                        "metadata": title
                    })

                page += 1
                time.sleep(1.5)  # Polite delay for FSD servers

            except Exception as e:
                print(f"FSD scraper error: {e}")
                break

        unique_tasks = {t['url']: t for t in tasks}.values()
        return list(unique_tasks)
