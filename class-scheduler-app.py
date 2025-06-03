import sys
import os
import pandas as pd
from datetime import datetime
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QTabWidget, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QComboBox, QSpinBox,
                            QFormLayout, QLineEdit, QGroupBox, QTextEdit,
                            QProgressBar, QSplitter, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

class Student:
    def __init__(self, student_id, data):
        self.id = student_id
        self.data = data
        self.classes = {}  # Dictionary to store class preferences
        self.building = "N/A"
        
        # Process data to extract and clean data #
        for column, value in data.items():
            # Class data (extract)
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', column):
                self.classes[column] = value if pd.notna(value) else ""
            # Building assignment (clean)
            elif re.match(r'^Building', column):
                self.building = data.get(column)

class Instructor:
    def __init__(self, instructor_id, data):
        self.id = instructor_id
        self.data = data
        self.classes = {}  # Dictionary to store class availability
        self.teach_with_preference = "No Preference"
        
        # Process data to extract class availability and preferences
        for column, value in data.items():
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', column):
                self.classes[column] = value if pd.notna(value) else ""
            elif column == "Would you like to teach with someone else?":
                self.teach_with_preference = value if pd.notna(value) else "No Preference"

class ClassPeriod:
    def __init__(self, name):
        self.name = name
        self.students = []
        self.instructors = []
        self.day = name.split()[0] if " " in name else ""
        
        # Extract time from format "Day HH:MMam/pm-HH:MMam/pm"
        #TODO: ensure 1PM-3PM == 1:00pm - 3:00pm
        time_pattern = r'(\d+)(:\d+)((?:am|pm))-(\d+)(:\d+)((?:am|pm))'
        time_match = re.search(time_pattern, name)
        
        if time_match:
            print(time_match.group(2))
            self.start_time = time_match.group(1) + time_match.group(2) + time_match.group(3)
            self.end_time =   time_match.group(4) + time_match.group(5) + time_match.group(6)

        else:
            self.start_time = ""
            self.end_time = ""
        
        self.name = self.day + self.start_time + self.end_time #TODO: make faster

class ClassSchedulerApp(QMainWindow):
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
            "prioritize_first_choice": True
        }
        
        # Setup UI
        self.setup_ui()
        
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
            {"title": "Scheduled Classes", "value": "0", "id": "scheduled_count"}
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
        self.students_table.setHorizontalHeaderLabels(["Student ID", "Building", "Data Points", "Classes"])
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
        self.instructors_table = QTableWidget(0, 3)  # Start with 3 columns
        self.instructors_table.setHorizontalHeaderLabels(
            ["Instructor ID", "Teach with Others", "Available Classes"])
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
        self.schedule_table = QTableWidget(0, 5)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Class Time", "Instructors", "Students", "Room", "Status"])
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
        
        self.prioritize_combo = QComboBox()
        self.prioritize_combo.addItems(["Yes", "No"])
        self.prioritize_combo.setCurrentText("Yes" if self.settings["prioritize_first_choice"] else "No")
        self.prioritize_combo.currentTextChanged.connect(
            lambda text: self.update_setting("prioritize_first_choice", text == "Yes"))
        
        # Add fields to layout
        layout.addRow("Maximum Students per Class:", self.max_students_spinbox)
        layout.addRow("Maximum Instructors per Class:", self.max_instructors_spinbox)
        layout.addRow("Minimum Students for Class to Run:", self.min_students_spinbox)
        layout.addRow("Prioritize First Choice Students:", self.prioritize_combo)
        
        # Save settings button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addRow("", save_btn)
        
        # Add tab
        self.tabs.addTab(settings_widget, "Settings")
    
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
                if class_name not in self.classes:
                    self.classes[class_name] = ClassPeriod(class_name)
        
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
            
            # Set building if available
            building = student.building
            self.students_table.setItem(row_position, 1, QTableWidgetItem(str(building)))
            
            # Count data points
            data_points = sum(1 for key in student.data if key not in ['ID', 'Building'] and pd.notna(student.data[key]))
            self.students_table.setItem(row_position, 2, QTableWidgetItem(str(data_points)))
            
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
                if class_name not in self.classes:
                    self.classes[class_name] = ClassPeriod(class_name)
        
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
            
            # Set teaching preference
            pref = instructor.teach_with_preference
            self.instructors_table.setItem(row_position, 1, QTableWidgetItem(str(pref)))
            
            # List available classes
            available_classes = ", ".join([class_name for class_name, availability in instructor.classes.items() 
                                          if availability and availability.lower() != "does not fit"])
            self.instructors_table.setItem(row_position, 2, QTableWidgetItem(available_classes))
    
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
    
    def generate_schedule(self):
        if not self.students or not self.instructors:
            QMessageBox.warning(self, "Warning", "Please import both students and instructors first.")
            return
        
        # Clear current schedule
        self.schedule_table.setRowCount(0)
        
        # Track assigned students and instructors
        assigned_students = set()
        assigned_instructors = {}  # Dict to track number of classes per instructor
        
        # Process classes by day/time
        for class_name, class_obj in sorted(self.classes.items(), 
                                           key=lambda x: (x[1].day, x[1].start_time if x[1].start_time else "")):
            # Get potential students for this class
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
            
            # Get potential instructors for this class
            available_instructors = [
                instructor_id for instructor_id, instructor in self.instructors.items()
                if class_name in instructor.classes and instructor.classes[class_name] != "Does Not Fit"
                and (instructor_id not in assigned_instructors or 
                     assigned_instructors[instructor_id] < 2)  # Limit instructors to 2 classes
            ]
            
            # Prioritize instructors with fewer assigned classes
            available_instructors.sort(key=lambda x: assigned_instructors.get(x, 0))
            
            # Check if we have enough students and instructors
            total_potential_students = len(first_choice_students) + len(fits_students)
            
            if (total_potential_students >= self.settings["min_students_per_class"] and 
                len(available_instructors) > 0):
                
                # Assign instructors (up to max_instructors_per_class)
                selected_instructors = available_instructors[:self.settings["max_instructors_per_class"]]
                
                # Update assigned instructors count
                for instructor_id in selected_instructors:
                    assigned_instructors[instructor_id] = assigned_instructors.get(instructor_id, 0) + 1
                
                # First prioritize First Choice students
                selected_students = first_choice_students
                
                # If we need more students, add from Fits category
                if len(selected_students) < self.settings["max_students_per_class"]:
                    remaining_slots = self.settings["max_students_per_class"] - len(selected_students)
                    selected_students.extend(fits_students[:remaining_slots])
                
                # If we have too many students, cap at maximum
                if len(selected_students) > self.settings["max_students_per_class"]:
                    selected_students = selected_students[:self.settings["max_students_per_class"]]
                
                # Mark these students as assigned
                assigned_students.update(selected_students)
                
                # Add to schedule table
                self.add_to_schedule(class_name, selected_instructors, selected_students)
        
        self.log_activity(f"Schedule generated with {self.schedule_table.rowCount()} classes")
        self.update_dashboard_stats()
        
        # Switch to schedule tab
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tabs.findChild(QWidget, "Schedule")))
    
    def add_to_schedule(self, class_name, instructor_ids, student_ids):
        row_position = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row_position)
        
        # Set class name/time
        self.schedule_table.setItem(row_position, 0, QTableWidgetItem(class_name))
        
        # Set instructors
        instructor_names = ", ".join(instructor_ids)
        self.schedule_table.setItem(row_position, 1, QTableWidgetItem(instructor_names))
        
        # Set students
        student_count = len(student_ids)
        student_text = f"{student_count} students"
        self.schedule_table.setItem(row_position, 2, QTableWidgetItem(student_text))
        
        # Set room (placeholder)
        self.schedule_table.setItem(row_position, 3, QTableWidgetItem("TBD"))
        
        # Set status
        status = "Scheduled"
        self.schedule_table.setItem(row_position, 4, QTableWidgetItem(status))
    
    def export_schedule(self):
        if self.schedule_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please generate a schedule first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Schedule", "", "Excel Files (*.xlsx)")
        
        if not filename:
            return
        
        try:
            # Create a dataframe from the schedule table
            rows = []
            for row in range(self.schedule_table.rowCount()):
                row_data = {}
                row_data["Class Time"] = self.schedule_table.item(row, 0).text()
                row_data["Instructors"] = self.schedule_table.item(row, 1).text()
                row_data["Students"] = self.schedule_table.item(row, 2).text()
                row_data["Room"] = self.schedule_table.item(row, 3).text()
                row_data["Status"] = self.schedule_table.item(row, 4).text()
                rows.append(row_data)
            
            df = pd.DataFrame(rows)
            
            # Export to Excel
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "Export", "Schedule exported successfully!")
            self.log_activity(f"Schedule exported to {os.path.basename(filename)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export schedule: {str(e)}")
            self.log_activity(f"Error exporting schedule: {str(e)}")
    
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClassSchedulerApp()
    window.show()
    sys.exit(app.exec_())
