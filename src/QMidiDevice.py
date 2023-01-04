from PySide2.QtCore import *

import logging
logging.getLogger().setLevel(logging.WARNING)


# https://pypi.org/project/python-rtmidi/
# https://github.com/SpotlightKid/python-rtmidi
import rtmidi



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



# =todo 13 (check) +0: perform actual plugged check
	'''
	Check if ports are plugged atm.
	'''
	def _portsPlugged(self):
		return True


	'''
	Device Out ports count
	'''
	def pluggedOut(self):
		if not len(self.portsOut):
			return

		if not self._portsPlugged():
			return

		return len(self.portsOut)


# =todo 17 (connect) +0: maintain last connected state after replug
	'''
	Device In ports count
	'''
	def pluggedIn(self):
		if not len(self.portsIn):
			return

		if not self._portsPlugged():
			return

		return len(self.portsIn)


	'''
	_plugOut, _plugOut

	Called when corresponding device is plugged or unplugged as visible to rtmidi.
	'''
	def _plugOut(self, _state=False):
		newPort = [rtmidi.MidiOut()] if _state else []
		self.portsOut = newPort

		self.sigPlugged.emit(True, _state)


	def _plugIn(self, _state=False):
		newPort = [rtmidi.MidiIn()] if _state else []
		self.portsIn = newPort

		self.sigPlugged.emit(False, _state)



	def isConnectedOut(self):
		return self.portsOut and self.portsOut[0].is_port_open()


	def isConnectedIn(self):
		return self.portsIn and self.portsIn[0].is_port_open()



	'''
	Connect present ports using device name
	'''
	def _connect(self, _out=True):
		def _listen(_data,_):
			self.sigRecieved.emit(_data[0])


		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return


		for cPort in range(portTest[0].get_port_count()):
			portName = portTest[0].get_port_name(cPort)
			if self.getName() == ' '.join(portName.split(' ')[:-1]):

				try:
					portTest[0].open_port(cPort)
					if not _out:
						portTest[0].set_callback(_listen)

				except Exception as x:
					return


				self.sigConnected.emit(_out, True)
				return True



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



	def _disconnect(self, _out):
		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return

		try:
			portTest.cloase_port()
		except:
			None


		self.sigConnected.emit(_out, False)



	def disconnectOut(self):
		self._disconnect(True)


	def disconnectIn(self):
		self._disconnect(False)



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
