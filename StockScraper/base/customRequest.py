import json

from requests import Session, session
from requests.adapters import HTTPAdapter, Retry


class CustomSession:
    def __init__(self, headers: dict = None) -> None:
        self.session = session()
        if headers:
            self.headers = headers
        else:
            self.headers = {}

        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504, 400, 401, 402, 403])

        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.timeout = 30  # timeout for 30 seconds

    def get_session(self) -> Session:
        return self.session

    def hit_and_get_data(self, url: str, params: dict = None) -> dict:
        try:
            if params:
                return self.session.get(url, params=params, headers=self.headers).json()
            else:
                return self.session.get(url, headers=self.headers).json()
        except json.JSONDecodeError:
            return {}
        except Exception as err:
            print(f'Error in connecting to url : {url} Error : {err}')
            return {}