import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from my_pyqt_basic_ui import Ui_MainWindow

# form_class = uic.loadUiType("d:/inflearn/crawling/section6/example/my_pyqt_basic_3.ui")[0]

class TestForm(QMainWindow, Ui_MainWindow):  # TestForm(QMainWindow, form_class): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestForm()
    window.show()

    app.exec_()
