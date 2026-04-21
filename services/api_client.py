import requests
from config.settings import settings

class API_Client:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.headers = {"api_key": settings.API_KEY}

    def get_links(self):
        response = requests.get(f"{self.base_url}/links", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_monitoring_data(self):
        response = requests.get(f"{self.base_url}/monitoring", headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data[0] if isinstance(data, list) else data