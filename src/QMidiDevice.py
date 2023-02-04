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


	sigRecieved = Signal(list, int) #[data], stamp
	sigCC = Signal(int, int, int, int) #controller, value, channel, stamp
	sigPlugged = Signal(bool, bool) #isOutput, state
	sigFail = Signal(bool) #error at sending data, isOutput flag
	sigRestore = Signal(bool, bool) #isOutput, success


	#name and in/out are remain unchanged and defines device at QMidiDevice.maintain()
	midiName = '' #original device name


	#[port,..]
	portsOut = None
	portsIn = None

	lastOut = False
	lastIn = False


	offBuffer = []

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

		self.offBuffer = []



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
#		self.sigFail.emit(True) #works, relative to todo18

		if bool(_state) == bool(self.pluggedOut()):
			return

		newPort = [rtmidi.MidiOut()] if _state else []
		self.portsOut = newPort

		if self.lastOut:
			recon = self.connectOut()
			self.sigRestore.emit(True, recon)

		self.sigPlugged.emit(True, _state)


	def _plugIn(self, _state=False):
#		self.sigFail.emit(True) #works, relative to todo18

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
		def _listen(_val, _):
			self.sigRecieved.emit(_val[0], _val[1])

			if (_val[0][0] & 0xF0) == self.MidiCC:
				self.sigCC.emit(_val[0][1], _val[0][2], _val[0][0] & 0x0F, _val[1])



		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return


		for cPort in range(portTest[0].get_port_count()):
			portName = portTest[0].get_port_name(cPort)
			if self.getName() == ' '.join(portName.split(' ')[:-1]):

				try:
					portTest[0].open_port(cPort)
				except Exception as x:
					return

				if not _out:
					portTest[0].set_callback(_listen)


				return True



	def connectOut(self):
#		self.sigFail.emit(False) #dont work, relative to todo18

		if not self.pluggedOut():
			return
		if self.isConnectedOut():
			return True


		self.lastOut = self._connect(True)
		self.send([])

		return self.lastOut


	def connectIn(self):
#		self.sigFail.emit(False) #dont work, relative to todo18

		if not self.pluggedIn():
			return
		if self.isConnectedIn():
			return True

		self.lastIn = self._connect(False)
		return self.lastIn



	def _disconnect(self, _out):
		portTest = self.portsOut if _out else self.portsIn
		if not portTest:
			return

		try:
			portTest[0].close_port()
		except:
			None



	def disconnectOut(self, _manual=True):
		self._disconnect(True)

		if _manual:
			self.lastOut = False


	def disconnectIn(self, _manual=True):
		self._disconnect(False)

		if _manual:
			self.lastIn = False


 
# -todo 19 (feature) +0: support 14bit data sending with two controllers
# -todo 20 (feature) +0: support sending arbitrary data, including sysex
# -todo 21 (feature) +0: support data pattern definition
# -todo 22 (feature) +0: assign data pattern to re-/connected state
# -todo 23 (feature) +0: support input filters
# -todo 24 (feature) +0: buffer sended data in case of currently disconnected state
	def cc(self, _ctrl, _val, channel=0, cmd=MidiCC, send=False, must=False):
		if channel>15:
			channel = 15

		if channel<0:
			channel = 0

		outMsg = [cmd+channel, _ctrl, _val]

		if send:
			if not self.send(outMsg, must):
				return

		return outMsg



'''Send data block to MIDI device

Send raw byte block to MIDI Out port.

Data is not checked for any kind of MIDI standart,
 it can be any sequence of bytes.

Args:
	_msg ([list]): [Byte list]
	must (bool): [Set if _msg should be buffered in case of device reconnect] (default: `False`)

Returns:
	[bool]: [Success flag]
'''
	def send(self, _msg, must=False):
		if must:
			self.offBuffer += [_msg]


		if not self.pluggedOut(quiet=True):
			return
		if not self.isConnectedOut():
			return


		try:
			for cMsg in self.offBuffer[:]:
				self.portsOut[0].send_message(cMsg)

				self.offBuffer.pop(0)


			if not must:
				self.portsOut[0].send_message(_msg)


			return True


		except Exception as x:
			self.disconnectOut(False)

# =todo 18 (issue) +1: signals dont pass to QMidiMonitor (only!) from here somehow
			self.sigFail.emit(True)

			self.pluggedOut() #check
