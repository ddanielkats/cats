#מייצג פנייה
import pandas as pd

class Node():
    #requester represents a row in the dataframe
    def __init__(self, requester, address, coded_address) -> None:
        self.created_on = requester['נוצר ב:']
        self.feed_time = requester['שעות האכלה']
        self.cat_number = requester['מספר חתולים']
        self.req_num = requester['מספר פנייה']
        #join the street, city, home_number into a string
        self.weight = 0
        self.emp_dict = {}
        self.emp_order = []
        #add address to dictionary
        address[coded_address] = coded_address
        self.location = coded_address

"""
    def add_emp(self, emp, weight):
        #append and sort by weights
        self.emp_order[str(emp)] = weight
        #sort all employees in descending order
        #TODO sort the dict better
        self.emp_order = sorted(self.emp_order.items(), key=lambda x: x[1])
"""