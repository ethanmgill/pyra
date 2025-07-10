from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
import sys
from pyra import ClassSchedulerApp

def main():
    app = QApplication(sys.argv)
    window = ClassSchedulerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()