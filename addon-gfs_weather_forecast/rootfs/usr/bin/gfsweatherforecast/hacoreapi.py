from requests import get
from typing import Any
from logger import logger
import json
import time

class HACoreApi:
    _api_token: str
    _api_url: str = 'http://supervisor/core/api'
    _sensor_data: dict[str, Any] = {}

    def __init__(self, api_token: str) -> None:
        self._api_token = api_token

    def __get_api_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json"
        }
        return headers

    def get_gps_position(self) -> tuple[float, float]:
        url = f'{self._api_url}/config'
        headers = self.__get_api_headers()
        count = 0
        while count < 3:
            response = get(url, headers=headers)
            if response.status_code in [200, 201]:
                data = json.loads(response.text)
                logger.info(f'Found gps location {data["latitude"]} {data["longitude"]}')
                return data['latitude'], data['longitude']
            else:
                time.sleep(1)
            count += 1
        raise ValueError('Could not acquire gps location')