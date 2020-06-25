import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout

import json
from pprint import pprint

def sendGetRequest(url, payload=None, timeout=5):
    response = None
    try:
        if payload is not None:
            response = requests.get(url, params=payload, timeout=timeout)
        else:
            response = requests.get(url, timeout)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Timeout as timeout_err:
        print(f'HTTP error occurred: {timeout_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        # The type of the return value of .json() is a dictionary,
        return response.json()
