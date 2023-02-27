#Pyside demo case


'''Cases

* Constant flow (Dev In)->(Dev Out)
    + Filter

* Dump In

* Pattern Out

'''


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
        self.wListMidiIns.blockSignals(True)
        self.wListMidiOuts.blockSignals(True)


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


        self.wListMidiIns.blockSignals(False)
        self.wListMidiOuts.blockSignals(False)



    def midiSetFrom(self):
        cItem = self.wListMidiIns.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev==self.midiFrom:
            return

        if self.midiFrom:
            self.midiFrom.sigReceived.disconnect()
            self.midiFrom.sigCC.disconnect()
            self.midiFrom.disconnectIn()

        if midiDev:
            midiDev.sigReceived.connect(self.midiDump)
            midiDev.sigCC.connect(self.midiProccess)
            midiDev.connectIn()

        self.midiFrom = midiDev



    def midiSetTo(self):
        cItem = self.wListMidiOuts.currentItem()
        if not cItem:
            return

        midiDev = cItem.data(Qt.UserRole)
        if midiDev==self.midiTo:
            return

        if self.midiTo:
            self.midiTo.sigFail.disconnect()
            self.midiTo.disconnectOut()

        if midiDev:
            midiDev.sigFail.connect(lambda _:print(f"!! fail: {midiDev.getName()}"))
            midiDev.connectOut()
        
        self.midiTo = midiDev



    def midiDump(self, _block):
        self.wDump.append(f"{_block}")



    def midiProccess(self, _ctrl, _val, _chan):
        if self.wFilterChan.value()>-1 and self.wFilterChan.value() != _chan:
            return
        if self.wFilterCtrl.value()>-1 and self.wFilterCtrl.value() != _ctrl:
            return

        self.midiTo and self.midiTo.cc(_ctrl, _val)



    def midiPattern(self):
        tick = 1
        tOut = time() +1
        while time() < tOut:
            self.midiTo and self.midiTo.cc(5, int(127*tick/10000)%127)
            tick +=1

        print(f"\n{tick} ticks/sec, {int(tick/127)} cycles")



    def __init__(self):
        #Window setup

        theApp = QApplication()
        theApp.setApplicationName('QMidiDevice test')
        theWindow = QMainWindow()
        theWindow.resize(QSize(700,300))
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


        layDump = QVBoxLayout()
        layDevs.addLayout(layDump)

        layDump.addWidget(QLabel('Dump'))
        self.wDump = QTextEdit()
        self.wDump.setMaximumWidth(150)
        layDump.addWidget(self.wDump)


        layDevOut = QVBoxLayout()
        layDevs.addLayout(layDevOut)

        layDevOut.addWidget(QLabel('Midi Out'))
        self.wListMidiOuts = QListWidget()
        layDevOut.addWidget(self.wListMidiOuts)


        layDevFilter = QHBoxLayout()
        layDevOut.addLayout(layDevFilter)

        layDevFilter.addWidget(QLabel('Channel'))
        self.wFilterChan = QSpinBox()
        self.wFilterChan.setMinimum(-1)
        self.wFilterChan.setMaximum(15)
        self.wFilterChan.setValue(-1)
        layDevFilter.addWidget(self.wFilterChan)

        layDevFilter.addWidget(QLabel('Controller'))
        self.wFilterCtrl = QSpinBox()
        self.wFilterCtrl.setMinimum(-1)
        self.wFilterCtrl.setMaximum(127)
        self.wFilterCtrl.setValue(-1)
        layDevFilter.addWidget(self.wFilterCtrl)

        wSpFilter = QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layDevFilter.addItem(wSpFilter)


        layOutPattern = QHBoxLayout()
        layDevOut.addLayout(layOutPattern)

        layOutPattern.addWidget(QLabel('Patterns'))
        self.wPattern1 = QPushButton('P1')
        layOutPattern.addWidget(self.wPattern1)

        wSpFilter = QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layOutPattern.addItem(wSpFilter)


        self.wListMidiIns.currentRowChanged.connect(self.midiSetFrom)
        self.wListMidiOuts.currentRowChanged.connect(self.midiSetTo)

        self.wPattern1.pressed.connect(self.midiPattern)


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
