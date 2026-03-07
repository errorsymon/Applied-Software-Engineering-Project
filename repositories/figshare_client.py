import requests


class FigshareClient:

    BASE_URL = "https://api.figshare.com/v2/articles/search"

    def search(self, query):

        tasks = []

        for page in range(1, 11):

            try:

                params = {
                    "search_for": query,
                    "page": page,
                    "page_size": 20
                }

                r = requests.get(self.BASE_URL, params=params, timeout=20)

                articles = r.json()

                for article in articles:

                    article_id = article.get("id")

                    if article_id:

                        file_url = f"https://api.figshare.com/v2/articles/{article_id}/files"

                        fr = requests.get(file_url)

                        files = fr.json()

                        for f in files:

                            tasks.append({
                                "url": f["download_url"],
                                "filename": f["name"],
                                "repository": "figshare"
                            })

            except:
                pass

        return tasks