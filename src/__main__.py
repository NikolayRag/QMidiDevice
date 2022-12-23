#Pyside demo case

if __name__ != "__main__":
    exit()



from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from threading import *
import random


from QMidiDevice import *




class QMDDemo():
    cMidi = None



    #show MIDI devices
    def midiCollect(self,  _devices):

        self.wListDevices.clear()

        for cDev in _devices.values():
            devName = f"{'in' if cDev.isPlugged(False) else '--'} {'out' if cDev.isPlugged(True) else '--'}: {cDev.getName()}"
            cItem = QListWidgetItem(devName)
            cItem.setData(Qt.UserRole, cDev)

            self.wListDevices.addItem(cItem)



    def midiListen(self):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev:
            midiDev.sigRecieved.connect(lambda v,s: self.midiPoke(v[1], v[2]))
            midiDev.connectPort(False)



    def midiPoke(self, _ctrl, _val):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev:
            midiDev.send(_ctrl, _val)



    def __init__(self):
        #Window setup

        theApp = QApplication()
        theApp.setApplicationName('QMidiDevice test')
        theWindow = QMainWindow()
        theWindow.resize(QSize(400,200))
        theWindow.setCentralWidget(QWidget())
        layMain = QVBoxLayout(theWindow.centralWidget())


        layMain.addWidget(QLabel('Midi Devices available'))

        self.wListDevices = QListWidget()
        layMain.addWidget(self.wListDevices)

        wBtnMidiScan = QPushButton('Scan devices')
        layMain.addWidget(wBtnMidiScan)


        wBtnMidiGet = QPushButton('Listen')
        layMain.addWidget(wBtnMidiGet)
        wBtnMidiNext = QPushButton('Send')
        layMain.addWidget(wBtnMidiNext)


        #QMidiDevice setup

        QMidiDevice.sigScanned.connect(self.midiCollect)
        wBtnMidiScan.clicked.connect(QMidiDevice.rescan)
        wBtnMidiGet.clicked.connect(self.midiListen)
        wBtnMidiNext.clicked.connect(self.midiPoke)


        QMidiDevice.rescan()


        #App run

        theWindow.show()
        theApp.exec_()



QMDDemo()
