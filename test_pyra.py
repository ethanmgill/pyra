import os
import pytest
import pandas as pd
from class_scheduler_app import ClassSchedulerApp
from PyQt5.QtWidgets import QApplication

# Helper to create a QApplication only once for all tests
@pytest.fixture(scope="session", autouse=True)
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def scheduler():
    # Create a new instance for each test
    sched = ClassSchedulerApp()
    return sched

def test_import_and_schedule_with_existing_files(scheduler):
    # Use existing Excel files with test data
    students_file = os.path.abspath("PSYC 100 Fall 2024 Options (NN Students).xlsx")
    instructors_file = os.path.abspath("PSYC 100 Fall 2024 Options (NN Instructors).xlsx")

    assert os.path.exists(students_file), f"Missing test file: {students_file}"
    assert os.path.exists(instructors_file), f"Missing test file: {instructors_file}"

    # Import students and instructors
    scheduler.process_student_data(pd.read_excel(students_file))
    scheduler.process_instructor_data(pd.read_excel(instructors_file))

    # Generate schedule
    scheduler.generate_schedule()

    # Collect assignments from the schedule
    assigned_students = set()
    misassigned_students = []
    for class_data in scheduler.detailed_schedule:
        for student in class_data['Students']:
            assigned_students.add(student['ID'])
            # Check that the class is in the student's preferences and is "First Choice" or "Fits"
            student_obj = scheduler.students[student['ID']]
            # The class name may have section info, so check startswith
            found = False
            for class_pref, pref_value in student_obj.classes.items():
                if class_data['Class Time'].startswith(class_pref) and pref_value in ("First Choice", "Fits"):
                    found = True
                    break
            if not found:
                misassigned_students.append((student,class_data['Class Time']))
    # Check if any students were misassigned
    assert not misassigned_students, f"Misassigned students ({len(misassigned_students)}):\n - {'\n - '.join([f'{s['Name']} (ID: {s['ID']}) (Class Time: {t})' for (s,t) in misassigned_students])}"

    # Ensure all students are assigned
    assert set(scheduler.students.keys()) == assigned_students, "Not all students were assigned to a class"