import requests
import json
import pandas as pd
import loop_result
import datetime
import math

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

mindate = datetime.datetime.strptime(location['mindate'], '%Y-%m-%d')
maxdate = datetime.datetime.strptime(location['maxdate'], '%Y-%m-%d')
years = math.ceil((maxdate - mindate).days/365)

start_year = int(mindate.strftime('%Y'))
all_years = [start_year + index for index in range(years)]

params = {
    'datatypeid':['TMIN','TMAX','TAVG'],
    'stationid': location['id'],
    'datasetid':datasetid,
    'limit':200
}
all_weather = []
for year in all_years:
    params.update({
        'startdate':str(year)+'-01-01',
        'enddate':str(year)+'-12-31'
    })
    print(year)
    all_weather.extend(loop_result.get_all_results(
        url='https://www.ncdc.noaa.gov/cdo-web/api/v2/data/',
        headers=headers,
        parameters=params
    ))

all_weather = pd.DataFrame(all_weather)

print(all_weather.head())
# r = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data/', headers = headers, params = params)

def process_json(json_text):
    return json.dumps(json.loads(json_text), indent=3, sort_keys=True)

#print(process_json(r.text))