"""import asyncio, time, aiohttp, warnings
from pprint import pprint
from Utils import reverse_data
from node import Node
from employee import Employee
from main import calculateTravelData
import pandas as pd"""
import requests, re


def geocode(location : str, ):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'
    payload = {
        'address' : location,
        'language' : "en",
        'key' : api_key
    }
    
    r = requests.get(base_url, params=payload).json()
    formatted =  r['results'][0]['formatted_address']
    #add the location in hebrew to the dictionary of all addresses

    
    return formatted


#regex test
match = re.search("[0-9]{1,2}[\.:][0-9]{1,2}", "18:30-19:00 יום א +ה")
print(match.group())