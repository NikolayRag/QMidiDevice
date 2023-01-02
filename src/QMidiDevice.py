from PySide2.QtCore import *
from threading import *
from time import *
import logging
logging.getLogger().setLevel(logging.WARNING)


# https://pypi.org/project/python-rtmidi/
# https://github.com/SpotlightKid/python-rtmidi
import rtmidi



'''
Dummy class for maintain static QMidiDevice signals
'''
class QMidiDeviceSignal(QObject):
	sigScanned = Signal(list) #all devices
	sigAdded = Signal(object, bool) #added outputs (True) or inputs (False)
	sigMissing = Signal(object, bool) #missing outputs (True) or inputs (False)


	def __init__(self):
		QObject.__init__(self)



#MIDI device pool maintainer singletone
class QMidiDeviceMonitor(QObject):
	SignalAlias = QMidiDeviceSignal()

	sigScanned = SignalAlias.sigScanned
	sigAdded = SignalAlias.sigAdded
	sigMissing = SignalAlias.sigMissing


	#dummy port listeners
	observerIn = rtmidi.MidiIn()
	observerOut = rtmidi.MidiOut()

	DevicePool = []


	maintainPulse = 0



#  todo 11 (plug, features) +0: allow similar names
#  todo 10 (plug, features) +0: make case for replugging several devices with one name
# rename ports to be sequental for each unique name
# "dev1 0", "devA 1", "dev1 2", "devA 3" ->
# "dev1", "devA", "dev1 (2)", "devA (2)"

#  todo 12 (features) +0: allow device to have multiple In's and Out's


	'''
	Issue: only first device with same names counts.


	Rescan plugged MIDI devices.

	Flow:

	* Iterate In,Out ports
		* Search QMidiDevice by device name
			* Create if new name
		* Unplug missing
	'''
# =todo 14 (scan) +0: Rescan unnamed device list
	def _rescan():
		def devSearch(_name):
			for cDev in QMidiDeviceMonitor.DevicePool:
				if cDev.getName()==_name:
					return cDev


		def devSigTransit (_dev):
			_dev.sigPlugged.connect(lambda _out, _state:
				(QMidiDeviceMonitor.sigAdded if _state else QMidiDeviceMonitor.sigMissing).emit(_dev, _out)
			)


		#In/Out ports for same device are independent of each other,
		# only collected within one device.
		logging.info("\n--- rescan")
		for obsObj, portIsOut in ((QMidiDeviceMonitor.observerOut, True), (QMidiDeviceMonitor.observerIn, False)):
			devsMissing = QMidiDeviceMonitor.midiList(portIsOut) #to be shrinked
			logging.info(f"{'out' if portIsOut else 'in'} with {[d.getName() for d in devsMissing]}")
			for cPort in range(obsObj.get_port_count()):
				cPortName = obsObj.get_port_name(cPort)
				devName = ' '.join(cPortName.split(' ')[:-1])

				cDevice = devSearch(devName)
				logging.info(f"\t\tfound: {cPortName}: {cDevice}")

				#create new device
				if not cDevice:
					cDevice = QMidiDevice(devName)
					devSigTransit(cDevice)

					QMidiDeviceMonitor.DevicePool += [cDevice]


				pluggedFn = cDevice.pluggedOut if portIsOut else cDevice.pluggedIn
				plugFn = cDevice._plugOut if portIsOut else cDevice._plugIn
				if not pluggedFn():
					plugFn(True)

				if cDevice in devsMissing:
					devsMissing.remove(cDevice)


			#accidentally missing
			logging.info(f"\tmiss:{devsMissing}")
			for cDev in devsMissing:
				plugFn = cDev._plugOut if portIsOut else cDev._plugIn
				plugFn(False)


		outList = QMidiDeviceMonitor.midiList()
		QMidiDeviceMonitor.sigScanned.emit(outList)

		return outList



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


		_pulse
			default None: rescan instantly, returning dict as with .midiList()
			int seconds: start recurring rescan every _pulse seconds.
	'''
# -todo 15 (issue) +0: prevent multi-start
	def maintain(_pulse=None):
		def _cycleThread():
			while QMidiDeviceMonitor.maintainPulse:
				QMidiDeviceMonitor._rescan()

				sleep(QMidiDeviceMonitor.maintainPulse)


		if not _pulse:
			QMidiDeviceMonitor.maintainPulse = 0 #cancel cycle

			return QMidiDeviceMonitor._rescan()


		if not QMidiDeviceMonitor.maintainPulse:
			QMidiDeviceMonitor.maintainPulse = _pulse
			Thread(target=_cycleThread, daemon=True).start()

		QMidiDeviceMonitor.maintainPulse = _pulse





'''
QMidiDevice is Rtmidi device wrapper.

QMidiDevice is bound to MIDI device's input and output using device name.
One device can have one input and one output. (subj to change)

QMidiDevice instances are created once, reused while reconnection or rescanning.
It is safe, and is proper use, not to release QMidiDevice in user app ever, if no need.

'''
class QMidiDevice(QObject):
	MidiCC = 0xB0


	sigRecieved = Signal(list) #[data]
	sigPlugged = Signal(bool, bool) #isOutput, state
	sigConnected = Signal(bool, bool) #isOutput, state
	sigFail = Signal(bool) #error at sending data, isOutput flag
	sigMissing = Signal(bool) #error at connecting, isOutput flag


	#name and in/out are remain unchanged and defines device at QMidiDevice.maintain()
	midiName = '' #original device name


	#[port,..]
	portsOut = None
	portsIn = None



	def _plugOut(self, _state=False):
		newPort = [rtmidi.MidiOut()] if _state else []
		self.portsOut = newPort

		self.sigPlugged.emit(True, _state)



	def _plugIn(self, _state=False):
		newPort = [rtmidi.MidiIn()] if _state else []
		self.portsIn = newPort

		self.sigPlugged.emit(False, _state)



# =todo 13 (check) +0: perform actual plugged check
	'''
	Check if ports are plugged atm.
	'''
	def _portsPlugged(self):
		return True



	def _listen(self,_data,_):
		self.sigRecieved.emit(_data[0])



	'''
	Connect present ports using device name
	'''
	def _connect(self, _out=True):
		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return


		for cPort in range(portTest[0].get_port_count()):
			portName = portTest[0].get_port_name(cPort)
			if self.getName() == ' '.join(portName.split(' ')[:-1]):

				try:
					portTest[0].open_port(cPort)
					if not _out:
						portTest[0].set_callback(self._listen)

				except Exception as x:
					return


				self.sigConnected.emit(_out, True)
				return True



### - private


	'''
	rtmidi wrapper.

	QMidiDevice lifetime:

	* created by static QMidiDevice._rescan()
	* once created, actual for app lifetime
	* connected automatically at use, or .connect() manually
	* disconnects on errors, not-found state at QMidiDevice._rescan() or manually

	_name
		unique device reference name, originally scanned vendor device name
	'''


	def __init__(self, _name):
		QObject.__init__(self)

		self.midiName = _name

		self.portsOut = []
		self.portsIn = []



	def getName(self):
		return self.midiName



	'''
	Device Out ports count
	'''
	def pluggedOut(self):
		if not self._portsPlugged():
			return

		return len(self.portsOut)


# =todo 17 (connect) +0: maintain last plugged state
	'''
	Device In ports count
	'''
	def pluggedIn(self):
		if not self._portsPlugged():
			return

		return len(self.portsIn)



	def isConnectedOut(self):
		return self.portsOut and self.portsOut[0].is_port_open()



	def isConnectedIn(self):
		return self.portsIn and self.portsIn[0].is_port_open()



	def connectOut(self):
		if not self.pluggedOut():
			return
		if self.isConnectedOut():
			return True

		return self._connect(True)



	def connectIn(self):
		if not self.pluggedIn():
			return

		if self.isConnectedIn():
			return True

		return self._connect(False)



	def disconnectOut(self):
		self._disconnect(True)



	def disconnectIn(self):
		self._disconnect(False)



	def _disconnect(self, _out):
		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return

		try:
			portTest.cloase_port()
		except:
			None


		self.sigConnected.emit(_out, False)



	def send(self, _ctrl, _val, channel=0, cmd=MidiCC):
		if channel>16 or channel<0:
			return

		if not self.connectOut():
			return


		try:
			self.portsOut[0].send_message([cmd+channel, _ctrl, _val])
		except Exception as x:
			self.disconnectOut()

			self.sigFail.emit(True)
