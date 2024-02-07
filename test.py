import asyncio, time, aiohttp, warnings
from pprint import pprint
from Utils import reverse_data
from node import Node
from employee import Employee
from main import getTravelData
import pandas as pd

for i in range(658400):
    print(i)
    if i % 100000 ==0:
        time.sleep(1)
    