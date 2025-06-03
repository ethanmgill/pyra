import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# TODO: any external file accesses need to be modified to use this function
# Get the base directory for resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ClassOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Organizer")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Initialize data
        self.students = []
        self.teachers = []
        self.classes = []
        self.load_data()
        
        # Set up the main container with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.students_tab = ttk.Frame(self.notebook)
        self.teachers_tab = ttk.Frame(self.notebook)
        self.classes_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.students_tab, text="Students")
        self.notebook.add(self.teachers_tab, text="Teachers")
        self.notebook.add(self.classes_tab, text="Classes")
        
        # Set up each tab
        self.setup_students_tab()
        self.setup_teachers_tab()
        self.setup_classes_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set a custom style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=('Helvetica', 10))
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def get_data_directory():
        """Get the directory to store application data"""
        if sys.platform == "win32":
            data_dir = os.path.join(os.environ["APPDATA"], "Class Organizer")
        else:
            data_dir = os.path.join(os.path.expanduser("~"), ".config", "class-organizer")
        
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def load_data(self):
        """Load data from JSON files if they exist"""
        data_dir = get_data_directory()
        try:
            students_file = os.path.join(data_dir, "students.json")
            teachers_file = os.path.join(data_dir, "teachers.json") 
            classes_file = os.path.join(data_dir, "classes.json")
            
            if os.path.exists(students_file):
                with open(students_file, "r") as f:
                    self.students = json.load(f)
            if os.path.exists(teachers_file):
                with open(teachers_file, "r") as f:
                    self.teachers = json.load(f)
            if os.path.exists(classes_file):
                with open(classes_file, "r") as f:
                    self.classes = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def save_data(self):
        """Save data to JSON files"""
        data_dir = get_data_directory()
        try:
            students_file = os.path.join(data_dir, "students.json")
            teachers_file = os.path.join(data_dir, "teachers.json") 
            classes_file = os.path.join(data_dir, "classes.json")
            
            with open(students_file, "w") as f:
                json.dump(self.students, f, indent=2)
            with open(teachers_file, "w") as f:
                json.dump(self.teachers, f, indent=2)
            with open(classes_file, "w") as f:
                json.dump(self.classes, f, indent=2)
            self.status_var.set("Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def setup_students_tab(self):
        """Set up the Students tab"""
        # Left frame for list
        left_frame = ttk.Frame(self.students_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Toolbar buttons
        add_btn = ttk.Button(toolbar, text="Add Student", command=self.add_student)
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_btn = ttk.Button(toolbar, text="Delete", command=self.delete_student)
        delete_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Student listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.student_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.student_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.student_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.student_listbox.yview)
        
        # Right frame for details
        right_frame = ttk.Frame(self.students_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Student details
        details_frame = ttk.LabelFrame(right_frame, text="Student Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Student form
        ttk.Label(details_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.first_name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.last_name_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Student ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.student_id_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.student_id_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Grade:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.grade_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.grade_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.notes_text = tk.Text(details_frame, height=5, width=30)
        self.notes_text.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(details_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_btn = ttk.Button(buttons_frame, text="Save", command=self.save_student)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_student_form)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        
        # Load students into listbox
        self.refresh_student_list()
        
        # Bind listbox selection event
        self.student_listbox.bind('<<ListboxSelect>>', self.on_student_select)
    
    def setup_teachers_tab(self):
        """Set up the Teachers tab"""
        # Left frame for list
        left_frame = ttk.Frame(self.teachers_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Toolbar buttons
        add_btn = ttk.Button(toolbar, text="Add Teacher", command=self.add_teacher)
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_btn = ttk.Button(toolbar, text="Delete", command=self.delete_teacher)
        delete_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Teacher listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.teacher_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.teacher_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.teacher_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.teacher_listbox.yview)
        
        # Right frame for details
        right_frame = ttk.Frame(self.teachers_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Teacher details
        details_frame = ttk.LabelFrame(right_frame, text="Teacher Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Teacher form
        ttk.Label(details_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.teacher_first_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.teacher_first_name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.teacher_last_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.teacher_last_name_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Employee ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.employee_id_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.employee_id_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Subject:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.subject_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.teacher_notes_text = tk.Text(details_frame, height=5, width=30)
        self.teacher_notes_text.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(details_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_btn = ttk.Button(buttons_frame, text="Save", command=self.save_teacher)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_teacher_form)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        
        # Load teachers into listbox
        self.refresh_teacher_list()
        
        # Bind listbox selection event
        self.teacher_listbox.bind('<<ListboxSelect>>', self.on_teacher_select)
    
    def setup_classes_tab(self):
        """Set up the Classes tab"""
        # Left frame for list
        left_frame = ttk.Frame(self.classes_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Toolbar buttons
        add_btn = ttk.Button(toolbar, text="Add Class", command=self.add_class)
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_btn = ttk.Button(toolbar, text="Delete", command=self.delete_class)
        delete_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Class listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.class_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.class_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.class_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.class_listbox.yview)
        
        # Right frame for details
        right_frame = ttk.Frame(self.classes_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Class details
        details_frame = ttk.LabelFrame(right_frame, text="Class Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Class form
        ttk.Label(details_frame, text="Class Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.class_name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Room:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.room_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.room_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(details_frame, text="Period:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.period_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.period_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Teacher selection
        ttk.Label(details_frame, text="Teacher:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.teacher_var = tk.StringVar()
        self.teacher_combo = ttk.Combobox(details_frame, textvariable=self.teacher_var)
        self.teacher_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.update_teacher_combo()
        
        # Students list (multi-select)
        ttk.Label(details_frame, text="Students:").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=5)
        
        students_frame = ttk.Frame(details_frame)
        students_frame.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.students_listbox = tk.Listbox(students_frame, selectmode=tk.MULTIPLE, height=6)
        self.students_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        students_scrollbar = ttk.Scrollbar(students_frame)
        students_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.students_listbox.config(yscrollcommand=students_scrollbar.set)
        students_scrollbar.config(command=self.students_listbox.yview)
        
        self.update_students_listbox()
        
        # Buttons
        buttons_frame = ttk.Frame(details_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_btn = ttk.Button(buttons_frame, text="Save", command=self.save_class)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_class_form)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure column weights
        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(4, weight=1)
        
        # Load classes into listbox
        self.refresh_class_list()
        
        # Bind listbox selection event
        self.class_listbox.bind('<<ListboxSelect>>', self.on_class_select)
    
    # Student methods
    def add_student(self):
        """Prepare to add a new student"""
        self.clear_student_form()
        self.status_var.set("Adding new student...")
    
    def save_student(self):
        """Save student data"""
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        student_id = self.student_id_var.get().strip()
        grade = self.grade_var.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not first_name or not last_name or not student_id:
            messagebox.showwarning("Missing Information", "Please enter first name, last name, and student ID.")
            return
        
        # Check if we're editing an existing student
        selected = self.student_listbox.curselection()
        
        if selected:
            # Update existing student
            index = selected[0]
            self.students[index] = {
                "first_name": first_name,
                "last_name": last_name,
                "student_id": student_id,
                "grade": grade,
                "notes": notes
            }
            self.status_var.set(f"Updated student: {first_name} {last_name}")
        else:
            # Add new student
            self.students.append({
                "first_name": first_name,
                "last_name": last_name,
                "student_id": student_id,
                "grade": grade,
                "notes": notes
            })
            self.status_var.set(f"Added new student: {first_name} {last_name}")
        
        self.save_data()
        self.refresh_student_list()
        self.clear_student_form()
        self.update_students_listbox()  # Update student lists in classes tab
    
    def delete_student(self):
        """Delete selected student"""
        selected = self.student_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Please select a student to delete.")
            return
        
        index = selected[0]
        student = self.students[index]
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {student['first_name']} {student['last_name']}?")
        
        if confirm:
            del self.students[index]
            self.save_data()
            self.refresh_student_list()
            self.clear_student_form()
            self.status_var.set(f"Deleted student: {student['first_name']} {student['last_name']}")
            self.update_students_listbox()  # Update student lists in classes tab
    
    def clear_student_form(self):
        """Clear the student form fields"""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.student_id_var.set("")
        self.grade_var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.student_listbox.selection_clear(0, tk.END)
    
    def refresh_student_list(self):
        """Refresh the student listbox"""
        self.student_listbox.delete(0, tk.END)
        for student in self.students:
            self.student_listbox.insert(tk.END, f"{student['first_name']} {student['last_name']} ({student['student_id']})")
    
    def on_student_select(self, event):
        """Handle student selection"""
        selected = self.student_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        student = self.students[index]
        
        self.first_name_var.set(student['first_name'])
        self.last_name_var.set(student['last_name'])
        self.student_id_var.set(student['student_id'])
        self.grade_var.set(student.get('grade', ''))
        
        self.notes_text.delete("1.0", tk.END)
        if 'notes' in student:
            self.notes_text.insert("1.0", student['notes'])
        
        self.status_var.set(f"Selected student: {student['first_name']} {student['last_name']}")
    
    # Teacher methods
    def add_teacher(self):
        """Prepare to add a new teacher"""
        self.clear_teacher_form()
        self.status_var.set("Adding new teacher...")
    
    def save_teacher(self):
        """Save teacher data"""
        first_name = self.teacher_first_name_var.get().strip()
        last_name = self.teacher_last_name_var.get().strip()
        employee_id = self.employee_id_var.get().strip()
        subject = self.subject_var.get().strip()
        notes = self.teacher_notes_text.get("1.0", tk.END).strip()
        
        if not first_name or not last_name or not employee_id:
            messagebox.showwarning("Missing Information", "Please enter first name, last name, and employee ID.")
            return
        
        # Check if we're editing an existing teacher
        selected = self.teacher_listbox.curselection()
        
        if selected:
            # Update existing teacher
            index = selected[0]
            self.teachers[index] = {
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": employee_id,
                "subject": subject,
                "notes": notes
            }
            self.status_var.set(f"Updated teacher: {first_name} {last_name}")
        else:
            # Add new teacher
            self.teachers.append({
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": employee_id,
                "subject": subject,
                "notes": notes
            })
            self.status_var.set(f"Added new teacher: {first_name} {last_name}")
        
        self.save_data()
        self.refresh_teacher_list()
        self.clear_teacher_form()
        self.update_teacher_combo()  # Update teacher combo in classes tab
    
    def delete_teacher(self):
        """Delete selected teacher"""
        selected = self.teacher_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Please select a teacher to delete.")
            return
        
        index = selected[0]
        teacher = self.teachers[index]
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete {teacher['first_name']} {teacher['last_name']}?")
        
        if confirm:
            del self.teachers[index]
            self.save_data()
            self.refresh_teacher_list()
            self.clear_teacher_form()
            self.status_var.set(f"Deleted teacher: {teacher['first_name']} {teacher['last_name']}")
            self.update_teacher_combo()  # Update teacher combo in classes tab
    
    def clear_teacher_form(self):
        """Clear the teacher form fields"""
        self.teacher_first_name_var.set("")
        self.teacher_last_name_var.set("")
        self.employee_id_var.set("")
        self.subject_var.set("")
        self.teacher_notes_text.delete("1.0", tk.END)
        self.teacher_listbox.selection_clear(0, tk.END)
    
    def refresh_teacher_list(self):
        """Refresh the teacher listbox"""
        self.teacher_listbox.delete(0, tk.END)
        for teacher in self.teachers:
            self.teacher_listbox.insert(tk.END, f"{teacher['first_name']} {teacher['last_name']} ({teacher['subject']})")
    
    def on_teacher_select(self, event):
        """Handle teacher selection"""
        selected = self.teacher_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        teacher = self.teachers[index]
        
        self.teacher_first_name_var.set(teacher['first_name'])
        self.teacher_last_name_var.set(teacher['last_name'])
        self.employee_id_var.set(teacher['employee_id'])
        self.subject_var.set(teacher.get('subject', ''))
        
        self.teacher_notes_text.delete("1.0", tk.END)
        if 'notes' in teacher:
            self.teacher_notes_text.insert("1.0", teacher['notes'])
        
        self.status_var.set(f"Selected teacher: {teacher['first_name']} {teacher['last_name']}")
    
    # Class methods
    def add_class(self):
        """Prepare to add a new class"""
        self.clear_class_form()
        self.status_var.set("Adding new class...")
    
    def save_class(self):
        """Save class data"""
        class_name = self.class_name_var.get().strip()
        room = self.room_var.get().strip()
        period = self.period_var.get().strip()
        teacher = self.teacher_var.get().strip()
        
        if not class_name:
            messagebox.showwarning("Missing Information", "Please enter class name.")
            return
        
        # Get selected students
        selected_students = [self.students_listbox.get(idx) for idx in self.students_listbox.curselection()]
        
        # Check if we're editing an existing class
        selected = self.class_listbox.curselection()
        
        if selected:
            # Update existing class
            index = selected[0]
            self.classes[index] = {
                "name": class_name,
                "room": room,
                "period": period,
                "teacher": teacher,
                "students": selected_students
            }
            self.status_var.set(f"Updated class: {class_name}")
        else:
            # Add new class
            self.classes.append({
                "name": class_name,
                "room": room,
                "period": period,
                "teacher": teacher,
                "students": selected_students
            })
            self.status_var.set(f"Added new class: {class_name}")
        
        self.save_data()
        self.refresh_class_list()
        self.clear_class_form()
    
    def delete_class(self):
        """Delete selected class"""
        selected = self.class_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Please select a class to delete.")
            return
        
        index = selected[0]
        class_item = self.classes[index]
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete {class_item['name']}?")
        
        if confirm:
            del self.classes[index]
            self.save_data()
            self.refresh_class_list()
            self.clear_class_form()
            self.status_var.set(f"Deleted class: {class_item['name']}")
    
    def clear_class_form(self):
        """Clear the class form fields"""
        self.class_name_var.set("")
        self.room_var.set("")
        self.period_var.set("")
        self.teacher_var.set("")
        self.students_listbox.selection_clear(0, tk.END)
        self.class_listbox.selection_clear(0, tk.END)

    def refresh_class_list(self):
        """Refresh the class listbox"""
        self.class_listbox.delete(0, tk.END)
        for class_item in self.classes:
            self.class_listbox.insert(tk.END, f"{class_item['name']} - {class_item.get('period', 'N/A')}")
    
    def on_class_select(self, event):
        """Handle class selection"""
        selected = self.class_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        class_item = self.classes[index]
        
        self.class_name_var.set(class_item['name'])
        self.room_var.set(class_item.get('room', ''))
        self.period_var.set(class_item.get('period', ''))
        self.teacher_var.set(class_item.get('teacher', ''))
        
        # Clear and update student selections
        self.students_listbox.selection_clear(0, tk.END)
        for i in range(self.students_listbox.size()):
            student_name = self.students_listbox.get(i)
            if student_name in class_item.get('students', []):
                self.students_listbox.selection_set(i)
        
        self.status_var.set(f"Selected class: {class_item['name']}")
    
    def update_teacher_combo(self):
        """Update teacher combobox"""
        teacher_names = []
        for teacher in self.teachers:
            teacher_names.append(f"{teacher['first_name']} {teacher['last_name']}")
        
        self.teacher_combo['values'] = teacher_names
    
    def update_students_listbox(self):
        """Update students listbox in classes tab"""
        self.students_listbox.delete(0, tk.END)
        for student in self.students:
            self.students_listbox.insert(tk.END, f"{student['first_name']} {student['last_name']}")
    
    def on_close(self):
        """Handle window close event"""
        if messagebox.askyesno("Save Data", "Do you want to save your data before exiting?"):
            self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassOrganizerApp(root)
    root.mainloop()