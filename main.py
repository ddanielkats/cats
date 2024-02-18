import time, json, asyncio, aiohttp
from Utils import *
from node import Node
from employee import Employee
from typing import List
from asyncio import Semaphore

#read excel
warnings.simplefilter(action='ignore', category=UserWarning)
dfs = pd.read_excel("./DATA.xlsx", sheet_name=None)
#data frames for each sheet 
cat_data = dfs['עיקור חתולים']
emp_data = dfs['עובדים']
address_dict = {
    
    }
sem = Semaphore(500)

data_path = "./Travel_data.json"
key_seperator = "    <---->    "
try:
    with open(data_path, 'r') as file:
        travel_dict = json.load(file)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    travel_dict = {}

async def calculateTravelData(origin, destination,session,  travel_dict = travel_dict):
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
    
    
    async with (sem, session.get(base_url, params=payload) as response):
        r = await response.json()
        time = r["rows"][0]["elements"][0]["duration"]["text"]

    
    #add origin-destination pair to travel_dict
    travel_dict[origin + key_seperator + destination] = time
    





def calculate_weight(node : Node, employee : Employee, travel_dict : dict) -> float:
    """calculates the weight for a given path between soruce and node
    
    node : A cat pickup place
    employee : A given employee
    travel_dict : a dictionary with travel time values
    
    """
    #travel time in minutes
    travel_time = convert_to_minutes(get_time(employee.location, node.location, travel_dict, key_seperator))
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

def map_employee(emp : Employee, nodes : List[Node],travel_dict : dict, max_stops : int): 
    """maps all the stops for a given empoloyee by the closest(lowest weight) stop first"""
    if max_stops == 0 or len(nodes) == 0:
        return
    
    curr_node = None
    min_weight = float('inf')

    for node in nodes:
        weight = calculate_weight(node, emp, travel_dict)
        if weight <= min_weight:
            min_weight = weight
            curr_node = node
    emp.add_stop(curr_node.location)
    emp.location = curr_node.location
    # Exclude the current node from the list before making the recursive call
    nodes.remove(curr_node)

    map_employee(emp, nodes, travel_dict, max_stops - 1)








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


async def calculate_all_routes(emp_locations, node_locations, td = travel_dict):
    tasks = []
    #maps all possible routes
    pairs = set()
    i = 0
    async with aiohttp.ClientSession() as session:
        for origin in node_locations:
            for dest in emp_locations + node_locations:
                    keys = [f"{origin}{key_seperator}{dest}", f"{dest}{key_seperator}{origin}"]
                    if origin != dest and not (keys[0] in pairs or keys[1] in pairs):
                        print(f"tasking #{i}")
                        tasks.append(calculateTravelData(origin, dest, session, td))
                        pairs.add(keys[0])
                        i+=1

        k = 1
        time_to_sleep = 60 if len(tasks) > 59000 else 0
        for chunk in divide_chunks(tasks, 59000):
            print(f"chunk #{k}")
            await asyncio.gather(*chunk, asyncio.sleep(time_to_sleep))
            k+=1



async def main(employees, nodes, travel_dict):
    #----------------------------------------------------------
    #object creation timer
    t1 = time.time() 
    await asyncio.gather(*create_objects(employees, nodes, address_dict))
    print(f'time for object creation :  {round(time.time() - t1, 2)} sec\n')
    #------------------------------------------------------------

    t2 = time.time()
    #calculate the route for each employee into his stops variable
    await calculate_all_routes([employee.location for employee in employees], [node.location for node in nodes])
    print(f'time for calculating routes :  {round(time.time() - t2, 2)} sec')
    
    #update the json file
    travel_dict = dict(sorted(travel_dict.items()))
    with open(data_path, 'w') as file:
        json.dump(travel_dict, file, indent=2)

    print("mapping employees ------------------------")
    t3 = time.time()
    for employee in employees:
        map_employee(employee, nodes, travel_dict, 3)
    
    
    print(f'time for mapping :  {round(time.time() - t3, 2)} sec')
    #------------------------------------------------------------


if __name__ == '__main__':
    employees = []
    nodes = []
    
    asyncio.run(main(employees, nodes, travel_dict))
    
    result_dict = {}
    for employee in employees:
        result_dict[employee.name] = employee.stops
    df = pd.DataFrame.from_dict(result_dict, orient='index')
    df = df.transpose()
    df.to_excel('./result.xlsx')
