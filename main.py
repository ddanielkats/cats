import requests
from pprint import pprint
from Utils import *
from node import Node
from employee import Employee
import time
from typing import List

def getTravelData(origins, destinations):
    origins = [origins] if isinstance(origins, str) else origins
    destinations = [destinations] if isinstance(destinations, str) else destinations

    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'
    max_elements_per_request = 100
    delay_between_requests = 10  # seconds

    num_origins = len(origins)
    num_destinations = len(destinations)
    num_elements = num_origins * num_destinations

    # Calculate the ratio between the number of elements and the max elements per request
    ratio = num_elements / max_elements_per_request

    # Calculate the chunk size for both origins and destinations based on the ratio
    origin_chunk_size  = max(1, round(num_origins / ratio))
    destination_chunk_size = max(1, round(num_destinations / ratio))
    # Split origins and destinations into chunks by the ration
    origin_chunks = [origins[i:i + origin_chunk_size] for i in range(0, num_origins, origin_chunk_size)]
    destination_chunks = [destinations[j:j + destination_chunk_size] for j in range(0, num_destinations, destination_chunk_size)]

    combined_response = {}

    for orig_chunk in origin_chunks:
        for dest_chunk in destination_chunks:
            payload = {
                'origins': '|'.join(orig_chunk),
                'destinations': '|'.join(dest_chunk),
                'key': api_key
            }

            r = requests.get(base_url, params=payload).json()
            combined_response = merge_dicts(combined_response, parse_response(r))

            if ratio >1:
                # Add a delay between requests
                print("waiting 10 secs")
                time.sleep(delay_between_requests)

    write_to_file(combined_response, "Travel_Data.json")

    return combined_response



def calculate_weight(node : Node, employee : Employee) -> float:
    """calculates the weight for a given path between soruce and node
    
    times : Dictionary with origin-location mapping
    node : A cat pickup place
    employee : A given employee
    
    """
    #travel time in minutes
    travel_data = getTravelData(employee.location, node.location)
    #the first value in the first value of travel_data
    travel_time = convert_to_minutes(next(iter(next(iter(travel_data.values()), {}).values()), None))
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
    address = {
        'hebrew' : {}, #english to hebrew
        'english' : {} #hebrew to english
    }
    
    t1 = time.time()

    #create employee objects
    for index, employee_row in emp_data.iterrows():
        emp = Employee(employee_row, address, geocode)
        employees.append(emp)
        origins.append(emp.location)
        

    #create node objects
    for index, pick_request in cat_data.iterrows():
        node = Node(pick_request, address, geocode)
        nodes.append(node)
        destinations.append(node.location)

    print(time.time() - t1)
    employee = Employee(emp_data.iloc[6], address, geocode)
    map_employee(employee, nodes, 5)
    print(employee.stops)

"""
    #calculate the route for each employee into his stops variable
    for employee in employees:
        map_employee(employee, nodes, 5)
        #print(employee.stops)
"""