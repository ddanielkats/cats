import requests
from pprint import pprint
from Utils import *
from node import Node
from employee import Employee
import time
from typing import List

data_path = "./Travel_data.json"
key_seperator = "    <---->    "
try:
    with open(data_path, 'r') as file:
        travel_dict = json.load(file)
except json.decoder.JSONDecodeError:
    travel_dict = {}  # Set a default dictionary or take another appropriate action


def getTravelData(origin, destination):
    global travel_dict

    #check if the travel time is already searched
    keys = [origin + key_seperator + destination, destination + key_seperator + origin]
    for key in keys:
        if key in travel_dict:
            return travel_dict[key]

    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'    
    payload = {
                'origins': origin,
                'destinations': destination,
                'key': api_key
            }
    
    r = requests.get(base_url, params=payload).json()
    time = r["rows"][0]["elements"][0]["duration"]["text"]
    
    #add origin-destination pair to travel_dict
    travel_dict[keys[0]] = time
    #update the json file
    with open(data_path, 'w') as file:
        json.dump(travel_dict, file, indent=2)

    
    return time



def calculate_weight(node : Node, employee : Employee) -> float:
    """calculates the weight for a given path between soruce and node
    
    times : Dictionary with origin-location mapping
    node : A cat pickup place
    employee : A given employee
    
    """
    #travel time in minutes
    travel_data = getTravelData(employee.location, node.location)
    #the first value in the first value of travel_data
    travel_time = convert_to_minutes(travel_data)
    #days since cat request in days
    days_since = (datetime.now() - node.created_on).days
    #how close will the employee be to the feeding time in minutes
    proximity_to_feeding = calculate_future_delta(datetime.now(), travel_time, node.feed_time)

    #assign weighs for each variable
    weight_travel_time = 0.6
    weight_days_since = -0.2
    weight_proximity_to_feeding = -0.2

    # Apply exponential transformation to days_since
    exponential_days_since = 2 ** days_since

    # Calculate the weighted sum
    weighted_sum = (
        weight_travel_time * travel_time +
        weight_days_since * exponential_days_since +
        weight_proximity_to_feeding * proximity_to_feeding
    )

    #lower sum = lower priorty
    return weighted_sum

def map_employee(emp : Employee, nodes : List[Node], max_stops : int): 
    """maps all the stops for a given empoloyee by the closest(lowest weight) stop first"""
    if max_stops == 0:
        return
    
    curr_node = None
    min_weight = float('inf')

    for node in nodes:
        weight = calculate_weight(node, employee)
        if weight <= min_weight:
            min_weight = weight
            curr_node = node
    
    emp.add_stop(curr_node.location)
    emp.location = curr_node.location
    # Exclude the current node from the list before making the recursive call
    nodes.remove(curr_node)

    map_employee(emp, nodes, max_stops - 1)

if __name__ == "__main__":
    employees = []
    origins = []
    destinations = []
    nodes = []
    address_dict = {
    
    }
    
    t1 = time.time()

    #create employee objects
    for index, employee_row in emp_data.iterrows():
        emp = Employee(employee_row, address_dict, geocode)
        employees.append(emp)
        origins.append(emp.location)
        

    #create node objects
    for index, pick_request in cat_data.iterrows():
        node = Node(pick_request, address_dict, geocode)
        nodes.append(node)
        destinations.append(node.location)

    print(f'time for object creation :  {round(time.time() - t1, 2)} sec')
    t2 = time.time()
    employee = Employee(emp_data.iloc[6], address_dict, geocode)
    map_employee(employee, nodes, 5)
    print(employee.stops)
    print(f'time for mapping :  {round(time.time() - t2, 2)} sec')

"""
    #calculate the route for each employee into his stops variable
    for employee in employees:
        map_employee(employee, nodes, 5)
        #print(employee.stops)
"""