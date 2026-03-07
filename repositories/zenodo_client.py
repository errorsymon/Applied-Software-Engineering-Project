import requests


class ZenodoClient:

    BASE_URL = "https://zenodo.org/api/records"

    def search(self, query):

        tasks = []

        for page in range(1, 11):

            try:

                params = {
                    "q": query,
                    "page": page,
                    "size": 20
                }

                r = requests.get(self.BASE_URL, params=params, timeout=20)
                data = r.json()

                for hit in data.get("hits", {}).get("hits", []):

                    files = hit.get("files", [])

                    for f in files:

                        tasks.append({
                            "url": f["links"]["self"],
                            "filename": f["key"],
                            "repository": "zenodo"
                        })

            except:
                pass

        return tasks