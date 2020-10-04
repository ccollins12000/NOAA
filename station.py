import requests
import json
import datetime


class Station:
    def __init__(self, station_id, api_key):
        # setup control attributes
        self._API_KEY = api_key
        self._STATION_ID = station_id
        self._STATION_DATA_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{station_id}'
        self._STATION_DATA_URL = self._STATION_DATA_URL.format(station_id=self._STATION_ID)
        self._TEMP_DATA_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data/'

        # request station description data
        self._AUTH_HEADER = {'token':self._API_KEY}
        self._STATION_DATA = requests.get(url=self._STATION_DATA_URL, headers=self._AUTH_HEADER)
        self._STATION_DATA = json.loads(self._STATION_DATA.text)

        # populate station data
        if self._STATION_DATA.get('id', None) is None:
            raise Exception(str(self._STATION_ID) + ' was not found')

        self._MIN_DATA_DATE = datetime.datetime.strptime(self._STATION_DATA.get('mindate'), '%Y-%m-%d')
        self._MAX_DATA_DATE = datetime.datetime.strptime(self._STATION_DATA.get('maxdate'), '%Y-%m-%d')
        self.latitude = self._STATION_DATA.get('latitude', None)
        self.longitude = self._STATION_DATA.get('longitude', None)
        self.station_name = self._STATION_DATA.get('name', None)