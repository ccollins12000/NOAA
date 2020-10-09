import station
import requests
import json


class StationSearch:
    def __init__(self, api_key):
        self._API_KEY = api_key
        self._AUTH_HEADER = {'token': api_key}
        self._SEARCH_PARAMS = {
            'datasetid': 'GHCND',
            'datatypeid': 'TAVG'
        }
        self._API_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'
        self.found_locations = []

    def search(self, zip_code):
        self._SEARCH_PARAMS.update({'locationid': 'ZIP:{zip_code}'.format(zip_code = str(zip_code))})
        self.found_locations = []

        print('making request')
        response = requests.get(url=self._API_URL, headers=self._AUTH_HEADER, params=self._SEARCH_PARAMS)

        print('parsing request')
        response_parsed = json.loads(response.text)
        results = response_parsed['results']

        for noaa_station in results:
            print(noaa_station['id'])
            self.found_locations.append(station.Station(noaa_station['id'], token, noaa_station))

    def return_station(self, station_index):
        return self.found_locations[station_index]


if __name__ == "__main__":
    token = input('Enter your NOAA token: ')

    StationSearcher = StationSearch(api_key=token)
    StationSearcher.search('55105')

    station_found = StationSearcher.return_station(station_index=0)
    print(station_found.station_name)
