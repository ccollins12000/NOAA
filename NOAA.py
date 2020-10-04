import requests
import json
import pandas as pd
import loop_result

token = input('Enter your NOAA token: ')

headers = {
    'token':token
}
parameters = {
    'locationcategoryid':'ST'
}
url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/locations'

response = requests.get(url = url, headers = headers, params=parameters)
parse_response = json.loads(response.text)
states = pd.DataFrame(parse_response['results'])
formatted_reponse = json.dumps(parse_response, indent=3, sort_keys=True)
print(states.iloc[0,4])
url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'
#datasetid = 'NEXRAD2'
#datasetid = 'NEXRAD3'
datasetid = 'GHCND'

parameters = {
    'locationid':states.iloc[0,4],
    'datasetid': datasetid,
    'datatypeid':['TMIN','TMAX','TAVG'],
    'startdate':'2020-09-29'
}
response = requests.get(url = url, headers = headers, params=parameters)
parse_response = json.loads(response.text)
alabama_locations = pd.DataFrame(parse_response['results'])
formatted_reponse = json.dumps(parse_response, indent=3, sort_keys=True)

location = alabama_locations.iloc[0,:]
# location['mindate']
# location['maxdate']
params = {
    'datatypeid':['TMIN','TMAX','TAVG'],
    'stationid': location['id'],
    'datasetid':datasetid,
    'startdate': '2019-01-01',
    'enddate': '2019-12-31'
}

all_weather = loop_result.get_all_results(
    url='https://www.ncdc.noaa.gov/cdo-web/api/v2/data/',
    headers=headers,
    parameters=params
)
print(all_weather)
# r = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data/', headers = headers, params = params)

def process_json(json_text):
    return json.dumps(json.loads(json_text), indent=3, sort_keys=True)

#print(process_json(r.text))