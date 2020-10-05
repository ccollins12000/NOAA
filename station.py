import requests
import json
import datetime
import math
import time
import pandas as pd


class StationDataRequest:
    def __init__(self, station_id, api_key, start_date, end_date):
        # Request parameters and headers
        self._API_KEY = api_key
        self._PARAMETERS = {
            'datatypeid': ['TMIN', 'TMAX', 'TAVG'],
            'stationid': station_id,
            'datasetid': 'GHCND',
            'limit': 1000  # maximum is 1000 https://www.ncdc.noaa.gov/cdo-web/webservices/v2#data
        }
        self._BASE_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data/'

        # Paging variables
        self._METADATA = {}
        self._RECORDS_PER_PAGE = 0
        self._CURRENT_PAGE = 0
        self._RECORD_COUNT = 0
        self._START_DATE = start_date
        self._END_DATE = end_date

        #Results
        self._RESPONSE = None
        self._RESPONSE_PARSED = None

    def _parse_metadata(self, metadata):
        self._RECORD_COUNT = metadata.get('count', 0)
        self._RECORDS_PER_PAGE = metadata.get('limit', 0)
        self._CURRENT_PAGE = metadata.get('offset', 0)

    def _get_next_result_set(self, year, page=None):
        # Setup page to retrieve
        if page is None:
            page = self._CURRENT_PAGE + 1
        params = self._PARAMETERS.copy()
        params.update({
            'offset': page,
            'startdate': str(year)+'-01-01',
            'enddate': str(year)+'-12-31'
        })

        # Request data
        self._RESPONSE = requests.get(
            url=self._BASE_URL,
            headers={'token': self._API_KEY},
            params=params
        )

        # Parse response
        print(self._RESPONSE.text)
        self._RESPONSE_PARSED = json.loads(self._RESPONSE.text)
        self._parse_metadata(self._RESPONSE_PARSED.get('metadata', {}))
        return self._RESPONSE_PARSED.get('results', [])

    def fetch_all_results(self):
        results = []

        years = math.ceil((self._END_DATE - self._START_DATE).days / 365)

        start_year = int(self._START_DATE.strftime('%Y'))
        all_years = [start_year + index for index in range(years)]

        for year in all_years:
            while True:
                results.extend(self._get_next_result_set(year))
                if self._RECORD_COUNT == 0:
                    break
                if self._CURRENT_PAGE >= self._RECORD_COUNT/self._RECORDS_PER_PAGE:
                    break
                print('Next Page')
                print(self._CURRENT_PAGE, ':', self._RECORD_COUNT/self._RECORDS_PER_PAGE, sep='')
                time.sleep(0.5)
        return results


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
        self.temp_data = []

    def retrieve_temperature_data(self):
        request = StationDataRequest(self._STATION_ID, self._API_KEY, self._MIN_DATA_DATE, self._MAX_DATA_DATE)
        self.temp_data = request.fetch_all_results()


if __name__ == '__main__':
    token = input('Enter your NOAA token: ')
    station = Station('GHCND:USC00210075', token)
    station.retrieve_temperature_data()
    print(pd.DataFrame(station.temp_data).head())
