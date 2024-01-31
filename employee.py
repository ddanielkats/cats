import requests


class Employee():
    def __init__(self, emp_data, address, coded_address) -> None:
        self.name = emp_data['שם העובד']
        self.stops = []

        
        #add address to dictionary
        address[coded_address] = emp_data['כתובת תחילה']
        self.start_location = coded_address
        self.location = self.start_location
        


    def __str__(self) -> str:
        return self.name


    def add_stop(self, location : str):
        self.stops.append(location)
