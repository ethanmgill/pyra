import sys
import os
import openpyxl
import pandas as pd
from datetime import datetime
import re
from settings import Settings, Setting
from student import Student
from instructor import Instructor
from class_period import ClassPeriod
from class_scheduler_app import ClassSchedulerAppGUI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QTabWidget, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QComboBox, QSpinBox,
                            QFormLayout, QLineEdit, QGroupBox, QTextEdit,
                            QProgressBar, QSplitter, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = Settings()
    window = ClassSchedulerAppGUI(settings)
    window.show()
    sys.exit(app.exec_())
