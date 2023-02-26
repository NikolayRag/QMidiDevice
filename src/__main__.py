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
        iSelIn = self.wListMidiIns.currentRow()
        if iSelIn==-1: iSelIn = 0
        self.wListMidiIns.clear()

        iSelOut = self.wListMidiOuts.currentRow()
        if iSelOut==-1: iSelOut = 0
        self.wListMidiOuts.clear()


        cItem = QListWidgetItem('---')
        cItem.setData(Qt.UserRole, None)
        self.wListMidiIns.addItem(cItem)

        cItem = QListWidgetItem('---')
        cItem.setData(Qt.UserRole, None)
        self.wListMidiOuts.addItem(cItem)


        for cDev in _devices:
            if cDev.pluggedIn():
                cItem = QListWidgetItem(cDev.getName())
                cItem.setData(Qt.UserRole, cDev)
                self.wListMidiIns.addItem(cItem)


            if cDev.pluggedOut():
                cItem = QListWidgetItem(cDev.getName())
                cItem.setData(Qt.UserRole, cDev)
                self.wListMidiOuts.addItem(cItem)


        self.wListMidiIns.setCurrentRow(iSelIn)
        self.wListMidiOuts.setCurrentRow(iSelOut)




    def midiSetFrom(self):
        cItem = self.wListMidiIns.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev==self.midiTo:
            return

        if self.midiFrom:
            self.midiFrom.sigRecieved.disconnect()
            self.midiFrom.disconnectIn()

        if midiDev:
            midiDev.sigCC.connect(self.midiProccess)
            midiDev.connectIn()

        self.midiFrom = midiDev



    def midiSetTo(self):
        cItem = self.wListMidiIns.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev==self.midiTo:
            return

        if self.midiTo:
            self.midiFrom.sigFail.disconnect()
            self.midiTo.disconnectIn()

        if midiDev:
            midiDev.sigFail.connect(lambda _:print(f"!! fail: {midiDev.getName()}"))
            midiDev.connectOut()
        
        self.midiTo = midiDev







    def midiProccess(self, _ctrl, _val, _chan):
#        print(f" midi {_chan} {_ctrl}: {_val}\t\t", end='\r')

        if _ctrl==32 and _val==127:
            tick = 1
            tOut = time() +1
            while time() < tOut:
                self.midiTo and self.midiTo.cc(0, int(127*tick/10000)%127, send=True)
                tick +=1

            print(f"\n{tick} ticks/sec, {int(tick/127)} cycles")


        self.midiTo and self.midiTo.cc(_ctrl, _val, send=True)




    def __init__(self):
        #Window setup

        theApp = QApplication()
        theApp.setApplicationName('QMidiDevice test')
        theWindow = QMainWindow()
        theWindow.resize(QSize(400,200))
        theWindow.setCentralWidget(QWidget())
        layMain = QVBoxLayout(theWindow.centralWidget())


        layDevs = QHBoxLayout()
        layMain.addLayout(layDevs)

        #devs ui
        layDevIn = QVBoxLayout()
        layDevs.addLayout(layDevIn)

        layDevIn.addWidget(QLabel('Midi In'))
        self.wListMidiIns = QListWidget()
        layDevIn.addWidget(self.wListMidiIns)


        layDevOut = QVBoxLayout()
        layDevs.addLayout(layDevOut)

        layDevOut.addWidget(QLabel('Midi Out'))
        self.wListMidiOuts = QListWidget()
        layDevOut.addWidget(self.wListMidiOuts)


        self.wListMidiIns.currentItemChanged.connect(self.midiSetFrom)
        self.wListMidiOuts.currentItemChanged.connect(self.midiSetTo)



        #QMidiDevice setup

        QMidiDeviceMonitor.sigScanned.connect(self.midiCollect)
        QMidiDeviceMonitor.sigAdded.connect(lambda _dev, _out: print(f" + {'out' if _out else 'in'} {_dev.getName()}"))
        QMidiDeviceMonitor.sigMissing.connect(lambda _dev, _out: print(f" - {'out' if _out else 'in'} {_dev.getName()}"))
        QMidiDeviceMonitor.sigCrit.connect(lambda _dev, _state: print(f" ! {'restore' if _state else 'fail'}: {_dev.getName()}"))

        QMidiDeviceMonitor.maintain(1)


        #App run

        theWindow.show()
        theApp.exec_()



QMDDemo()
