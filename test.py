import requests
from pprint import pprint
from Utils import *
from node import Node
from employee import Employee
from main import getTravelData
#print(calculate_future_delta(datetime.now(), "0 hours 43 mins", "23:59"))





"""
time_string = '2 hours 12 min'
result = convert_to_minutes(time_string)
requester = cat_data.iloc[0]
print(reverse_data(requester))
print((requester['יישוב הפנייה'] + ' ' + requester['רחוב הפנייה'] + ' ' + requester['מס בית הפנייה'])[::-1])

employee = Employee(emp_data.iloc[0])
print(employee)







def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            dict1[key] = merge_dicts(dict1[key], value)
        else:
            # Overwrite or add key-value pair
            dict1[key] = value
    return dict1
     
# Driver code
dict1 = {'a': {'b' : 1}}
dict2 = {'a': {'c' : 2},
         'd': {'e' : 3}
         }

dict1 = merge_dicts(dict1, dict2)
print(dict1)
"""


times = getTravelData(['נוף הגליל', 'תל אביב'], ['אילת', 'באר שבע'])
write_to_file(times, 'RESPONSE.json')
