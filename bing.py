import requests
import json

class Geocoder:
    """An object for searching for companies using bings's custom search engine API

    Attributes:
    """
    def __init__(self, api_key):
        """The constructor for the address geocoder utilizing bing

        Args:
            api_key (str): The secret key for accessing the api
            api_app_key (str): The id for the custom search engine
        """
        self._session = requests.session()
        self._response = None
        self._api_key = api_key
        self.address = None
        self.result = None

    def search(self, address):
        """Searches for an address

        Args:
            address (str): The address to search for
        Raises:
            Exception: If an invalid Bing key is provided
        """
        self.address = address

        # Conduct search
        # search_api_url = 'http://open.mapquestapi.com/geocoding/v1/address'
        search_api_url = 'http://dev.virtualearth.net/REST/v1/Locations'
        params = {'key': self._api_key, 'q': self.address}
        self._response = self._session.get(search_api_url, params=params)


        # Parse results
        results_data = json.loads(self._response.text)
        if results_data.get('statusCode') != 200:
            raise Exception(results_data.get('statusDescription', 'The request returned a non-success status.'))

        self.result = AddressResult(results_data)

    def write_results(self, write_path):
        """Writes the json response of the google search to a text file

        Args:
            The path to write the file to
        """
        with open(write_path + '.json', 'w') as f:
            f.write(self._response.text)


class AddressResult:
    """An address object

    Attributes:
        street_address (str): The street address. Example: 1 Main St
        neighborhood (str): The neighborhood of the address result
        city (str): The city
        county (str): The county
        state (str): The state
        country (str): The country
        latitude (str): The latitude of the address
        longitude (str): The longitude of the address
        geocode_quality (str): The quality of the result found
        geocode_quality_code (str): The quality of the result found
        side_of_street (str): which side of the street the result is on
    """
    def __init__(self, response):
        self._response = response
        self._location = response.get('resourceSets', [{}])[0].get('resources', [{}])[0].get('address', {})
        self._coordinates = response.get('resourceSets', [{}])[0].get('resources', [{}])[0].get('geocodePoints', [{}])[0].get('coordinates', [None, None])

    @property
    def street_address(self):
        return self._location.get('addressLine')

    @property
    def zip_code(self):
        return self._location.get('postalCode')

    @property
    def neighborhood(self):
        return self._location.get('adminArea6')

    @property
    def city(self):
        return self._location.get('locality')

    @property
    def county(self):
        return self._location.get('adminDistrict2')

    @property
    def state(self):
        return self._location.get('adminDistrict')

    @property
    def country(self):
        return self._location.get('countryRegion')

    @property
    def latitude(self):
        return self._coordinates[0]

    @property
    def longitude(self):
        return self._coordinates[1]

    @property
    def geocode_quality(self):
        return self._response.get('resourceSets', [{}])[0].get('resources', [{}])[0].get('confidence', '')

    @property
    def geocode_quality_code(self):
        return str(self._response.get('resourceSets', [{}])[0].get('resources', [{}])[0].get('matchCodes', str([])))

    def __str__(self):
        return self._location.get('formattedAddress')


if __name__ == "__main__":
    api_key = input('Enter the bing api key: ')
    write_path = input('Enter an output path for the response: ')
    geocoder = Geocoder(api_key)
    geocoder.search('81 1st st N, Paris')
    geocoder.write_results(write_path)
    print(geocoder.result)
    print(geocoder.result.longitude)
    print(geocoder.result.latitude)
    print(geocoder.result.geocode_quality)
    print(geocoder.result.geocode_quality_code)
