import requests


class Employee():
    def __init__(self, emp_data, address, code_func) -> None:
        self.name = emp_data['שם העובד']
        self.stops = []

        
        coded_address = code_func(emp_data['כתובת תחילה'])
        #add address to dictionary
        address[coded_address] = emp_data['כתובת תחילה']
        self.start_location = coded_address
        self.location = self.start_location
        


    def __str__(self) -> str:
        return self.name


    def add_stop(self, location : str):
        self.stops.append(location)
