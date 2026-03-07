import requests


class SiktClient:
    # NSD merged into SIKT. Their active open repository uses the Dataverse framework.
    BASE_URL = "https://dataverse.no/api/search"

    def search(self, query):
        tasks = []
        try:
            # Using the standard Dataverse API search parameters
            params = {
                "q": query,
                "type": "file",  # We want direct files, not just dataset landing pages
                "per_page": 20
            }

            # Added timeout! If the server is unresponsive, it drops out after 15 seconds.
            r = requests.get(self.BASE_URL, params=params, timeout=15)
            r.raise_for_status()

            data = r.json()

            # Safely navigate the JSON response
            for item in data.get("data", {}).get("items", []):
                # Dataverse provides a direct file 'url' and 'name'
                file_url = item.get("url")
                file_name = item.get("name")

                if file_url and file_name:
                    tasks.append({
                        "url": file_url,
                        "filename": file_name,
                        "repository": "sikt"
                    })

        except requests.exceptions.RequestException as e:
            print(f"SIKT connection error: {e}")
        except ValueError:
            print("SIKT error: Received invalid JSON response")
        except Exception as e:
            print(f"SIKT unexpected error: {e}")

        return tasks