import requests


class DataverseClient:

    BASE_URL = "https://dataverse.harvard.edu/api/search"

    def search(self, query):

        tasks = []

        for start in range(0, 200, 20):

            try:

                params = {
                    "q": query,
                    "type": "file",
                    "start": start
                }

                r = requests.get(self.BASE_URL, params=params, timeout=20)

                data = r.json()

                items = data.get("data", {}).get("items", [])

                for item in items:

                    url = item.get("url")

                    if url:

                        tasks.append({
                            "url": url,
                            "filename": url.split("/")[-1],
                            "repository": "dataverse"
                        })

            except:
                pass

        return tasks