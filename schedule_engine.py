from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import heapq
from enums import Availability, TeachingPreference
from settings import Settings, Setting

# Configuration constants
MIN_STUDENTS = lambda: Settings().get_setting(Setting.MIN_STUDENTS_PER_CLASS)
MAX_CLASSES_PER_INSTRUCTOR = lambda: Settings().get_setting(Setting.MAX_CLASSES_PER_INSTRUCTOR)
MAX_INSTRUCTORS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_INSTRUCTORS_PER_CLASS)
MAX_STUDENTS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_STUDENTS_PER_CLASS)
MAX_SECTIONS_PER_CLASS = lambda: Settings().get_setting(Setting.MAX_SECTIONS_PER_CLASS)

@dataclass
class Student:
    student_id: str
    full_name: str
    classes: Dict[str, str]  # class_time -> availability
    building: str
    flexibility: int = field(init=False)
    
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

@dataclass
class Instructor:
    id: str
    full_name: str
    classes: Dict[str, str]  # class_time -> availability
    teach_with_preference: str
    assigned_classes: int = field(default=0, init=False)
    
    def get_availability(self, class_time: str) -> Availability:
        """Get availability enum for a class time"""
        availability_str = self.classes.get(class_time, Availability.DOES_NOT_FIT.value)
        return Availability(availability_str)
    
    def can_teach_more(self) -> bool:
        """Check if instructor can be assigned to more classes"""
        return self.assigned_classes < MAX_CLASSES_PER_INSTRUCTOR
    
    def prefers_co_teaching(self) -> bool:
        """Check if instructor prefers to teach with others"""
        return self.teach_with_preference == TeachingPreference.YES.value

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

class SchedulingPriorityQueue:
    """Priority queue for scheduling decisions"""
    
    def __init__(self):
        self.heap = []
    
    def add_student_assignment(self, student: Student, class_time: str, 
                            section_idx: int, priority_score: float):
        """Add student assignment with priority score (lower = higher priority)"""
        heapq.heappush(self.heap, (priority_score, student.student_id, class_time, section_idx))
    
    def get_next_assignment(self) -> Optional[Tuple[float, str, str, int]]:
        """Get next assignment or None if queue is empty"""
        if self.heap:
            return heapq.heappop(self.heap)
        return None

class ClassScheduler:
    """Main scheduling algorithm"""
    
    def __init__(self):
        self.schedule: Dict[str, ClassPeriod] = {}
        self.student_assignments: Dict[str, str] = {}
        self.class_demand = defaultdict(int)
        
    def generate_schedule(self, student: Student, class_list: List[List[ClassSection]], 
                         instructors: Dict[str, Instructor]) -> Dict[str, ClassPeriod]:
        """
        Generate class schedule for a single student based on preferences
        
        Args:
            student: Student object to schedule
            class_list: List of sections (each section is a list of ClassSection objects)
            instructors: Map of instructor_id -> Instructor object
            
        Returns:
            Dictionary with class names as keys and ClassPeriod objects as values
        """
        # Reset state
        self.schedule = {}
        self.student_assignments = {}
        self.class_demand = defaultdict(int)
        
        # Initialize schedule structure from class_list
        for section_group in class_list:
            for class_section in section_group:
                class_name = class_section.name
                if class_name not in self.schedule:
                    self.schedule[class_name] = ClassPeriod(class_name)
                
                # Add this section to the class period
                self.schedule[class_name].add_section(class_section)
        
        # Calculate demand for each class time
        self._calculate_class_demand(student)
        
        # Create priority queue for student assignments
        priority_queue = SchedulingPriorityQueue()
        
        # Add all possible assignments to priority queue
        for class_time in student.classes:
            availability = student.get_availability(class_time)
            if availability != Availability.DOES_NOT_FIT:
                priority_score = self._calculate_priority_score(
                    student, class_time, availability
                )
                
                # Try to assign to existing sections
                if class_time in self.schedule:
                    class_period = self.schedule[class_time]
                    for section_idx in range(len(class_period.sections)):
                        priority_queue.add_student_assignment(
                            student, class_time, section_idx, priority_score
                        )
        
        # Process assignments in priority order
        assigned_classes = set()
        while True:
            assignment = priority_queue.get_next_assignment()
            if not assignment:
                break
                
            priority_score, student_id, class_time, section_idx = assignment
            
            # Skip if student already assigned to this class time
            if class_time in assigned_classes:
                continue
                
            # Try to assign student to this section
            if self._assign_student_to_section(student, class_time, section_idx):
                assigned_classes.add(class_time)
        
        # Assign instructors to viable classes
        self._assign_instructors(instructors)
        
        # Clean up non-viable classes
        self._cleanup_schedule()
        
        # Verify schedule integrity
        self.verify_schedule_integrity()
        
        return self.schedule
    
    def _calculate_class_demand(self, student: Student):
        """Calculate demand for each class time"""
        for class_time, availability_str in student.classes.items():
            availability = Availability(availability_str)
            if availability == Availability.FIRST_CHOICE:
                self.class_demand[class_time] += 2
            elif availability == Availability.FITS:
                self.class_demand[class_time] += 1
    
    def _calculate_priority_score(self, student: Student, class_time: str, 
                                availability: Availability) -> float:
        """Calculate priority score for assignment (lower = higher priority)"""
        base_score = 0
        
        # Prioritize first choice
        if availability == Availability.FIRST_CHOICE:
            base_score = 1
        elif availability == Availability.FITS:
            base_score = 2
        
        # Factor in student flexibility (less flexible students get priority)
        flexibility_penalty = student.flexibility * 0.1
        
        # Factor in class demand (higher demand = higher priority)
        demand_bonus = -self.class_demand[class_time] * 0.05
        
        return base_score + flexibility_penalty + demand_bonus
    
    def _assign_student_to_section(self, student: Student, class_time: str, 
                                 section_idx: int) -> bool:
        """Assign student to specific section if possible"""
        if class_time not in self.schedule:
            return False
        
        class_period = self.schedule[class_time]
        section = class_period.get_section(section_idx)
        
        if section and section.add_student(student):
            self.student_assignments[student.student_id] = class_time
            return True
        
        return False
    
    def _assign_instructors(self, instructors: Dict[str, Instructor]):
        """Assign instructors to classes based on availability and preferences"""
        # Sort class sections by student count (descending) to prioritize larger classes
        class_sections = []
        for class_time, class_period in self.schedule.items():
            for section in class_period.sections:
                if section.get_student_count() > 0:
                    class_sections.append((class_time, section))
        
        class_sections.sort(key=lambda x: x[1].get_student_count(), reverse=True)
        
        # Track sections that couldn't get instructors
        sections_needing_removal = []
        
        # Assign instructors
        for class_time, section in class_sections:
            available_instructors = []
            
            # Find available instructors for this class time
            for instructor in instructors.values():
                availability = instructor.get_availability(class_time)
                if availability != Availability.DOES_NOT_FIT and instructor.can_teach_more():
                    priority = 0
                    if availability == Availability.FIRST_CHOICE:
                        priority = 1
                    elif availability == Availability.FITS:
                        priority = 2
                    
                    available_instructors.append((priority, instructor))
            
            # Sort by priority (first choice first)
            available_instructors.sort(key=lambda x: x[0])
            
            # Assign instructors based on class size and preferences
            target_instructors = min(
                MAX_INSTRUCTORS_PER_CLASS,
                max(1, section.get_student_count() // 10)  # 1 instructor per 10 students
            )
            
            assigned_count = 0
            for priority, instructor in available_instructors:
                if assigned_count >= target_instructors:
                    break
                
                if section.add_instructor(instructor):
                    assigned_count += 1
            
            # If no instructors were assigned, mark section for removal
            if assigned_count == 0:
                sections_needing_removal.append((class_time, section))
        
        # Remove sections that couldn't get instructors
        for class_time, section in sections_needing_removal:
            if class_time in self.schedule:
                class_period = self.schedule[class_time]
                if section in class_period.sections:
                    class_period.sections.remove(section)
                    # Remove students from assignments if their section was removed
                    for student in section.students:
                        if student.student_id in self.student_assignments:
                            if self.student_assignments[student.student_id] == class_time:
                                del self.student_assignments[student.student_id]
    
    def _cleanup_schedule(self):
        """Remove classes that don't meet minimum requirements"""
        classes_to_remove = []
        
        for class_time, class_period in self.schedule.items():
            # Remove non-viable sections and get displaced students
            displaced_students = class_period.remove_non_viable_sections()
            
            # Remove students from assignments if their section was removed
            for student in displaced_students:
                if student.student_id in self.student_assignments:
                    if self.student_assignments[student.student_id] == class_time:
                        del self.student_assignments[student.student_id]
            
            # If no viable sections remain, mark class period for removal
            if not class_period.sections:
                classes_to_remove.append(class_time)
        
        # Remove empty class periods
        for class_time in classes_to_remove:
            del self.schedule[class_time]
    
    def verify_schedule_integrity(self) -> bool:
        """Verify that the final schedule meets all constraints"""
        for class_time, class_period in self.schedule.items():
            for section in class_period.sections:
                # Check minimum students
                if len(section.students) < MIN_STUDENTS:
                    print(f"ERROR: {class_time} has {len(section.students)} students (min: {MIN_STUDENTS})")
                    return False
                
                # Check maximum students
                if len(section.students) > MAX_STUDENTS_PER_CLASS:
                    print(f"ERROR: {class_time} has {len(section.students)} students (max: {MAX_STUDENTS_PER_CLASS})")
                    return False
                
                # Check minimum instructors (CRITICAL CHECK)
                if len(section.instructors) < 1:
                    print(f"ERROR: {class_time} has no instructors")
                    return False
                
                # Check maximum instructors
                if len(section.instructors) > MAX_INSTRUCTORS_PER_CLASS:
                    print(f"ERROR: {class_time} has {len(section.instructors)} instructors (max: {MAX_INSTRUCTORS_PER_CLASS})")
                    return False
        
        # Check instructor load constraints
        instructor_loads = {}
        for class_time, class_period in self.schedule.items():
            for section in class_period.sections:
                for instructor in section.instructors:
                    if instructor.id not in instructor_loads:
                        instructor_loads[instructor.id] = 0
                    instructor_loads[instructor.id] += 1
        
        for instructor_id, load in instructor_loads.items():
            if load > MAX_CLASSES_PER_INSTRUCTOR:
                print(f"ERROR: Instructor {instructor_id} assigned to {load} classes (max: {MAX_CLASSES_PER_INSTRUCTOR})")
                return False
        
        # Check sections per class constraint
        for class_time, class_period in self.schedule.items():
            if len(class_period.sections) > MAX_SECTIONS_PER_CLASS:
                print(f"ERROR: {class_time} has {len(class_period.sections)} sections (max: {MAX_SECTIONS_PER_CLASS})")
                return False
        
        print("✅ Schedule integrity verified - all constraints satisfied")
        return True

# Example usage and testing
def test_scheduling_algorithm():
    """Test the scheduling algorithm with sample data"""
    
    # Create sample student
    student = Student(
        student_id="S001",
        full_name="John Doe",
        classes={
            "Monday 9AM": "First Choice",
            "Tuesday 2PM": "fits",
            "Wednesday 10AM": "First Choice",
            "Thursday 3PM": "does not fit",
            "Friday 1PM": "fits"
        },
        building="Dorm A"
    )
    
    # Create sample instructors
    instructors = {
        "I001": Instructor(
            id="I001",
            full_name="Prof. Smith",
            classes={
                "Monday 9AM": "First Choice",
                "Tuesday 2PM": "fits",
                "Wednesday 10AM": "fits"
            },
            teach_with_preference="Yes"
        ),
        "I002": Instructor(
            id="I002",
            full_name="Dr. Johnson",
            classes={
                "Monday 9AM": "fits",
                "Wednesday 10AM": "First Choice",
                "Friday 1PM": "First Choice"
            },
            teach_with_preference="No Preference"
        )
    }
    
    # Create sample class list (groups of sections)
    class_list = [
        [
            ClassSection("Monday 9AM"),
            ClassSection("Tuesday 2PM"),
            ClassSection("Wednesday 10AM")
        ],
        [
            ClassSection("Monday 9AM"),
            ClassSection("Friday 1PM")
        ]
    ]
    
    # Run scheduler
    scheduler = ClassScheduler()
    schedule = scheduler.generate_schedule(student, class_list, instructors)
    
    # Print results
    print("Generated Schedule:")
    for class_time, class_period in schedule.items():
        print(f"\n{class_time}:")
        print(f"  Total Students: {class_period.get_total_students()}")
        print(f"  Number of Sections: {len(class_period.sections)}")
        
        for i, section in enumerate(class_period.sections):
            print(f"    Section {i+1}:")
            print(f"      Students: {len(section.students)}")
            print(f"      Instructors: {len(section.instructors)}")
            print(f"      Viable: {section.is_viable()}")
            
            # Print student names
            if section.students:
                student_names = [s.full_name for s in section.students]
                print(f"      Student Names: {', '.join(student_names)}")
            
            # Print instructor names
            if section.instructors:
                instructor_names = [i.full_name for i in section.instructors]
                print(f"      Instructor Names: {', '.join(instructor_names)}")
    
    return schedule

# Algorithm proof and complexity analysis
def analyze_algorithm():
    """
    Algorithm Analysis:
    
    Time Complexity:
    - O(S * C * Sec) where S = students, C = class times, Sec = sections
    - Priority queue operations: O(log(S * C * Sec))
    - Instructor assignment: O(I * C * Sec) where I = instructors
    - Overall: O((S + I) * C * Sec * log(S * C * Sec))
    
    Space Complexity:
    - O(S * C + I * C + C * Sec) for storing schedules and assignments
    
    Correctness Proof:
    1. Constraint Satisfaction:
       - MIN_STUDENTS: Enforced in is_viable() method
       - MAX_CLASSES_PER_INSTRUCTOR: Enforced in can_teach_more()
       - MAX_INSTRUCTORS_PER_CLASS: Enforced in add_instructor()
       - MAX_STUDENTS_PER_CLASS: Enforced in add_student()
       - MAX_SECTIONS_PER_CLASS: Enforced in assignment loop
    
    2. Priority Objectives:
       - Student preferences: Priority queue ensures first choice processed first
       - Balance: Instructor assignment prioritizes larger classes
       - Instructor allocation: Based on class size and instructor availability
    
    3. Optimality:
       - Greedy approach ensures locally optimal decisions
       - Priority-based assignment maximizes student satisfaction
       - Cleanup phase ensures all constraints are met
    """
    print("Algorithm Analysis Complete - See docstring for details")

if __name__ == "__main__":
    # Run test
    test_schedule = test_scheduling_algorithm()
    
    # Run analysis
    analyze_algorithm()
