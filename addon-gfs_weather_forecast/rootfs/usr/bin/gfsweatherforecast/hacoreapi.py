from requests import get
from typing import Any
from logger import logger
import json
import time
from zoneinfo import ZoneInfo

class HACoreApi:
    _api_token: str
    _api_url: str = 'http://supervisor/core/api'
    _sensor_data: dict[str, Any] = {}
    _latitude: float
    _longitude: float
    _time_zone: str

    def __init__(self, api_token: str) -> None:
        self._api_token = api_token
        self._get_HA_config()

    def __get_api_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json"
        }
        return headers

    def _get_HA_config(self):
        url = f'{self._api_url}/config'
        headers = self.__get_api_headers()
        count = 0
        while count < 3:
            response = get(url, headers=headers)
            if response.status_code in [200, 201]:
                data = json.loads(response.text)
                logger.info(f'Found gps location {data["latitude"]} {data["longitude"]}')
                self._latitude = data['latitude']
                self._longitude = data['longitude']
                self._time_zone = data['time_zone']
                return
            else:
                time.sleep(1)
            count += 1
        raise ValueError('Could not acquire HA config')
    
    def get_gps_position(self) -> tuple[float, float]:
        return self._latitude, self._longitude
    
    def get_zone_info(self) -> ZoneInfo:
        return ZoneInfo(self._time_zone)