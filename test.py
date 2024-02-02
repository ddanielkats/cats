import requests
from pprint import pprint
from Utils import *
from node import Node
from employee import Employee
from main import getTravelData




# Define a global list
global_list = []

def append_to_global(value):
    # Access the global list
    # Append to the global list
    global_list.append(value)


# Example usage
append_to_global('item1')
append_to_global('item2')

# Print or use the global list outside the function
print(global_list)