import requests
import json
import datetime
import math
import time
import pandas as pd

def list_years(start_date, end_date):
    """Retrieve the years between the provided start date and end date

    :param start_date: The date to start the list at
    :param end_date: The date to end the list at
    :return: A list containing all years between the provided start date and end date
    """
    years = math.ceil((end_date - start_date).days / 365)
    start_year = int(start_date.strftime('%Y'))
    return [start_year + index for index in range(years)]


class StationDataRequest:
    """

    """
    def __init__(self, station_id, api_key):
        """The constructor for a data request for a NOAA station

        :param station_id: The id of the station
        :param api_key: Your NOAA api key
        """
        self._STATION_ID = station_id
        self._API_KEY = api_key
        self._REQUEST_MADE = False
        self._RECORD_COUNT = None
        self._RECORDS_PER_PAGE = None
        self._CURRENT_PAGE = None
        self._PAGES = None
        self._RESULTS = []

    def parse_response(self, request_data):
        """Parase the metadata and results from a station data request

        :param request_data: The parsed json dictionary object from the response
        :return: None
        """
        # parse metadata
        metadata = request_data.get('metadata', {})
        self._RECORD_COUNT = metadata.get('count', 0)
        self._RECORDS_PER_PAGE = metadata.get('limit', 0)
        self._CURRENT_PAGE = metadata.get('offset', 0)
        if self._RECORD_COUNT == 0:
            self._PAGES = 0
        else:
            self._PAGES = math.ceil(self._RECORD_COUNT / self._RECORDS_PER_PAGE)

        #parse results
        self._RESULTS.extend(request_data.get('results', []))

    def request_result_page(self, year, page=None):
        """Get a page of station data from the NOAA api

        :param year: The year of the data
        :param page: Results can contain multiple pages, this is the page to return
        :return: The json from the response parsed as a dictionary object
        """
        url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data/'
        headers = {'token': self._API_KEY}
        parameters = {
            'datatypeid': ['TMIN', 'TMAX', 'TAVG'],
            'stationid': self._STATION_ID,
            'datasetid': 'GHCND',
            'limit': 1000,  # maximum is 1000 https://www.ncdc.noaa.gov/cdo-web/webservices/v2#data,
            'startdate': str(year) + '-01-01',
            'enddate': str(year) + '-12-31'
        }
        if page:
            parameters.update({'offset':page})
        return json.loads(requests.get(url=url, headers=headers, params=parameters).text)

    def get_all_pages(self, year):
        """Retrieve all pages of data collected from a station for a paticular year

        :param year: The year the data is fromo
        :return: None
        """
        time.sleep(.2)
        print('Retrieving ', year, sep='')
        response = self.request_result_page(year)
        self.parse_response(response)
        for page in range(2, self._PAGES + 1):
            response = self.request_result_page(year, page)
            self.parse_response(response)


class Station:
    def __init__(self, station_id, api_key):
        """The constructor for the station object

        :param station_id: The id of the NOAA station
        :param api_key: Your NOAA api key
        """
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
        self.temperature_data = []

    def retrieve_temperature_data(self):
        """Retrieves all the data a station has

        :return:
        """
        request = StationDataRequest(self._STATION_ID, self._API_KEY)
        for year in list_years(self._MIN_DATA_DATE, self._MAX_DATA_DATE):
            request.get_all_pages(year)
        self.temperature_data = request._RESULTS


if __name__ == '__main__':
    token = input('Enter your NOAA token: ')
    station = Station('GHCND:USC00210075', token)
    station.retrieve_temperature_data()
    print(pd.DataFrame(station.temperature_data).head())
