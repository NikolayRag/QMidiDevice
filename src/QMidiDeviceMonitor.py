from PySide2.QtCore import *

from threading import *
from time import *

import logging
logging.getLogger().setLevel(logging.WARNING)


from QMidiDevice import *



'''
Dummy class for maintain static QMidiDevice signals
'''
class QMidiDeviceSignal(QObject):
	sigScanned = Signal(list) #all devices
	sigAdded = Signal(object, bool) #added outputs (True) or inputs (False)
	sigMissing = Signal(object, bool) #missing outputs (True) or inputs (False)

	sigCrit = Signal(object, bool) #failed or reconnected

	def __init__(self):
		QObject.__init__(self)



#MIDI device pool maintainer singletone
class QMidiDeviceMonitor(QObject):
	SignalAlias = QMidiDeviceSignal()

	sigScanned = SignalAlias.sigScanned
	sigAdded = SignalAlias.sigAdded
	sigMissing = SignalAlias.sigMissing
	sigCrit = SignalAlias.sigCrit


	#dummy port listeners
	observerIn = rtmidi.MidiIn()
	observerOut = rtmidi.MidiOut()

	DevicePool = []


	maintainPulse = 0



	def _devSearch(_name):
		for cDev in QMidiDeviceMonitor.DevicePool:
			if cDev.getName()==_name:
				return cDev



	def _devSigTransit(_dev):
		_dev.sigPlugged.connect(lambda _out, _state:
			(QMidiDeviceMonitor.sigAdded if _state else QMidiDeviceMonitor.sigMissing).emit(_dev, _out)
		)

		_dev.sigFail.connect(lambda _out:
			QMidiDeviceMonitor.sigCrit.emit(_dev, False)
		)

		_dev.sigRestore.connect(lambda _out, _state:
			QMidiDeviceMonitor.sigCrit.emit(_dev, True) if _state else None
		)

		_dev.sigTest.connect(lambda v:print('test monitor', v))



#  todo 11 (plug, feature) +0: allow similar names
#  todo 10 (plug, feature) +0: make case for replugging several devices with one name
# rename ports to be sequental for each unique name
# "dev1 0", "devA 1", "dev1 2", "devA 3" ->
# "dev1", "devA", "dev1 (2)", "devA (2)"

#  todo 12 (feature) +0: allow device to have multiple In's and Out's


	'''
	Issue: only first device with same names counts.


	Rescan plugged MIDI devices.

	Flow:

	* Iterate In,Out ports
		* Check all plugged
		* Search QMidiDevice by device name
			* Create if new name
	'''
	def _rescan():



		#In/Out ports for same device are independent of each other,
		# only collected within one device.
		logging.info("\n--- rescan")
		for portIsOut in (True, False):
			#check all's plugged state, unplugging orphan
			for dObj in QMidiDeviceMonitor.DevicePool:
				dObj.pluggedOut() if portIsOut else dObj.pluggedIn()


			for cPortName in QMidiDeviceMonitor.listPorts(portIsOut):
				devName = ' '.join(cPortName.split(' ')[:-1])

				cDevice = QMidiDeviceMonitor._devSearch(devName)
				logging.info(f"\t\tfound: {cPortName}: {cDevice}")

				#create new device
				if not cDevice:
					cDevice = QMidiDevice(devName)
					QMidiDeviceMonitor._devSigTransit(cDevice)

					QMidiDeviceMonitor.DevicePool += [cDevice]


				plugFn = cDevice._plugOut if portIsOut else cDevice._plugIn
				plugFn(True)


		outList = QMidiDeviceMonitor.midiList()
		QMidiDeviceMonitor.sigScanned.emit(outList)

		return outList



	def listPorts(_out):
		return (QMidiDeviceMonitor.observerOut if _out else QMidiDeviceMonitor.observerIn).get_ports()



	'''
	Return copy of device list.

	Devices list is static QMidiDevice dict, referenced by name.
	Replugged device will reuse corresponding QMidiDevice if any, so QMidiDevice
	 instance is safe for being lock-assigned by app.

		return: {name:QMidiDevice,..} dict

		isOut
			True: devices with outputs
			False: devices with inputs
			default None: all devices
	'''
	def midiList(isOut=None):
		if isOut==None:
			return list(QMidiDeviceMonitor.DevicePool)


		return [
			dObj for dObj in QMidiDeviceMonitor.DevicePool if (
				dObj.pluggedOut() if isOut else dObj.pluggedIn()
			)
		]




	'''
	Rescan device list instantly or periodically.

	Rescan results are emited with QT Signals:
		sigScanned(list): all devices
		sigAdded(object, bool): outputs and inputs added from last rescan, accordingly
		sigMissing(object, bool): outputs and inputs missing from last rescan, accordingly
		sigCrit(object, bool): device fail or reconnected


		seconds
			default 0: rescan instantly, returning dict as with .midiList()
			int seconds: start recurring rescan every seconds seconds.
	'''
# -todo 15 (issue) +0: blank maintain() cause multi-start
	def maintain(seconds=0):
		def _cycleThread():
			while QMidiDeviceMonitor.maintainPulse:
				QMidiDeviceMonitor._rescan()

				sleep(QMidiDeviceMonitor.maintainPulse)


		if not seconds:
			QMidiDeviceMonitor.maintainPulse = 0 #cancel cycle

			return QMidiDeviceMonitor._rescan()


		if not QMidiDeviceMonitor.maintainPulse:
			QMidiDeviceMonitor.maintainPulse = seconds
			Thread(target=_cycleThread, daemon=True).start()

		QMidiDeviceMonitor.maintainPulse = seconds
