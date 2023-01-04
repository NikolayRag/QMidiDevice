from PySide2.QtCore import *

import logging
logging.getLogger().setLevel(logging.WARNING)



# https://pypi.org/project/python-rtmidi/
# https://github.com/SpotlightKid/python-rtmidi
import rtmidi

''' !!!
Take in mind that rtmidi identifies ports by sequental naming,
 where sequence id WILL change as devices are disconnected.
!!! '''



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
	sigRestore = Signal(bool, bool) #isOutput, success


	#name and in/out are remain unchanged and defines device at QMidiDevice.maintain()
	midiName = '' #original device name


	#[port,..]
	portsOut = None
	portsIn = None

	lastOut = False
	lastIn = False


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
	Check if ports are plugged atm.

	bool _quiet
		suppress checking if plugged port exists within rtmidi.
	'''
	def _pluggedState(self, _out, _quiet):
		ports = self.portsOut if _out else self.portsIn

		if not len(ports):
			return

		if _quiet:
			return True


		for pName in ports[0].get_ports():
			if self.getName() == ' '.join(pName.split(' ')[:-1]):
				return True

		#cleanup orphan port
		del ports[:]

		self.sigPlugged.emit(_out, False)



	'''
	Device ports marked or actually plugged
	'''
	def pluggedOut(self, quiet=False):
		return self._pluggedState(True, quiet)


	def pluggedIn(self, quiet=False):
		return self._pluggedState(False, quiet)



	'''
	_plugOut, _plugOut

	Called when corresponding device is plugged or unplugged as visible to rtmidi.
	'''
	def _plugOut(self, _state=False):
		if bool(_state) == bool(self.pluggedOut()):
			return

		newPort = [rtmidi.MidiOut()] if _state else []
		self.portsOut = newPort

		if self.lastOut:
			recon = self.connectOut()
			self.sigRestore.emit(True, recon)

		self.sigPlugged.emit(True, _state)


	def _plugIn(self, _state=False):
		if bool(_state) == bool(self.pluggedIn()):
			return

		newPort = [rtmidi.MidiIn()] if _state else []
		self.portsIn = newPort

		if self.lastIn:
			recon = self.connectIn()
			self.sigRestore.emit(False, recon)

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

		self.lastOut = True

		return self._connect(True)


	def connectIn(self):
		if not self.pluggedIn():
			return
		if self.isConnectedIn():
			return True

		self.lastIn = True

		return self._connect(False)



	def _disconnect(self, _out):
		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return

		try:
			portTest.close_port()
		except:
			None


		self.sigConnected.emit(_out, False)



	def disconnectOut(self, _manual=True):
		self._disconnect(True)

		if _manual:
			self.lastOut = False


	def disconnectIn(self, _manual=True):
		self._disconnect(False)

		if _manual:
			self.lastIn = False



	def send(self, _ctrl, _val, channel=0, cmd=MidiCC):
		if channel>16 or channel<0:
			return

		if not self.pluggedOut(test=False):
			return
		if not self.isConnectedOut():
			return


		try:
			self.portsOut and self.portsOut[0].send_message([cmd+channel, _ctrl, _val])
		except Exception as x:
			self.disconnectOut(False)

			self.sigFail.emit(True)

			self.pluggedOut() #check
