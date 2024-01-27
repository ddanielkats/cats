class Employee():
    def __init__(self, emp_data) -> None:
        self.name = emp_data['שם העובד']
        self.start_location = emp_data['כתובת תחילה']
        self.location = self.start_location
        self.stops = []
        
    def __str__(self) -> str:
        return self.name


    def add_stop(self, location : str):
        self.stops.append(location)
