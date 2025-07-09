from schedule_engine import ClassScheduler
from collections import defaultdict
import sys
import os
import openpyxl
import pandas as pd
import schedule_engine as se
from datetime import datetime
import re
from settings import Settings, Setting
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


class ClassSchedulerAppGUI(QMainWindow):

    #                                                   #
    #  Main application class for the Class Scheduler.  #
    #                                                   #

    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("Class Scheduler")
        self.setMinimumSize(1200, 800)
        
        # Backend
        self.scheduler = ClassScheduler()

        # Application data
        self.students = {}
        self.instructors = {}
        self.classes = {}
        
        # Settings with defaults
        self.settings = settings
        
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
        generate_schedule_btn.clicked.connect(self.scheduler.generate_schedule)
        
        export_schedule_btn = QPushButton("Export Schedule")
        export_schedule_btn.clicked.connect(self.scheduler.export_schedule)
        
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
        self.max_students_spinbox.setValue(self.settings.get_setting(Setting.MAX_STUDENTS_PER_CLASS))
        self.max_students_spinbox.valueChanged.connect(
            lambda val: self.update_setting(Setting.MAX_STUDENTS_PER_CLASS, val))
        
        self.max_instructors_spinbox = QSpinBox()
        self.max_instructors_spinbox.setRange(1, 10)
        self.max_instructors_spinbox.setValue(self.settings.get_setting(Setting.MAX_INSTRUCTORS_PER_CLASS))
        self.max_instructors_spinbox.valueChanged.connect(
            lambda val: self.update_setting(Setting.MAX_INSTRUCTORS_PER_CLASS, val))
        
        self.min_students_spinbox = QSpinBox()
        self.min_students_spinbox.setRange(1, 50)
        self.min_students_spinbox.setValue(self.settings.get_setting(Setting.MIN_STUDENTS_PER_CLASS))
        self.min_students_spinbox.valueChanged.connect(
            lambda val: self.update_setting(Setting.MIN_STUDENTS_PER_CLASS, val))
        
        self.max_classes_per_instructor_spinbox = QSpinBox()
        self.max_classes_per_instructor_spinbox.setRange(1, 10)
        self.max_classes_per_instructor_spinbox.setValue(self.settings.get_setting(Setting.MAX_CLASSES_PER_INSTRUCTOR))
        self.max_classes_per_instructor_spinbox.valueChanged.connect(
            lambda val: self.update_setting(Setting.MAX_CLASSES_PER_INSTRUCTOR, val))

        self.prioritize_combo = QComboBox()
        self.prioritize_combo.addItems(["Yes", "No"])
        self.prioritize_combo.setCurrentText("Yes" if self.settings.get_setting(Setting.PRIORITIZE_FIRST_CHOICE) else "No")
        self.prioritize_combo.currentTextChanged.connect(
            lambda text: self.update_setting(Setting.PRIORITIZE_FIRST_CHOICE, text == "Yes"))
        
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

    #                 #
    #  BACKEND LOGIC  #
    #                 #

    def update_setting(self, key, value):
        self.settings.set_setting(key, value)  # Update settings class
        self.log_activity(f"Updated setting: {key} = {value}")
    
    def save_settings(self):
        # Could save settings to file here if needed
        if self.settings.save_settings():
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
        else:
            QMessageBox.warning(self, "Settings", "Failed to save settings.")
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
            status = "Ready" if student_count >= self.settings.get_setting(Setting.MIN_STUDENTS_PER_CLASS) and instructor_count > 0 else "Not Ready"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("green" if status == "Ready" else "red"))
            self.classes_table.setItem(row_position, 3, status_item)
    
    def add_class_dialog(self):
        # In a real app, we'd create a dialog to add a class manually
        # For simplicity in this example, we'll just show a message
        QMessageBox.information(self, "Add Class", 
                               "This functionality would open a dialog to manually add a class.")
        self.log_activity("Add class dialog opened")