from collections import defaultdict
import sys
import os
import openpyxl
import pandas as pd
from datetime import datetime
import re
from student import Student
from instructor import Instructor
from class_period import ClassPeriod
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QTabWidget, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QComboBox, QSpinBox,
                            QFormLayout, QLineEdit, QGroupBox, QTextEdit,
                            QProgressBar, QSplitter, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor


class ClassSchedulerApp(QMainWindow):

    #                                                   #
    #  Main application class for the Class Scheduler.  #
    #                                                   #

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Class Scheduler")
        self.setMinimumSize(1200, 800)
        
        # Application data
        self.students = {}
        self.instructors = {}
        self.classes = {}
        
        # Settings with defaults
        self.settings = {
            "max_students_per_class": 20,
            "max_instructors_per_class": 2,
            "min_students_per_class": 6,
            "max_classes_per_instructor": 2,
            "prioritize_first_choice": True
        }
        
        # Setup UI
        self.setup_ui()
        
    #  Setup the main UI components and layout for the application.  #

    def setup_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_students_tab()
        self.create_instructors_tab()
        self.create_classes_tab()
        self.create_schedule_tab()
        self.create_settings_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_dashboard_tab(self):
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Welcome message
        welcome_label = QLabel("Class Scheduler Dashboard")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(welcome_label)
        
        # Statistics section
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_layout = QHBoxLayout(stats_frame)
        
        # Statistics boxes
        stats_boxes = [
            {"title": "Students", "value": "0", "id": "students_count"},
            {"title": "Instructors", "value": "0", "id": "instructors_count"},
            {"title": "Classes", "value": "0", "id": "classes_count"},
            {"title": "Schedule Builder", "value": "0", "id": "scheduled_count"}
        ]
        
        for box in stats_boxes:
            group_box = QGroupBox(box["title"])
            box_layout = QVBoxLayout(group_box)
            
            value_label = QLabel(box["value"])
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setFont(QFont("Arial", 24))
            value_label.setObjectName(box["id"])
            
            box_layout.addWidget(value_label)
            stats_layout.addWidget(group_box)
        
        layout.addWidget(stats_frame)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Import buttons
        import_students_btn = QPushButton("Import Students")
        import_students_btn.clicked.connect(self.import_students)
        
        import_instructors_btn = QPushButton("Import Instructors")
        import_instructors_btn.clicked.connect(self.import_instructors)
        
        generate_schedule_btn = QPushButton("Generate Schedule")
        generate_schedule_btn.clicked.connect(self.generate_schedule)
        
        export_schedule_btn = QPushButton("Export Schedule")
        export_schedule_btn.clicked.connect(self.export_schedule)
        
        actions_layout.addWidget(import_students_btn)
        actions_layout.addWidget(import_instructors_btn)
        actions_layout.addWidget(generate_schedule_btn)
        actions_layout.addWidget(export_schedule_btn)
        
        layout.addWidget(actions_group)
        
        # Recent activity log
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Add tab
        self.tabs.addTab(dashboard_widget, "Dashboard")
    
    def create_students_tab(self):
        students_widget = QWidget()
        layout = QVBoxLayout(students_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Students")
        import_btn.clicked.connect(self.import_students)
        
        clear_btn = QPushButton("Clear Students")
        clear_btn.clicked.connect(self.clear_students)
        
        controls_layout.addWidget(import_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addStretch()
        
        # Table for students
        self.students_table = QTableWidget(0, 4)  # Start with 4 columns
        self.students_table.setHorizontalHeaderLabels(["Student ID","Full Name", "Building", "Classes"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.students_table)
        
        # Add tab
        self.tabs.addTab(students_widget, "Students")
    
    def create_instructors_tab(self):
        instructors_widget = QWidget()
        layout = QVBoxLayout(instructors_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Instructors")
        import_btn.clicked.connect(self.import_instructors)
        
        clear_btn = QPushButton("Clear Instructors")
        clear_btn.clicked.connect(self.clear_instructors)
        
        controls_layout.addWidget(import_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addStretch()
        
        # Table for instructors
        self.instructors_table = QTableWidget(0, 4)  # Start with 3 columns
        self.instructors_table.setHorizontalHeaderLabels(
            ["Instructor ID", "Full Name", "Teach with Others", "Available Classes"])
        self.instructors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.instructors_table)
        
        # Add tab
        self.tabs.addTab(instructors_widget, "Instructors")
    
    def create_classes_tab(self):
        classes_widget = QWidget()
        layout = QVBoxLayout(classes_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_class_btn = QPushButton("Add Class")
        add_class_btn.clicked.connect(self.add_class_dialog)
        
        clear_classes_btn = QPushButton("Clear Classes")
        clear_classes_btn.clicked.connect(self.clear_classes)
        
        controls_layout.addWidget(add_class_btn)
        controls_layout.addWidget(clear_classes_btn)
        controls_layout.addStretch()
        
        # Table for classes
        self.classes_table = QTableWidget(0, 4)
        self.classes_table.setHorizontalHeaderLabels(
            ["Class Name", "Students", "Instructors", "Status"])
        self.classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.classes_table)
        
        # Add tab
        self.tabs.addTab(classes_widget, "Classes")
    
    def create_schedule_tab(self):
        schedule_widget = QWidget()
        layout = QVBoxLayout(schedule_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Schedule")
        generate_btn.clicked.connect(self.generate_schedule)
        
        export_btn = QPushButton("Export Schedule")
        export_btn.clicked.connect(self.export_schedule)
        
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        
        # Schedule view
        self.schedule_table = QTableWidget(0, 4)  # Start with 3 columns
        self.schedule_table.setHorizontalHeaderLabels(
            ["Class Time", "Instructors", "Students", "Student Count"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.schedule_table)
        
        # Add tab
        self.tabs.addTab(schedule_widget, "Schedule")
    
    def create_settings_tab(self):
        settings_widget = QWidget()
        layout = QFormLayout(settings_widget)
        
        # Settings fields
        self.max_students_spinbox = QSpinBox()
        self.max_students_spinbox.setRange(1, 100)
        self.max_students_spinbox.setValue(self.settings["max_students_per_class"])
        self.max_students_spinbox.valueChanged.connect(
            lambda val: self.update_setting("max_students_per_class", val))
        
        self.max_instructors_spinbox = QSpinBox()
        self.max_instructors_spinbox.setRange(1, 10)
        self.max_instructors_spinbox.setValue(self.settings["max_instructors_per_class"])
        self.max_instructors_spinbox.valueChanged.connect(
            lambda val: self.update_setting("max_instructors_per_class", val))
        
        self.min_students_spinbox = QSpinBox()
        self.min_students_spinbox.setRange(1, 50)
        self.min_students_spinbox.setValue(self.settings["min_students_per_class"])
        self.min_students_spinbox.valueChanged.connect(
            lambda val: self.update_setting("min_students_per_class", val))
        
        self.max_classes_per_instructor_spinbox = QSpinBox()
        self.max_classes_per_instructor_spinbox.setRange(1, 10)
        self.max_classes_per_instructor_spinbox.setValue(self.settings["max_classes_per_instructor"])
        self.max_classes_per_instructor_spinbox.valueChanged.connect(
            lambda val: self.update_setting("max_classes_per_instructor", val))

        self.prioritize_combo = QComboBox()
        self.prioritize_combo.addItems(["Yes", "No"])
        self.prioritize_combo.setCurrentText("Yes" if self.settings["prioritize_first_choice"] else "No")
        self.prioritize_combo.currentTextChanged.connect(
            lambda text: self.update_setting("prioritize_first_choice", text == "Yes"))
        
        # Add fields to layout
        layout.addRow("Maximum Students per Class:", self.max_students_spinbox)
        layout.addRow("Maximum Instructors per Class:", self.max_instructors_spinbox)
        layout.addRow("Minimum Students for Class to Run:", self.min_students_spinbox)
        layout.addRow("Maximum Classes per Instructor:", self.max_classes_per_instructor_spinbox)
        layout.addRow("Prioritize First Choice Students:", self.prioritize_combo)
        
        # Save settings button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addRow("", save_btn)
        
        # Add tab
        self.tabs.addTab(settings_widget, "Settings")


    #  BACKEND LOGIC  #
    

    def update_setting(self, key, value):
        self.settings[key] = value
        self.log_activity(f"Updated setting: {key} = {value}")
    
    def save_settings(self):
        # Could save settings to file here if needed
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.log_activity("Settings saved")
    
    def import_students(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Students", "", "Excel Files (*.xlsx *.xls)")
        
        if not filename:
            return
        
        try:
            df = pd.read_excel(filename)
            self.process_student_data(df)
            self.log_activity(f"Imported {len(df)} students from {os.path.basename(filename)}")
            self.update_dashboard_stats()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import students: {str(e)}")
            self.log_activity(f"Error importing students: {str(e)}")
    
    def process_student_data(self, df):
        # Clear existing students
        self.students = {}
        
        # Find class columns - any column that starts with a day of the week
        class_columns = [col for col in df.columns if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', col)]
        
        # Process each student row
        for _, row in df.iterrows():
            student_id = str(row.get('ID', 'Unknown'))
            student_data = row.to_dict()
            student = Student(student_id, student_data)
            self.students[student_id] = student
            
            # Create classes if they don't exist
            for class_name in class_columns:
                fname = ClassPeriod.calculate_name(class_name)[0]  # Commonize class name
                if fname not in self.classes:
                    self.classes[fname] = ClassPeriod(class_name)

        # Update students table
        self.update_students_table()
        self.update_classes_table()
    
    def update_students_table(self):
        self.students_table.setRowCount(0)
        
        for student_id, student in self.students.items():
            row_position = self.students_table.rowCount()
            self.students_table.insertRow(row_position)
            
            # Set student ID
            self.students_table.setItem(row_position, 0, QTableWidgetItem(student_id))

            # Set full name if available
            full_name = student.full_name
            self.students_table.setItem(row_position, 1, QTableWidgetItem(full_name))

            # Set building if available
            building = student.building
            self.students_table.setItem(row_position, 2, QTableWidgetItem(str(building)))

            # List classes
            classes_text = ", ".join([f"{class_name}: {preference}" 
                                     for class_name, preference in student.classes.items() 
                                     if preference])
            self.students_table.setItem(row_position, 3, QTableWidgetItem(classes_text))
    
    def import_instructors(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Instructors", "", "Excel Files (*.xlsx *.xls)")
        
        if not filename:
            return
        
        try:
            df = pd.read_excel(filename)
            self.process_instructor_data(df)
            self.log_activity(f"Imported {len(df)} instructors from {os.path.basename(filename)}")
            self.update_dashboard_stats()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import instructors: {str(e)}")
            self.log_activity(f"Error importing instructors: {str(e)}")
    
    def process_instructor_data(self, df):
        # Clear existing instructors
        self.instructors = {}
        
        # Find class columns - any column that starts with a day of the week
        class_columns = [col for col in df.columns if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', col)]
        
        # Process each instructor row
        for _, row in df.iterrows():
            instructor_id = str(row.get('ID', 'Unknown'))
            instructor_data = row.to_dict()
            instructor = Instructor(instructor_id, instructor_data)
            self.instructors[instructor_id] = instructor
            
            # Create classes if they don't exist
            for class_name in class_columns:
                fname = ClassPeriod.calculate_name(class_name)[0]
                if fname not in self.classes:
                    self.classes[fname] = ClassPeriod(class_name)
        
        # Update instructors table
        self.update_instructors_table()
        self.update_classes_table()
    
    def update_instructors_table(self):
        self.instructors_table.setRowCount(0)
        
        for instructor_id, instructor in self.instructors.items():
            row_position = self.instructors_table.rowCount()
            self.instructors_table.insertRow(row_position)
            
            # Set instructor ID
            self.instructors_table.setItem(row_position, 0, QTableWidgetItem(instructor_id))
            
            # Set full name if available
            full_name = instructor.full_name
            self.instructors_table.setItem(row_position, 1, QTableWidgetItem(full_name))

            # Set teaching preference
            pref = instructor.teach_with_preference
            self.instructors_table.setItem(row_position, 2, QTableWidgetItem(str(pref)))
            
            # List available classes
            available_classes = ", ".join([class_name for class_name, availability in instructor.classes.items() 
                                          if availability and availability.lower() != "does not fit"])
            self.instructors_table.setItem(row_position, 3, QTableWidgetItem(available_classes))
    
    def update_classes_table(self):
        self.classes_table.setRowCount(0)
        
        for class_name, class_obj in self.classes.items():
            row_position = self.classes_table.rowCount()
            self.classes_table.insertRow(row_position)
            
            # Set class name
            self.classes_table.setItem(row_position, 0, QTableWidgetItem(class_name))
            
            # Count potential students (those who marked First Choice or Fits)
            student_count = sum(1 for student in self.students.values() 
                               if class_name in student.classes and 
                               student.classes[class_name] in ["First Choice", "Fits"])
            self.classes_table.setItem(row_position, 1, QTableWidgetItem(str(student_count)))
            
            # Count potential instructors
            instructor_count = sum(1 for instructor in self.instructors.values() 
                                  if class_name in instructor.classes and 
                                  instructor.classes[class_name] != "Does Not Fit")
            self.classes_table.setItem(row_position, 2, QTableWidgetItem(str(instructor_count)))
            
            # Class status
            status = "Ready" if student_count >= self.settings["min_students_per_class"] and instructor_count > 0 else "Not Ready"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("green" if status == "Ready" else "red"))
            self.classes_table.setItem(row_position, 3, status_item)
    
    def add_class_dialog(self):
        # In a real app, we'd create a dialog to add a class manually
        # For simplicity in this example, we'll just show a message
        QMessageBox.information(self, "Add Class", 
                               "This functionality would open a dialog to manually add a class.")
        self.log_activity("Add class dialog opened")
    

    #  SCHEDULE GENERATION LOGIC  #

    # returns a dictionary with class names as keys and a list of scores as values
    def analyze_class_times(self):
        scored_class_times = dict()
        # score class popularity by students
        for student in self.students.keys():
            for class_name, preference in self.students[student].classes.items():
                if preference in ["First Choice", "Fits"]:
                    if class_name not in scored_class_times:
                        scored_class_times[class_name] = [1,0]  # students score, instructor score
                    else:
                        scored_class_times[class_name][0] += 1  # increment student score
        # score class popularity by instructors
        for instructor in self.instructors.keys():
            for class_name, availability in self.instructors[instructor].classes.items():
                if availability != "Does Not Fit":
                    if class_name not in scored_class_times:
                        scored_class_times[class_name] = [0,1]  # students score, instructor score
                    else:
                        scored_class_times[class_name][1] += 1  # increment instructor score
        return scored_class_times
    
    # takes a dictionary of scored class times and cleans it based on min_students_per_class setting
    def clean_class_times(self, class_times):
        # Clean class times to remove classes that have a student score below min_students_per_class setting
        cleaned_classes = {}
        for class_name, scores in class_times.items():
            if scores[0] >= self.settings["min_students_per_class"] or scores[1] > 0:
                cleaned_classes[class_name] = scores
        self.log_activity(f"Cleaned class times, remaining classes: {len(cleaned_classes)} from {len(class_times)}")
        return cleaned_classes

    def generate_schedule(self):
        if not self.students or not self.instructors:
            QMessageBox.warning(self, "Warning", "Please import both students and instructors first.")
            return

        # Clear current schedule
        self.schedule_table.setRowCount(0)
        self.detailed_schedule = []

        assigned_students = set()  # to track assigned students
        assigned_instructors = {}  # to track how many classes each instructor is assigned to
        created_classes = defaultdict(list)  # To hold created class sections

        # Phase 0: Analyze class times and preferences

        self.log_activity("Phase 0: Analyzing class times and preferences...")
        # returns a dict with class names as keys and [student_score, instructor_score] as values
        class_scores = self.analyze_class_times()
        # removes classes that have a student score of < min_students_per_class
        class_scores = self.clean_class_times(class_scores)

        # Phase 1: iterate through students (pickiest first) and assign them to classes

        self.log_activity("Phase 1: Assigning students to classes based on preferences...")
        # Sort students by number of classes they have available (least available first)
        sorted_students = sorted(self.students.values(), key=lambda s: s.flexibility)

        # nested function to avoid repeating code
        # given a list of class names try to enroll the student in one of them
        # if a section already exists with space, enroll them in that
        # if not, create a new section with available instructors
        def try_enroll(student, class_list):
            for class_name in class_list:
                if class_name in class_scores:  # if the class is viable
                    # check if a section already exists with space
                    if class_name in created_classes:
                        # Find an existing section with available space
                        for section in created_classes[class_name]:
                            if len(section.students) < self.settings["max_students_per_class"]:
                                section.students.append(student)
                                assigned_students.add(student.id)
                                self.log_activity(f"Assigned student {student.id} to existing section of {class_name}.")
                                break
                    # check if a section can be created with available instructors
                    available_instructors = [
                        instructor_id for instructor_id, instructor in self.instructors.items()
                        if class_name in instructor.classes and instructor.classes[class_name] != "Does Not Fit"
                        and assigned_instructors.get(instructor_id, 0) < self.settings["max_classes_per_instructor"]
                    ]
                    if student.id not in assigned_students and available_instructors:
                        available_instructors.sort(key=lambda x: assigned_instructors.get(x, 0))
                        selected_instructors = available_instructors[:self.settings["max_instructors_per_class"]]
                        for instructor_id in selected_instructors:
                            assigned_instructors[instructor_id] = assigned_instructors.get(instructor_id, 0) + 1
                        # Create a new section for this class
                        new_section = ClassPeriod(class_name, instructors=selected_instructors)
                        new_section.students.append(student)
                        assigned_students.add(student.id)
                        # Add the new section to created classes
                        created_classes[class_name].append(new_section)
                        self.log_activity(f"Assigned student {student.id} to new section of {class_name}.")
                        break
                else:
                    break # No more viable classes to check

        # iterate through students to assign them to classes
        for student in sorted_students:
            # filter and sort preferences (most popular first) to find most popular classes
            first_choice_classes = [c for c, p in student.classes.items() if p == "First Choice"]
            first_choice_classes.sort(key=lambda c: class_scores.get(c, [0, 0])[0], reverse=True)
            second_choice_classes = [c for c, p in student.classes.items() if p == "Fits"]
            second_choice_classes.sort(key=lambda c: class_scores.get(c, [0, 0])[0], reverse=True)
            # try to assign the student to their first choice class
            try_enroll(student, first_choice_classes)
                
            # try to assign the student to their second choice class if not already assigned
            if student.id not in assigned_students:
                try_enroll(student, second_choice_classes)
            
        self.log_activity(f"Assigned {len(assigned_students)} students to classes in Phase 1.")

        '''
        #  Phase 1: Try to fill existing classes optimally (greedy)  #

        self.log_activity("Phase 1: Filling existing classes...")

        for class_name, class_obj in sorted(self.classes.items(),
                                           key=lambda x: (x[1].day, x[1].start_time if x[1].start_time else "")):
            first_choice_students = [
                student_id for student_id, student in self.students.items()
                if class_name in student.classes and student.classes[class_name] == "First Choice"
                and student_id not in assigned_students
            ]
            fits_students = [
                student_id for student_id, student in self.students.items()
                if class_name in student.classes and student.classes[class_name] == "Fits"
                and student_id not in assigned_students
            ]
            available_instructors = [
                instructor_id for instructor_id, instructor in self.instructors.items()
                if class_name in instructor.classes and instructor.classes[class_name] != "Does Not Fit"
                and assigned_instructors.get(instructor_id, 0) < self.settings["max_classes_per_instructor"]
            ]
            available_instructors.sort(key=lambda x: assigned_instructors.get(x, 0))
            total_potential_students = len(first_choice_students) + len(fits_students)

            if total_potential_students >= self.settings["min_students_per_class"] and len(available_instructors) > 0:
                selected_instructors = available_instructors[:self.settings["max_instructors_per_class"]]
                for instructor_id in selected_instructors:
                    assigned_instructors[instructor_id] = assigned_instructors.get(instructor_id, 0) + 1
                selected_students = first_choice_students[:self.settings["max_students_per_class"]]
                if len(selected_students) < self.settings["max_students_per_class"]:
                    remaining_slots = self.settings["max_students_per_class"] - len(selected_students)
                    selected_students.extend(fits_students[:remaining_slots])
                assigned_students.update(selected_students)
                created_classes.append({
                    'name': class_name,
                    'instructors': selected_instructors,
                    'students': selected_students,
                    'is_additional': False
                })

        #  Phase 2: Assign remaining students, creating new sections as needed  #

        self.log_activity("Phase 2: Assigning remaining students...")

        unassigned_students = set(self.students.keys()) - assigned_students
        class_counter = {}  # Track how many additional instances of each class we've created

        # Build a list of all possible class names (from preferences or all classes)
        all_class_names = list(self.classes.keys())

        while unassigned_students:
            # For each unassigned student, try to assign to a preferred class first
            for student_id in list(unassigned_students):
                student = self.students[student_id]
                # Try to find a preferred class with available instructor
                preferred_classes = [c for c, p in student.classes.items() if p in ["First Choice", "Fits"]]
                assigned = False

                for class_name in preferred_classes + all_class_names:
                    # Try to find or create a section with available space
                    # Find available instructors for this class
                    available_instructors = [
                        instructor_id for instructor_id, instructor in self.instructors.items()
                        if class_name in instructor.classes and instructor.classes[class_name] != "Does Not Fit"
                        and assigned_instructors.get(instructor_id, 0) < self.settings["max_classes_per_instructor"]
                    ]
                    if not available_instructors:
                        continue
                    available_instructors.sort(key=lambda x: assigned_instructors.get(x, 0))
                    selected_instructors = available_instructors[:self.settings["max_instructors_per_class"]]
                    for instructor_id in selected_instructors:
                        assigned_instructors[instructor_id] = assigned_instructors.get(instructor_id, 0) + 1

                    # Try to find an existing section of this class with space
                    found_section = False
                    for class_info in created_classes:
                        if (class_info['name'].startswith(class_name)
                            and len(class_info['students']) < self.settings["max_students_per_class"]
                            and set(class_info['instructors']) == set(selected_instructors)):
                            class_info['students'].append(student_id)
                            assigned_students.add(student_id)
                            found_section = True
                            break
                    if found_section:
                        break

                    # Otherwise, create a new section for this class
                    class_counter[class_name] = class_counter.get(class_name, 0) + 1
                    section_name = class_name
                    if class_counter[class_name] > 1:
                        section_name = f"{class_name} (Section {class_counter[class_name]})"
                    created_classes.append({
                        'name': section_name,
                        'instructors': selected_instructors,
                        'students': [student_id],
                        'is_additional': True
                    })
                    assigned_students.add(student_id)
                    assigned = True
                    break

                if assigned:
                    unassigned_students.remove(student_id)
                else:
                    # If no assignment possible (should not happen unless no instructors at all)
                    self.log_activity(f"Could not assign student {student_id} to any class (no available instructors).")
                    unassigned_students.remove(student_id)

        # Phase 2.5: Balance classes to meet minimum class size 

        self.log_activity("Phase 2.5: Balancing classes to meet minimum size...")

        min_size = self.settings["min_students_per_class"]
        max_size = self.settings["max_students_per_class"]
        avg_size = (min_size + max_size) // 2

        # Find underfilled and overfilled classes
        underfilled = [c for c in created_classes if len(c['students']) < min_size]  # select classes that need students
        overfilled = [c for c in created_classes if len(c['students']) > min_size]  # select classes with students to spare
        # Sort underfilled by size (smallest first) and overfilled by size (largest first)
        underfilled.sort(key=lambda x: len(x['students']))
        overfilled.sort(key=lambda x: -len(x['students']))
        # Try to move students from overfilled to underfilled classes
        for under_class in underfilled:  # from smallest to largest
            needed = min_size - len(under_class['students'])
            deviance = avg_size - len(under_class['students'])

            # try to fill under_class with students that already are not in their first choice
            for over_class in overfilled:  # from largest to smallest 
                # collect students from over_class that are in their 'fits' choice and try to move them to under_class
                for student in over_class['students']:
                    if student not in under_class['students'] and student in self.students:
                        student_obj = self.students[student]
                        if student_obj.classes.get(over_class['name'], '') == 'Fits' and student_obj.classes.get(under_class['name'], '') in ['First Choice', 'Fits']:
                            under_class['students'].append(student)
                            over_class['students'].remove(student)
                            needed -= 1
                            deviance -= 1
                            if deviance <= 0: # reached average size
                                break  # if we filled the under_class to average size, break out of the loop
                    else:   # how did you get here?
                        self.log_activity(f"ERR: Student {student} not found in student data, skipping.")
                        continue
                    # ensure we don't go below minimum size
                    if len(over_class['students']) < min_size:
                        continue  # skip this class if it has no extra students to spare
                # if we filled the under_class to minimum size, break out of the loop
                if needed <= 0:
                    break
            
            # if still needing students:
            if needed > 0:

                for over_class in overfilled:
                    # collect any student that can be moved to under_class
                    for student in over_class['students']:
                        if student not in under_class['students'] and student in self.students:
                            student_obj = self.students[student]
                            if student_obj.classes.get(over_class['name'], '') in ['First Choice', 'Fits'] and student_obj.classes.get(under_class['name'], '') in ['First Choice', 'Fits']:
                                # viable student found, move them
                                under_class['students'].append(student)
                                over_class['students'].remove(student)
                                needed -= 1
                                deviance -= 1
                                if deviance <= 0:  # reached average size or min size 
                                    break  # if we filled the under_class to average size, break out of the loop
                        else:   # how did you get here?
                            self.log_activity(f"ERR: Student {student} not found in student data, skipping.")
                            continue
                    if needed <= 0:
                        break
        '''
        '''
        # Optionally, remove classes that still don't meet the minimum and reassign their students
        removed_classes = []
        for c in list(created_classes):
            if len(c['students']) < min_size:
                # Try to reassign these students to other classes with space
                for student in c['students']:
                    if student in self.students:
                        student_obj = self.students[student]
                        # Find a class with space and the student has availability for
                        assigned = False
                        for target in created_classes:
                            if target is c:
                                continue
                            if len(target['students']) < max_size and student_obj.classes.get(target['name'], '') in ['First Choice', 'Fits']:
                                target['students'].append(student_id)
                                assigned = True
                                break
                        if not assigned:
                            # If no fitting class available, assign to any class with space (missassignment)
                            for target in created_classes:
                                if target is c:
                                    continue
                                if len(target['students']) < max_size:
                                    target['students'].append(student_id)
                                    break
                    else:   # how did you get here?
                        self.log_activity(f"ERR: Student {student} not found in student data, skipping.")
                        continue
                # Mark this class for removal
                removed_classes.append(c)

        for c in removed_classes:
            created_classes.remove(c)
            self.log_activity(f"Removed class '{c['name']}' due to insufficient students after balancing.")
        '''
        # Phase 3: Add all created classes to the schedule
        for class_period, sections in created_classes.items():
            sect_num = 1
            for section in sections:
                self.add_to_schedule_detailed(f"{class_period} [{sect_num}]", section.instructors, section.students)
                sect_num += 1
            
        # Verify preference compliance
        assigned_students = set()
        misassigned_students = []
        # Check each class and its students
        self.log_activity("Verifying student preferences compliance...")
        for class_data in self.detailed_schedule:
            for student in class_data['Students']:
                assigned_students.add(student['ID'])
                # Check that the class is in the student's preferences and is "First Choice" or "Fits"
                student_obj = self.students[student['ID']]
                # The class name may have section info, so check startswith
                found = False
                for class_pref, pref_value in student_obj.classes.items():
                    if class_data['Class Time'].startswith(class_pref) and pref_value in ("First Choice", "Fits"):
                        found = True
                        break
                if not found:
                    misassigned_students.append((student,class_data['Class Time']))
          
        # Log summary
        total_assigned = len(assigned_students)
        total_students = len(self.students)
        unassigned_count = total_students - total_assigned

        self.log_activity(f"Schedule generation complete:")
        self.log_activity(f"- Total classes created: {len(created_classes)}")
        self.log_activity(f"- Students assigned: {total_assigned}/{total_students}")

        if unassigned_count > 0:
            unassigned_list = list(map(lambda x: self.students[x].full_name, list(set(self.students.keys()) - assigned_students)))
            unassigned_list.sort()  # Sort for better readability
            self.log_activity(f"- Students unassigned: {unassigned_count}\n - {'\n - '.join(unassigned_list) if unassigned_count > 0 else ""}")
            # Show warning for unassigned students
            QMessageBox.warning(self, "Unassigned Students",
                f"{unassigned_count} students could not be assigned to any class.\n\n"
                f"This may be due to:\n"
                f"- Insufficient instructor availability\n"
                f"- No suitable class preferences\n"
                f"- Instructor class limits reached\n\n"
                f"Unassigned students: {', '.join(unassigned_list[:10])}"
                f"{'...' if len(unassigned_list) > 10 else ''}")

        if misassigned_students:
            self.log_activity(f"Misassigned students ({len(misassigned_students)}):\n - {'\n - '.join([f'{s['Name']} (ID: {s['ID']}) (Class Time: {t})' for (s,t) in misassigned_students])}")
        else:
            self.log_activity("All students assigned to classes that match their preferences.")
            

        self.update_dashboard_stats()
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tabs.findChild(QWidget, "Schedule")))
        self.log_activity(f"Schedule generated with {self.schedule_table.rowCount()} classes")
        self.update_dashboard_stats()
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tabs.findChild(QWidget, "Schedule")))
    
    def add_to_schedule_detailed(self, class_name, instructor_ids, student_ids):
        row_position = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row_position)
        
        # Set class name/time
        self.schedule_table.setItem(row_position, 0, QTableWidgetItem(class_name))
        
        # Get detailed instructor information
        instructor_details = []
        instructor_display = []
        for instructor_id in instructor_ids:
            instructor = self.instructors.get(instructor_id)
            if instructor:
                # Get instructor name from data, fallback to ID if no name
                instructor_name = instructor.full_name
                instructor_details.append({
                    'ID': instructor_id,
                    'Name': instructor_name
                })
                instructor_display.append(f"{instructor_name} ({instructor_id})")
        
        # Set instructors display
        instructor_text = "\n".join(instructor_display)
        self.schedule_table.setItem(row_position, 1, QTableWidgetItem(instructor_text))
        
        # Get detailed student information
        student_details = []
        student_display = []
        for student_id in student_ids:
            student = self.students.get(student_id)
            if student:
                # Get student name from data, fallback to ID if no name
                student_name = student.full_name
                building = student.building
                
                student_details.append({
                    'ID': student_id,
                    'Name': student_name,
                    'Building': building
                })
                student_display.append(f"{student_name} ({student_id})")
        
        # Set student count
        student_count = len(student_ids)
        student_text = f"{student_count} students"
        self.schedule_table.setItem(row_position, 3, QTableWidgetItem(student_text))
        
        # Set detailed student information (truncated for display)
        if len(student_display) <= 5:
            student_details_text = "\n".join(student_display)
        else:
            student_details_text = "\n".join(student_display[:5]) + f"\n... and {len(student_display) - 5} more"
        
        self.schedule_table.setItem(row_position, 2, QTableWidgetItem(student_details_text))
        '''
        # Set status
        status = "Scheduled"
        self.schedule_table.setItem(row_position, 5, QTableWidgetItem(status))
        '''
        # Store detailed information for export
        class_data = {
            'Class Time': class_name,
            'Instructors': instructor_details,
            'Students': student_details,
            'Room': 'TBD',
            'Status': 'Scheduled'
        }
        self.detailed_schedule.append(class_data)
    

    """ I/O - SCHEDULE EXPORT LOGIC """


    def export_schedule(self):  #TODO: fix formatting on file
        if self.schedule_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please generate a schedule first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Schedule", "", "Excel Files (*.xlsx)")
        
        if not filename:
            return
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        try:
            # Create detailed schedule data for export
            export_data = []
            
            for class_data in self.detailed_schedule:
                # Create a row for each class with detailed information
                base_row = {
                    'Class Time': class_data['Class Time'],
                    'Room': class_data['Room'],
                    'Status': class_data['Status'],
                    'Total Students': len(class_data['Students']),
                    'Total Instructors': len(class_data['Instructors'])
                }
                
                # Add instructor details
                instructor_names = []
                instructor_ids = []
                for instructor in class_data['Instructors']:
                    instructor_names.append(instructor['Name'])
                    instructor_ids.append(instructor['ID'])
                
                base_row['Instructor Names'] = '; '.join(instructor_names)
                base_row['Instructor IDs'] = '; '.join(instructor_ids)
                
                # Add student details
                student_names = []
                student_ids = []
                student_buildings = []
                for student in class_data['Students']:
                    student_names.append(student['Name'])
                    student_ids.append(student['ID'])
                    student_buildings.append(student['Building'])
                
                base_row['Student Names'] = '; '.join(student_names)
                base_row['Student IDs'] = '; '.join(student_ids)
                base_row['Student Buildings'] = '; '.join(student_buildings)
                
                export_data.append(base_row)
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            
            # Reorder columns for better readability
            column_order = [
                'Class Time', 'Total Students', 'Total Instructors',
                'Instructor Names', 'Instructor IDs',
                'Student Names', 'Student IDs', 'Student Buildings',
                'Room', 'Status'
            ]
            
            df = df[column_order]
            
            # Create Excel writer with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main schedule sheet
                df.to_excel(writer, sheet_name='Schedule Summary', index=False)
                
                # Detailed breakdown sheet
                detailed_breakdown = []
                for class_data in self.detailed_schedule:
                    class_name = class_data['Class Time']
                    
                    # Add instructors for this class
                    for instructor in class_data['Instructors']:
                        detailed_breakdown.append({
                            'Class Time': class_name,
                            'Type': 'Instructor',
                            'ID': instructor['ID'],
                            'Name': instructor['Name'],
                            'Building': 'N/A'
                        })
                    
                    # Add students for this class
                    for student in class_data['Students']:
                        detailed_breakdown.append({
                            'Class Time': class_name,
                            'Type': 'Student',
                            'ID': student['ID'],
                            'Name': student['Name'],
                            'Building': student['Building']
                        })
                    
                    # Add a line break between classes for clarity
                    detailed_breakdown.append({
                        'Class Time': '',
                        'Type': '',
                        'ID': '',
                        'Name': '',
                        'Building': ''
                    })
                detailed_df = pd.DataFrame(detailed_breakdown)
                if not detailed_df.empty:
                    detailed_df.to_excel(writer, sheet_name='Detailed Assignments', index=False)
            
                # Set column widths for 'Schedule Summary' sheet
                worksheet = writer.sheets['Schedule Summary']
                for col in df.columns:
                    max_length = max(df[col].astype(str).map(len).max(), len(col))
                    col_letter = openpyxl.utils.get_column_letter(df.columns.get_loc(col) + 1)
                    worksheet.column_dimensions[col_letter].width = max_length + 2
                
                # Set column widths for 'Detailed Assignments' sheet
                detailed_worksheet = writer.sheets['Detailed Assignments']
                for col in detailed_df.columns:
                    max_length = max(detailed_df[col].astype(str).map(len).max(), len(col))
                    col_letter = openpyxl.utils.get_column_letter(detailed_df.columns.get_loc(col) + 1)
                    detailed_worksheet.column_dimensions[col_letter].width = max_length + 2

            QMessageBox.information(self, "Export", "Schedule exported successfully!\n\nThe file contains:\n- Schedule Summary: Overview of each class\n- Detailed Assignments: Individual student and instructor assignments")
            self.log_activity(f"Detailed schedule exported to {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export schedule: {str(e)}")
            self.log_activity(f"Error exporting schedule: {str(e)}")
    
    """ STUDENT/INSTRUCTOR MANAGEMENT LOGIC """

    def clear_students(self):
        reply = QMessageBox.question(self, "Clear Students", 
                                    "Are you sure you want to clear all students?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.students = {}
            self.update_students_table()
            self.log_activity("All students cleared")
            self.update_dashboard_stats()
    
    def clear_instructors(self):
        reply = QMessageBox.question(self, "Clear Instructors", 
                                    "Are you sure you want to clear all instructors?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.instructors = {}
            self.update_instructors_table()
            self.log_activity("All instructors cleared")
            self.update_dashboard_stats()
    
    def clear_classes(self):
        reply = QMessageBox.question(self, "Clear Classes", 
                                    "Are you sure you want to clear all classes?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.classes = {}
            self.update_classes_table()
            self.log_activity("All classes cleared")
            self.update_dashboard_stats()
    
    def log_activity(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def update_dashboard_stats(self):
        # Update dashboard statistics
        student_count_label = self.findChild(QLabel, "students_count")
        if student_count_label:
            student_count_label.setText(str(len(self.students)))
        
        instructor_count_label = self.findChild(QLabel, "instructors_count")
        if instructor_count_label:
            instructor_count_label.setText(str(len(self.instructors)))
        
        class_count_label = self.findChild(QLabel, "classes_count")
        if class_count_label:
            class_count_label.setText(str(len(self.classes)))
        
        scheduled_count_label = self.findChild(QLabel, "scheduled_count")
        if scheduled_count_label:
            scheduled_count_label.setText(str(self.schedule_table.rowCount()))
