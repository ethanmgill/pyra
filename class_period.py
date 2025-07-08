import re
from enums import Availability
from dataclasses import dataclass, field
from typing import List, Optional
from student import Student
from instructor import Instructor
from settings import Settings, Setting

# Configuration constants
MIN_STUDENTS = lambda: Settings().get_setting(Setting.MIN_STUDENTS_PER_CLASS)
MAX_CLASSES_PER_INSTRUCTOR = lambda: Settings().get_setting(Setting.MAX_CLASSES_PER_INSTRUCTOR)
MAX_INSTRUCTORS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_INSTRUCTORS_PER_CLASS)
MAX_STUDENTS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_STUDENTS_PER_CLASS)
MAX_SECTIONS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_SECTIONS_PER_CLASS)

class ClassPeriod:

    def __init__(self, name, students=[], instructors=[]):

        # instance variables
        self.name = name
        self.students = students
        self.instructors = instructors

        self.name, self.day, self.start_time, self.end_time = self.calculate_name(name)

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

@dataclass
class ClassSection:
    """Individual section of a class period"""
    name: str
    students: List[Student] = field(default_factory=list)
    instructors: List[Instructor] = field(default_factory=list)
    
    def add_student(self, student: Student) -> bool:
        """Add student if there's space"""
        if len(self.students) < MAX_STUDENTS_PER_CLASS:
            self.students.append(student)
            return True
        return False
    
    def add_instructor(self, instructor: Instructor) -> bool:
        """Add instructor if there's space and they can teach more"""
        if (len(self.instructors) < MAX_INSTRUCTORS_PER_CLASS and 
            instructor.can_teach_more()):
            self.instructors.append(instructor)
            instructor.assigned_classes += 1
            return True
        return False
    
    def get_student_count(self) -> int:
        return len(self.students)
    
    def get_instructor_count(self) -> int:
        return len(self.instructors)
    
    def is_viable(self) -> bool:
        """Check if class section meets minimum requirements"""
        return (len(self.students) >= MIN_STUDENTS and 
                len(self.instructors) >= 1 and
                len(self.instructors) <= MAX_INSTRUCTORS_PER_CLASS)

@dataclass
class ClassPeriod:
    """Container for all sections of a specific class time"""
    name: str
    sections: List[ClassSection] = field(default_factory=list)
    
    def add_section(self, section: ClassSection) -> bool:
        """Add a section if we haven't reached the maximum"""
        if len(self.sections) < MAX_SECTIONS_PER_CLASS:
            self.sections.append(section)
            return True
        return False
    
    def create_new_section(self) -> Optional[ClassSection]:
        """Create and add a new section if possible"""
        if len(self.sections) < MAX_SECTIONS_PER_CLASS:
            section = ClassSection(self.name)
            self.sections.append(section)
            return section
        return None
    
    def get_section(self, section_index: int) -> Optional[ClassSection]:
        """Get a specific section by index"""
        if 0 <= section_index < len(self.sections):
            return self.sections[section_index]
        return None
    
    def get_total_students(self) -> int:
        """Get total number of students across all sections"""
        return sum(section.get_student_count() for section in self.sections)
    
    def get_viable_sections(self) -> List[ClassSection]:
        """Get all sections that meet minimum requirements"""
        return [section for section in self.sections if section.is_viable()]
    
    def remove_non_viable_sections(self) -> List[Student]:
        """Remove sections that don't meet requirements and return displaced students"""
        displaced_students = []
        viable_sections = []
        
        for section in self.sections:
            if section.is_viable():
                viable_sections.append(section)
            else:
                displaced_students.extend(section.students)
        
        self.sections = viable_sections
        return displaced_students
    

            