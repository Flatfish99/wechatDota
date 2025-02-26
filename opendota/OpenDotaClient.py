import requests

class OpenDotaClient:
    def __init__(self, timeout=10):
        self.base_url = "https://api.opendota.com/api"
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # 自动处理HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None