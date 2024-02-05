import requests_async as requests, time, json, asyncio, aiohttp
from pprint import pprint
from Utils import *
from node import Node
from employee import Employee
from typing import List

#read excel
warnings.simplefilter(action='ignore', category=UserWarning)
dfs = pd.read_excel("./SAMPLE.xlsx", sheet_name=None)
#data frames for each sheet 
cat_data = dfs['עיקור חתולים']
emp_data = dfs['עובדים']
address_dict = {
    
    }

data_path = "./Travel_data.json"
key_seperator = "    <---->    "
try:
    with open(data_path, 'r') as file:
        travel_dict = json.load(file)
except json.decoder.JSONDecodeError:
    travel_dict = {}  # Set a default dictionary or take another appropriate action

num = 0
async def getTravelData(origin, destination):
    global travel_dict, num
    #check if the travel time is already searched
    
    t = get_time(origin, destination, travel_dict, key_seperator)
    if (t == 0 and t is not False):
        travel_dict[origin + key_seperator + destination] = t
        return t
    elif t:
        return t

    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'    
    payload = {
                'origins': origin,
                'destinations': destination,
                'key': api_key
            }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=payload) as response:
            r = await response.json()
            num += 1
            print(f"GOT RESPONSE #{num}: {origin} + {key_seperator} + {destination}")
            time = r["rows"][0]["elements"][0]["duration"]["text"]
    
    
    #add origin-destination pair to travel_dict
    travel_dict[origin + key_seperator + destination] = time
    
    return time





def calculate_weight(node : Node, employee : Employee) -> float:
    """calculates the weight for a given path between soruce and node
    
    times : Dictionary with origin-location mapping
    node : A cat pickup place
    employee : A given employee
    
    """
    #travel time in minutes
    travel_time = convert_to_minutes(travel_dict[employee.location + key_seperator + employee.location])
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
    if len(nodes) == 0:
        print("no more nodes")
        return
    
    curr_node = None
    min_weight = float('inf')

    for node in nodes:
        weight = calculate_weight(node, emp)
        if weight <= min_weight:
            min_weight = weight
            curr_node = node
    emp.add_stop(curr_node.location)
    emp.location = curr_node.location
    # Exclude the current node from the list before making the recursive call
    nodes.remove(curr_node)

    map_employee(emp, nodes, max_stops - 1)



def map_employee_wrapper(employee, nodes, max_stops):
    t2 = time.time() #employee mapping timer
    map_employee(employee, nodes, max_stops)
    print(f'''
    time for {reverse_data(employee.name)}                 :   {round(time.time() - t2, 2)}
    origin                                :   {employee.start_location}  
    stops                                 :   {employee.stops}
    ''')




#code all locations of both employees and nodes
def create_objects(employees, nodes, address_dict):
    threads = []
    #create employee objects
        
    async def create_employee(employee_row, index):
        try:
            coded_address = await geocode(employee_row['כתובת תחילה'], address_dict)
            emp = Employee(employee_row, coded_address)
            employees.append(emp)
        except IndexError:
            print(f"invalid employee address in row: {index}")

    async def create_node(node_row, index):
            try:
                hebrew_location = ' '.join(str(node_row[column]) for column in ['יישוב הפנייה', 'רחוב הפנייה', 'מס בית הפנייה'] if not pd.isna(node_row[column]))
                coded_address = await geocode(hebrew_location, address_dict)
                node = Node(node_row, coded_address)
                nodes.append(node)
            except IndexError:
                print(f"invalid node in row : {index}")

    employee_tasks = [create_employee(employee_row, index) for index, employee_row in emp_data.iterrows()]
    node_tasks = [create_node(cat_row, index) for index, cat_row in cat_data.iterrows()]

    return (*employee_tasks, *node_tasks)


def get_all_routes(emp_locations, node_locations):
    tasks = []
    #maps all possible routes
    for origin in node_locations:
        for dest in emp_locations:
            
            tasks.append(getTravelData(origin, dest))
    return tasks

async def main():
    employees = []
    nodes = []
    

    #----------------------------------------------------------
    #object creation timer
    t1 = time.time() 
    tasks = create_objects(employees, nodes, address_dict)
    await asyncio.gather(*tasks)
    print(f'time for object creation :  {round(time.time() - t1, 2)} sec\n')
    #------------------------------------------------------------

    #time for mapping of all employees
    t3 = time.time()
    #calculate the route for each employee into his stops variable
    await asyncio.gather(*get_all_routes([employee.location for employee in employees], [node.location for node in nodes]))
    
    #update the json file
    with open(data_path, 'w') as file:
        json.dump(travel_dict, file, indent=2)

    for employee in employees:
        map_employee_wrapper(employee, nodes, 5)
    
    
    print(f'time for mapping :  {round(time.time() - t3, 2)} sec')
    #------------------------------------------------------------


if __name__ == '__main__':

    asyncio.run(main())
    