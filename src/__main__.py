#Pyside demo case

if __name__ != "__main__":
    exit()



from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *



from QMidiDevice import *




class QMDDemo():
    midiFrom = None
    midiTo = None



    #show MIDI devices
    def midiCollect(self,  _devices):
        if self.midiFrom:
            self.midiFrom.sigRecieved.disconnect()
            self.midiFrom.disconnectPort(False)
            self.midiFrom = None
        if self.midiTo:
            self.midiTo.disconnectPort(True)
            self.midiTo = None

        self.wListDevices.clear()

        for cDev in _devices:
            devName = f"{'in' if cDev.pluggedIn() else '--'} {'out' if cDev.pluggedOut() else '--'}: {cDev.getName()}"
            cItem = QListWidgetItem(devName)
            cItem.setData(Qt.UserRole, cDev)

            self.wListDevices.addItem(cItem)



    def midiListen(self):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev and midiDev!=self.midiFrom:
            if self.midiFrom:
                self.midiFrom.sigRecieved.disconnect()
                self.midiFrom.disconnectPort(False)

            midiDev.sigRecieved.connect(lambda v: self.midiPoke(v[1], v[2]))

        midiDev.connectPort(False)
        self.midiFrom = midiDev


    
    def midiPoke(self, _ctrl, _val):
        self.midiTo and self.midiTo.send(_ctrl, _val)



    def midiHold(self):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev and midiDev!=self.midiTo:
            self.midiTo and self.midiTo.disconnectPort(True)

        midiDev.connectPort(True)
        self.midiTo = midiDev



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


        wBtnMidiGet = QPushButton('Listen')
#        layMain.addWidget(wBtnMidiGet)
        wBtnMidiNext = QPushButton('Sink')
#        layMain.addWidget(wBtnMidiNext)


        #QMidiDevice setup

        QMidiDeviceSeer.sigScanned.connect(self.midiCollect)
        QMidiDeviceSeer.sigAdded.connect(lambda _dev, _out: print(f" + {'out' if _out else 'in'} {_dev.getName()}"))
        QMidiDeviceSeer.sigMissing.connect(lambda _dev, _out: print(f" - {'out' if _out else 'in'} {_dev.getName()}"))
        wBtnMidiGet.clicked.connect(self.midiListen)
        wBtnMidiNext.clicked.connect(self.midiHold)


        QMidiDeviceSeer.maintain(1)


        #App run

        theWindow.show()
        theApp.exec_()



QMDDemo()
