#Pyside demo case

if __name__ != "__main__":
    exit()



from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *



from QMidiDevice import *




class QMDDemo():
    cMidi = None


    def __init__(self):
        #Window setup

        theApp = QApplication()
        theWindow = QMainWindow()
        theWindow.setCentralWidget(QWidget())
        layMain = QVBoxLayout(theWindow.centralWidget())

        layMain.addWidget(QLabel('Midi Devices available'))

        self.wListDevices = QListWidget()
        layMain.addWidget(self.wListDevices)


        #QMidiDevice setup

        self.cMidi = QMidiDevice()


        #App run

        theWindow.show()
        theApp.exec_()

QMDDemo()
