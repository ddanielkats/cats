#מייצג פנייה
class Node():
    #requester represents a row in the dataframe
    def __init__(self, requester) -> None:
        self.created_on = requester['נוצר ב:']
        self.feed_time = requester['שעות האכלה']
        self.location = requester['יישוב הפנייה'] + ' ' + str(requester['רחוב הפנייה']) + ' ' + str(requester['מס בית הפנייה'])
        self.cat_number = requester['מספר חתולים']
        self.req_num = requester['מספר פנייה']

        self.weight = 0
        self.emp_dict = {}
        self.emp_order = []

    def add_emp(self, emp, weight):
        #append and sort by weights
        self.emp_order[str(emp)] = weight
        #sort all employees in descending order
        #TODO sort the dict better
        self.emp_order = sorted(self.emp_order.items(), key=lambda x: x[1])


