import math
import requests
import json
import time

def get_all_results(url, headers, parameters):
    results = []
    while True:
        # request data
        parameters = parameters.copy()
        response = requests.get(url, headers=headers, params=parameters)
        initial_limit = parameters.get('limit', 0)
        # parse out data from response
        parsed_response = json.loads(response.text)
        metadata = parsed_response.get('metadata', {}).get('resultset', {})

        if not parsed_response.get('results', []):
            print('no results for: ', parameters)
            break

        results.extend(parsed_response.get('results', []))

        # check record counts
        record_count = metadata.get('count')
        limit = metadata.get('limit')
        pages = math.ceil(record_count/limit)
        current_page = metadata.get('offset', 0)

        print('Page ', current_page, ' of ', pages, sep='')
        # setup next iteration
        if not record_count or current_page >= pages:
            break
        parameters.update({'offset': (current_page + 1)})
        # Wait so as not to hit request limit
        time.sleep(0.5)

    return results

