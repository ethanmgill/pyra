from enum import Enum

class Availability(Enum):
    FIRST_CHOICE = "First Choice"
    AVAILABLE = "Fits"
    NOT_AVAILABLE = "Does Not Fit"

class TeachingPreference(Enum):
    YES = "Yes"
    NO = "No"
    NO_PREFERENCE = "No Preference"