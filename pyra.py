import sys
import re
from settings import Settings
from gui import ClassSchedulerAppGUI
from PyQt5.QtWidgets import (QApplication)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = Settings()
    window = ClassSchedulerAppGUI(settings)
    window.show()
    sys.exit(app.exec_())
