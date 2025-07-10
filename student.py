from dataclasses import dataclass
from enums import Availability
from typing import Dict

@dataclass
class Student:
    id: str
    full_name: str
    #  data: pd.Series  | maybe?
    classes: Dict[str, str]  # Dictionary to store class preferences NOTE: should this be Dict[ClassPeriod, Availability]?
    building: str
    flexibility: int  # Number of flexible class preferences

    def __post_init__(self):
        self.flexibility = self._calculate_flexibility()
    
    def _calculate_flexibility(self) -> int:
        """Calculate flexibility score based on availability preferences"""
        score = 0
        for availability in self.classes.values():
            if availability == Availability.FIRST_CHOICE.value:
                score += 2
            elif availability == Availability.FITS.value:
                score += 1
            elif availability == Availability.DOES_NOT_FIT.value:
                score -= 1
        return score
    
    def get_availability(self, class_time: str) -> Availability:
        """Get availability enum for a class time"""
        availability_str = self.classes.get(class_time, Availability.DOES_NOT_FIT.value)
        return Availability(availability_str)
        
        '''       # Deprecated cleaning logic, move to import logic in schedule_engine.py

        # Process data to extract and clean data #
        for column, value in data.items():
            # Class data (extract and clean)
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', column):
                self.classes[column] = value if pd.notna(value) else ""
                self.flexibility += 1 if re.match(r'^(First Choice|Fits)$', value) else 0
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

        '''