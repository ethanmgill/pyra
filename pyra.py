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
from PyQt5.QtWidgets import (QApplication)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = Settings()
    window = ClassSchedulerAppGUI(settings)
    window.show()
    sys.exit(app.exec_())
