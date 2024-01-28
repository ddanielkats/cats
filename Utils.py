import requests
import json
import pandas as pd
from datetime import datetime, timedelta

#-------------------------constants to be used in main----------------------------------
#read excel
dfs = pd.read_excel("./CAT_DATA.xlsx", sheet_name=None)
#data frames for each sheet 
cat_data = dfs['עיקור חתולים']
emp_data = dfs['עובדים']


#print(cat_data['נוצר ב:'])
#print(cat_data['שם הפונה'])
#print(cat_data['יישוב הפנייה'])
#print(cat_data['רחוב הפנייה'])
#print(cat_data['מס בית הפנייה'])
#print(cat_data['שעות האכלה'])


#times = getTravelData(['nof hagalil', 'tel aviv'], ['eilat', 'miatzpe ramon'])
#pprint(times)

#---------------------HERE LYE FUNCTIONS THAT DON'T DEPEND ON EACH OTHER AND ARE USED ELSEWHERE--------------------------

def delete_after_comma(input_str):
    if ',' in input_str:
        index_of_comma = input_str.index(',')
        result_str = input_str[:index_of_comma]
        return result_str
    else:
        return input_str
    

def write_to_file(jsn, path):
    with open(path, 'w') as f:
        json.dump(jsn, f)


def parse_response(response):
    parsed = {}
    #each row in row list
    for origin in response["origin_addresses"]:
        org_indx = response["origin_addresses"].index(origin)
        elements = response["rows"][org_indx]["elements"]
        #each element in element list
        for destination in response["destination_addresses"]:
            dest_indx = response["destination_addresses"].index(destination)
            duration = elements[dest_indx]["duration"]["text"]
            # Use the origin-destination pair as the keys in the parsed dictionary
            if not origin in parsed:
                parsed[origin] = {}
            parsed[origin][destination] = duration

    return parsed

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

    if len(parts) == 4 and parts[1] == 'hours' and parts[3] == 'min':
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
    elif len(parts) == 2 and parts[1] == 'mins':
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


def calculate_future_delta(start_time, travel_time, target_hour):
    """returns the time difference in minutes from the time of arrival to the target hour in that day
    start_time : datetime
    travel_time : time in minutes
    target_hour : like 7:00
    """
    
    
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


def geocode(location : str):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'
    payload = {
        'address' : location,
        'key' : api_key
    }
    r = requests.get(base_url, params=payload).json()
    
    return r['results'][0]['formatted_address']


def add_address(adress_dict : dict, hebrew_location : str, coded_location : str):
    """adds an adress to a hebrew - english dictionary in both ways
    hebrew_location : location in hebrew from the excel
    coded_location : google maps location
    
    """

    adress_dict['english'][hebrew_location] = coded_location
    adress_dict['hebrew'][coded_location] = hebrew_location