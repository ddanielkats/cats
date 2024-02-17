#מייצג פנייה
import pandas as pd
from Utils import geocode
import math

class Node():
    #requester represents a row in the dataframe
    def __init__(self, node_row, coded_location) -> None:
        self.node_row = node_row
        self.created_on = node_row['נוצר ב:']
        self.feed_time = node_row['שעות האכלה']
        #if the target hour is empty in excel, return 0
        try:
            if math.isnan(self.feed_time):
                self.feed_time = 0
        except: #feed time is string
            self.feed_time = self.feed_time.replace(".", ":")
        self.feed_time
        self.cat_number = node_row['מספר חתולים']
        self.req_num = node_row['מספר פנייה']
        #join the street, city, home_number into a string
        self.weight = 0
        self.emp_dict = {}
        self.emp_order = []
        #add address to dictionary
        self.hebrew_location = ' '.join(str(node_row[column]) for column in ['יישוב הפנייה', 'רחוב הפנייה', 'מס בית הפנייה'] if not pd.isna(node_row[column]))
        self.location = coded_location

    def __str__(self) -> str:
        return self.hebrew_location
"""
    def add_emp(self, emp, weight):
        #append and sort by weights
        self.emp_order[str(emp)] = weight
        #sort all employees in descending order
        #TODO sort the dict better
        self.emp_order = sorted(self.emp_order.items(), key=lambda x: x[1])
"""