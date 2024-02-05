import asyncio, time, aiohttp, warnings
from pprint import pprint
from Utils import reverse_data
from node import Node
from employee import Employee
from main import getTravelData
import pandas as pd

#read excel
warnings.simplefilter(action='ignore', category=UserWarning)
dfs = pd.read_excel("./DATA.xlsx", sheet_name=None)
#data frames for each sheet 
cat_data = dfs['עיקור חתולים']
emp_data = dfs['עובדים']


address_dict = {}

async def geocode(location : str, address_dict : dict):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = 'AIzaSyBtWeoy_5l6X0HBsiDfmJkr6nsLdUZ6gxw'
    payload = {
        'address' : location,
        'key' : api_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=payload) as response:
            r = await response.json()
            formatted =  r['results'][0]['formatted_address']
            #add the location in hebrew to the dictionary of all addresses

    address_dict[location] = formatted
    
    return formatted



async def create_employee(employee_row, index, employees):
    global address_dict
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
                print(f"invalid node address in row : {index}")

employees = []
nodes = []
async def main():
    employee_tasks = [create_employee(employee_row, index, employees) for index, employee_row in emp_data.iterrows()]
    node_tasks = [create_node(cat_row, index) for index, cat_row in cat_data.iterrows()]

    await asyncio.gather(*employee_tasks, *node_tasks)


t = time.time()
asyncio.run(main())
print(time.time() - t)

print("\n".join(reverse_data(str(node)) for node in nodes))

