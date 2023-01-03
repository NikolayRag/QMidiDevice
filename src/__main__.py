#Pyside demo case

if __name__ != "__main__":
    exit()



from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from time import *


from QMidiDeviceMonitor import *




class QMDDemo():
    midiFrom = None
    midiTo = None



    #show MIDI devices
    def midiCollect(self,  _devices):
        iSelected = self.wListDevices.currentRow()
        self.wListDevices.clear()

        for cDev in _devices:
            devName = f"{'in' if cDev.pluggedIn() else '--'} {'out' if cDev.pluggedOut() else '--'}: {cDev.getName()}"
            cItem = QListWidgetItem(devName)
            cItem.setData(Qt.UserRole, cDev)

            self.wListDevices.addItem(cItem)

        if _devices:
            self.wListDevices.setCurrentRow(iSelected)



    def midiSetFrom(self):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev and midiDev!=self.midiFrom:
            if self.midiFrom:
                self.midiFrom.sigRecieved.disconnect()
                self.midiFrom.disconnectIn()

            midiDev.sigRecieved.connect(self.midiProccess)

        midiDev.connectIn()
        self.midiFrom = midiDev


    
    def midiProccess(self, _midi):
        _cch, _ctrl, _val = _midi
        _cmd = _cch & 0xF0
        _chan = _cch & 0x0F

        print(f" echo {bin(_cmd>>4)} {_chan} {_ctrl}: {_val}\t\t", end='\r')

        if _ctrl==32 and _val==127:
            tick = 1
            tOut = time() +1
            while time() < tOut:
                self.midiTo and self.midiTo.send(0, int(127*tick/10000)%127)
                tick +=1

            print(f"\n{tick} ticks/sec, {tick/127} cycles")


        self.midiTo and self.midiTo.send(_ctrl, _val)



    def midiSetTo(self):
        cItem = self.wListDevices.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev and midiDev!=self.midiTo:
            self.midiTo and self.midiTo.disconnectOut()

        midiDev.connectOut()
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


        wBtnMidiFrom = QPushButton('From')
        layMain.addWidget(wBtnMidiFrom)
        wBtnMidiTo = QPushButton('To')
        layMain.addWidget(wBtnMidiTo)


        #QMidiDevice setup

        QMidiDeviceMonitor.sigScanned.connect(self.midiCollect)
        QMidiDeviceMonitor.sigAdded.connect(lambda _dev, _out: print(f" + {'out' if _out else 'in'} {_dev.getName()}"))
        QMidiDeviceMonitor.sigMissing.connect(lambda _dev, _out: print(f" - {'out' if _out else 'in'} {_dev.getName()}"))
        wBtnMidiFrom.clicked.connect(self.midiSetFrom)
        wBtnMidiTo.clicked.connect(self.midiSetTo)


        QMidiDeviceMonitor.maintain(1)


        #App run

        theWindow.show()
        theApp.exec_()



QMDDemo()
