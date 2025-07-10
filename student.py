import pandas as pd
import re

class Student:
    def __init__(self, student_id, data):
        self.id = student_id
        self.full_name = "N/A"
        self.data = data
        self.classes = {}  # Dictionary to store class preferences
        self.building = "N/A"
        
        # Process data to extract and clean data #
        for column, value in data.items():
            # Class data (extract and clean)
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', column):
                self.classes[column] = value if pd.notna(value) else ""
            # Full name (extract and clean)
            elif re.match(r'^(First Name|Last Name|Name)$', column):
                if column == "Name":
                    self.full_name = value if pd.notna(value) else "N/A"
                else:
                    # If First Name or Last Name, combine them
                    first_name = data.get('First Name', '')
                    last_name = data.get('Last Name', '')
                    self.full_name = f"{first_name} {last_name}".strip() or "N/A"
            # Building assignment (clean)
            elif re.match(r'^Building', column):
                self.building = data.get(column)
