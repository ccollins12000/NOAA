import station
import requests
import json


class StationSearch:
    """A object for searching for NOAA stations

    """
    def __init__(self, api_key):
        """The constructor for the NOAA station search

        args:
            api_key (str): Your NOAA api key  You can request a key here: https://www.ncdc.noaa.gov/cdo-web/token

        attributes:
            found_locations (obj): A list object containing all the stations found in the latest search call
        """
        self._API_KEY = api_key
        self._AUTH_HEADER = {'token': api_key}
        self._SEARCH_PARAMS = {
            'datasetid': 'GHCND',
            'datatypeid': 'TAVG'
        }
        self._API_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'
        self.found_locations = []

    def search(self, zip_code):
        """Search for stations in a certain zip code. results are saved to found_locations attribute

        args:
            zip_code (str): The zip code to search within.
        """
        self._SEARCH_PARAMS.update({'locationid': 'ZIP:{zip_code}'.format(zip_code = str(zip_code))})
        self.found_locations = []

        print('making request')
        response = requests.get(url=self._API_URL, headers=self._AUTH_HEADER, params=self._SEARCH_PARAMS)

        print('parsing request')
        response_parsed = json.loads(response.text)
        results = response_parsed['results']

        for noaa_station in results:
            self.found_locations.append(station.Station(noaa_station['id'], token, noaa_station))

    def return_station(self, station_index=0):
        """Return a station from the results of the last search call

        args:
            station_index (int): The index of the station in the results
        """
        if len(self.found_locations) > 0:
            return self.found_locations[station_index]
        else:
            return None


if __name__ == "__main__":
    token = input('Enter your NOAA token: ')
    zip_code = input('Enter a zipcode: ')

    StationSearcher = StationSearch(api_key=token)
    StationSearcher.search(zip_code)

    station_found = StationSearcher.return_station(station_index=0)
    print(station_found.station_name)
