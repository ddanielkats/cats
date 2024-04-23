import pandas as pd
from datetime import datetime, timedelta
import math
import warnings
import aiohttp
import re




#---------------------HERE LYE FUNCTIONS THAT DON'T ARE USED ELSEWHERE--------------------------

def delete_after_comma(input_str):
    if ',' in input_str:
        index_of_comma = input_str.index(',')
        result_str = input_str[:index_of_comma]
        return result_str
    else:
        return input_str
    
    


def reverse_data(input_data):
    # Function to reverse a string
    def reverse_string(s):
        return s[::-1]

    if isinstance(input_data, pd.DataFrame):
        # Use applymap to reverse all strings in the DataFrame
        reversed_df = input_data.applymap(lambda x: reverse_string(x) if isinstance(x, str) else x)
        # Reverse columns
        reversed_df.columns = [reverse_string(col) for col in reversed_df.columns]
        return reversed_df
    elif isinstance(input_data, pd.Series):
        # Use map to reverse all strings in the Series
        reversed_series = input_data.map(lambda x: reverse_string(x) if isinstance(x, str) else x)
        # Reverse the Series name
        reversed_series.name = reverse_string(str(input_data.name)) if isinstance(input_data.name, str) else input_data.name
        # Reverse the index (row names)
        reversed_series.index = reversed_series.index.map(reverse_string)
        return reversed_series
    elif isinstance(input_data, str):
        return reverse_string(input_data)
    
    elif isinstance(input_data, list):
        return [reverse_data(subitem) for subitem in input_data]
    else:
        raise ValueError("Input must be a DataFrame or a Series")


def convert_to_minutes(time_string):
    """convert a time string that looks like '3 hours 12 mins' or '18 mins' to pure minutes"""
    # Split the string into parts using space as the delimiter
    parts = time_string.split()

    if len(parts) == 4 and parts[1] == 'hours' and parts[3] in('min', 'mins'):
        try:
            # Extract hours and minutes from the parts and convert to integers
            hours = int(parts[0])
            minutes = int(parts[2])

            # Convert hours to minutes and add to total minutes
            total_minutes = hours * 60 + minutes
            return total_minutes
        except ValueError:
            print("Invalid time format: Non-integer values detected.")
            return None
    elif len(parts) == 2 and parts[1] in('min', 'mins'):
        try:
            # Extract minutes from the parts and convert to integers
            minutes = int(parts[0])

            # Return the total minutes
            return minutes
        except ValueError:
            print("Invalid time format: Non-integer values detected.")
            return None
    else:
        print("Invalid time format")
        return None

def parse_time(time_str):
    formats = ['%H:%M', '%I:%M', '%H.%M']
    for fmt in formats:
        try:
            time_obj = datetime.strptime(time_str, fmt)
            return time_obj.strftime('%H:%M')  
        except ValueError:
            pass
    return None


def calculate_future_delta(start_time, travel_time, target_hour):
    """returns the time difference in minutes from the time of arrival to the target hour in that day
    start_time : datetime
    travel_time : time in minutes
    target_hour : like 7:00
    """

    if target_hour == 0:
        return 0

    #regex find hour in string
    match = re.search("[0-9]{1,2}[\.:][0-9]{1,2}", target_hour)
    if match is not None:
        target_hour = match.group()
    else:
        return 0
    
    
    # Calculate arrival time
    arrival_time = start_time + timedelta(minutes=travel_time)

    # Get the current date
    current_date = datetime.now().date()
    # Convert the input time string to a datetime object
    target_time = datetime.strptime(f"{current_date} {target_hour}", "%Y-%m-%d %H:%M")
    # Calculate the time difference in minutes
    time_difference_minutes = (arrival_time - target_time).total_seconds() / 60

    return round(abs(time_difference_minutes))


def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            dict1[key] = merge_dicts(dict1[key], value)
        else:
            # Overwrite or add key-value pair
            dict1[key] = value
    return dict1


async def geocode(location : str, address_dict : dict):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = 'AIzaSyA80vzxwbDBiJzq4l6kPXnoV5wfmFmfha8'
    payload = {
        'address' : location,
        'key' : api_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=payload) as response:
            r = await response.json()
            print(r)
            formatted =  r['results'][0]['formatted_address']
            #add the location in hebrew to the dictionary of all addresses

    address_dict[location] = formatted
    
    return formatted


def get_time(origin, destination, travel_dict, key_seperator):
    #check if the travel time is already searched
    if origin == destination:
        return "0 mins"
    
    keys = [origin + key_seperator + destination, destination + key_seperator + origin]
    for key in keys:
        if key in travel_dict:
            return travel_dict[key]
    return False

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 


