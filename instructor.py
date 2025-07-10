from dataclasses import dataclass, field
from typing import Dict
from enums import Availability, TeachingPreference
from settings import Settings, Setting

class Instructor:
    id: str
    full_name: str
    full_name = "N/A"
    # data = data  TODO: Remove this line, not used in the class
    classes: Dict[str, str]  # class time -> availability  NOTE: should this be Dict[ClassPeriod, Availability]?
    teach_with_preference: str
    assigned_classes: int = field(default=0, init=False)
        

    ''' TODO: Deprecated cleaning logic, move to import logic in schedule_engine.py 


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
    '''
    
    def get_availability(self, class_time: str) -> Availability:
        """Get availability enum for a class time"""
        availability_str = self.classes.get(class_time, Availability.NOT_AVAILABLE.value)
        return Availability(availability_str)
    
    def can_teach_more(self) -> bool:
        """Check if instructor can be assigned to more classes"""
        return self.assigned_classes < Settings.get_setting(Setting.MAX_CLASSES_PER_INSTRUCTOR)
    
    def prefers_co_teaching(self) -> bool:
        """Check if instructor prefers to teach with others"""
        return self.teach_with_preference == TeachingPreference.YES.value
