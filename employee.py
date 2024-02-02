import requests
from Utils import geocode

class Employee():
    def __init__(self, emp_data, address_dict) -> None:
        self.name = emp_data['שם העובד']
        self.stops = []

        
        self.hebrew_location = emp_data['כתובת תחילה']
        self.start_location = geocode(self.hebrew_location, address_dict)
        self.location = self.start_location
        


    def __str__(self) -> str:
        return self.name


    def add_stop(self, location : str):
        self.stops.append(location)
