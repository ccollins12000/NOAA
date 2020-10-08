import requests
import json
import datetime
import math
import time
import pandas as pd
from dateutil import parser


def list_years(start_date, end_date):
    """Retrieve the years between the provided start date and end date

    args:
        start_date (datetime): The date to start at
        end_date (datetime): The date to end at

    returns:
        A list of integers containing all years between the provided start and end ate
    """
    years = math.ceil((end_date - start_date).days / 365)
    start_year = int(start_date.strftime('%Y'))
    return [start_year + index for index in range(years)]


class StationDataRequest:
    """An object for requesting data from the NOAA about a station

    attributes:
        _RESULTS (obj); A List object containing all of the results retrieved
    """
    def __init__(self, station_id, api_key):
        """The constructor for a data request for a NOAA station

        args:
            station_id (str): The id of the NOAA station. Example GHCND:USC00210075. Stations can be searched for at https://www.ncdc.noaa.gov/data-access/land-based-station-data/find-station
            api_key (str): Your NOAA api key. You can request a key here: https://www.ncdc.noaa.gov/cdo-web/token
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
        """Parase the metadata and results from a station data request. Updates the page attributes of the DataRequest object

        args:
            request_data (obj): A parsed json response
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

        args:
            year (int): The year of data to retrieve
            page (int): Which page of data to retrieve

        returns:
            The reponse text as parsed json
        """
        url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data/'
        headers = {'token': self._API_KEY}
        parameters = {
            #'datatypeid': ['TMIN', 'TMAX', 'TAVG'],
            'datatypeid': ['TMIN', 'TMAX', 'TAVG'],
            'units': 'standard',
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
        """Retrieve all pages of data collected from a station for a particular year

        args:
            year(int): The year of data to retrieve
        """
        # pause in order to not hit requests per second limit
        time.sleep(.2)
        print('Retrieving ', year, sep='')
        response = self.request_result_page(year)
        self.parse_response(response)
        for page in range(2, self._PAGES + 1):
            response = self.request_result_page(year, page)
            self.parse_response(response)


class Station:
    """An object for an NOAA station

    attributes:
        latitude (str): The latitude the station is located at.
        longitude (str): the longitude the station is located at
        station_name (str): The name of the station
        temperature_data (obj): The temperature data the station has collected as a list object. Data must be retrieved using the retrieve_temperature_data method
    """
    def __init__(self, station_id, api_key):
        """The constructor for the station object

        args:
            station_id (str): The id of the NOAA station. Example GHCND:USC00210075. Stations can be searched for at https://www.ncdc.noaa.gov/data-access/land-based-station-data/find-station
            api_key (str): Your NOAA api key. You can request a key here: https://www.ncdc.noaa.gov/cdo-web/token
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

    def retrieve_temperature_data(self, start_year=None, end_year=None):
        """Retrieves all the data a station has. Data is populated to the temperature_data attribute

        """
        request = StationDataRequest(self._STATION_ID, self._API_KEY)
        if start_year is None:
            start_year = self._MIN_DATA_DATE
        if end_year is None:
            end_year = self._MAX_DATA_DATE
        for year in list_years(start_year, end_year):
            request.get_all_pages(year)
        self.temperature_data = request._RESULTS


if __name__ == '__main__':
    token = input('Enter your NOAA token: ')
    station = Station('GHCND:USC00210075', token)
    station.retrieve_temperature_data(datetime.date(2020,1,1),datetime.date(2020,1,2))
    df = pd.DataFrame(station.temperature_data)

    df['date'] = df['date'].apply(lambda x: parser.parse(x))
    print(df.head())
