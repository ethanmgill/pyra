import re

class ClassPeriod:
    @staticmethod
    def calculate_name(name):
        
        day = name.split()[0] if " " in name else ""
        # Extract time from format "Day HH:MMam/pm-HH:MMam/pm"
        time_pattern = r'((\d+)(:?\d+)?([ampmAMPM]{2}))-((\d+)(:?\d+)?([ampmAMPM]{2}))'
        m = re.search(time_pattern, name)

        start_time = f"{m.group(2)}{m.group(3) or ":00"}{m.group(4).lower()}"
        end_time   = f"{m.group(6)}{m.group(7) or ":00"}{m.group(8).lower()}"

        name = f"{day} {start_time}-{end_time}"
        return (name, day, start_time, end_time)

    def __init__(self, name, students=[], instructors=[]):

        # instance variables
        self.name = name
        self.students = students
        self.instructors = instructors

        self.name, self.day, self.start_time, self.end_time = self.calculate_name(name)
    

            