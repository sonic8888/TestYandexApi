import sys
from PySide6 import QtWidgets
from MainWindow import Ui_MainWindow
from qt_material import apply_stylesheet


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    window.show()
    app.exec()


if __name__ == '__main__':
    main()


