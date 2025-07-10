from class_time import ClassPeriod
import pandas as pd
import re

class Instructor:
    def __init__(self, instructor_id, data):
        self.id = instructor_id
        self.full_name = "N/A"
        self.data = data
        self.classes = {}  # Dictionary to store class availability
        self.teach_with_preference = "No Preference"
        
        # Process data to extract class availability and preferences
        for column, value in data.items():
            # Class availability (extract and clean)
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', column):
                fname = ClassPeriod.calculate_name(column)[0]
                self.classes[fname] = value if pd.notna(value) else ""
            # Full name (extract and clean)
            elif re.match(r'^(First Name|Last Name|Name)$', column):
                if column == "Name":
                    self.full_name = value if pd.notna(value) else "N/A"
                else:
                    # If First Name or Last Name, combine them
                    first_name = data.get('First Name', '')
                    last_name = data.get('Last Name', '')
                    self.full_name = f"{first_name} {last_name}".strip() or "N/A"
            # Teaching preference (extract and clean)
            elif column == "Would you like to teach with someone else?":
                self.teach_with_preference = value if pd.notna(value) else "No Preference"
