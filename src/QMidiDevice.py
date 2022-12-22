from PySide2.QtCore import *
from threading import *


import pygame.midi #   https://www.pygame.org/docs/   https://github.com/pygame/pygame



# =todo 7 (ux, api) +0: join Input and Output into one QMidiDevice

'''
QMidiDevice is Pygame.midi device wrapper.

QMidiDevice is bound to Input and/or Output midi device using midi device name.

QMidiDevice instances are created once, reused while reconnection or rescanning.
It is safe, and is proper use, not to release QMidiDevice in user app ever, if no need.

'''
class QMidiDevice(QObject):
	MidiCC = 0xB0


	DevicePool = {} #static {name:QMidiDevice,..}


	'''
	Static QMidiDevice.rescan()
	Rescan plugged MIDI devices and bind found ID's. This will make any used
	device outdated untill reconnected, as .quit() is neccessary for updating
	pygame.midi device list by it's design.
	
#	Auto-reconnection will be forced immediately, but devices may react
#	at reconnection in specific way like lagging.

	return: {name:QMidiDevice,..} dict
		Devices list is static QMidiDevice dict, referenced by name.
		QMidiDevice added to this list at first time will be reused in
		 subsequent and will remain till app end,even when completely unplugged.
		Replugged device will reuse corresponding QMidiDevice, so QMidiDevice
		 instance is safe for being lock-assigned by app.
	'''

	def rescan():
#  todo 5 (decide, lowlevel) +0: reuse pygame.midi.Output/Input device
		'''
		todo: investigate reuse of (pypm.Output)pygame.midi.Output(id)._output
		and (pypm.Input)pygame.midi.Input(id)._input objects after pygame.midi.rescan()
		This probably can eliminate interrupt of Input/Output useage due to non-reconnection.
		!Highly rely on portmidi!

		Trace:
		https://github.com/pygame/pygame/blob/main/src_py/midi.py
		https://github.com/pygame/pygame/blob/main/src_c/pypm.c
		https://github.com/PortMidi/portmidi/blob/master/pm_common/portmidi.c
		'''


		#mark all unplugged
		for cDevice in QMidiDevice.DevicePool.values():
			cDevice._plug() #reset id before sigConnectedState emit
			cDevice.disconnect()


		pygame.midi.quit() #the only way to get actual device list
		pygame.midi.init()


		for mN in range(pygame.midi.get_count()):
			cDevInfo = pygame.midi.get_device_info(mN)
			devName = cDevInfo[1].decode('UTF-8')
			devOut = cDevInfo[3]

			if devName not in QMidiDevice.DevicePool:
				cDevice = QMidiDevice(
					devName
				)

				QMidiDevice.DevicePool[devName] = cDevice

			else: #reuse by (name, inout)
				cDevice = QMidiDevice.DevicePool[devName]


			cDevice._plug(mN, devOut)


		return QMidiDevice.midiList()



	def midiList():
		return dict(QMidiDevice.DevicePool)



	# rescan and reconnect by pulse period, if any
	def maintain(_pulse=0):
		None


#	'''
#	Make duplicate list of all QMidiDevice pool.
#	Returned QMidiDevice can be used to access one midi device in parallel.
#	'''
#	def clone():
#		return dict(QMidiDevice.DevicePool)



#### -STATIC

	sigConnectedState = Signal(bool, bool) #isOutput, stste
	sigFail = Signal(bool) #error at sending data, isOutput flag
	sigMissing = Signal(bool) #error at connecting, isOutput flag


	#name and in/out are remain unchanged and defines device at QMidiDevice.rescan()
	pymidiName = '' #original device name

	pymidiIdIn = -1 #pymidi input device id if any
	pymidiDeviceIn = None #assigned pymidi Input device instance
	pymidiIdOut = -1 #output id
	pymidiDeviceOut = None #Output device
	


	def _plug(self, _id=-1, _out=None):
		if _out==None or _out==True:
			self.pymidiIdOut = _id

		if _out==None or _out==False:
			self.pymidiIdIn = _id



### - private


	'''
	pygame.midi wrapper.
	pygame.midi device is going to be in connected state,
	 as connection dont poke or block actual MIDI device,
	 according to current pymidi implementation(?).


	QMidiDevice lifetime:

	* created by static QMidiDevice.rescan()
	* once created, actual for app lifetime
	* connected automatically at use, or .connect() manually
	* disconnects on errors, not-found state at QMidiDevice.rescan() ot manually

	_name
		unique device reference name, originally scanned vendor device name
	'''
	def __init__(self, _name):
		QObject.__init__(self)

		self.pymidiName = _name



	#visible by pygame.midi last time
	def isPlugged(self, _out=True):
		if _out:
			return (self.pymidiIdOut >= 0)
		else:
			return (self.pymidiIdIn >= 0)



	def isConnected(self, _out=True):
		if _out:
			return True if self.pymidiDeviceOut else self.pymidiDeviceOut
		else:
			return True if self.pymidiDeviceIn else self.pymidiDeviceIn



	def getName(self):
		return self.pymidiName



	def connect(self, _out=True):
		if self.isConnected(_out):
			return True


		if not self.isPlugged(_out):
			self.sigMissing.emit(_out)
			return


		try:
			if _out:
				self.pymidiDeviceOut = pygame.midi.Output(self.pymidiIdOut)
			else:
				self.pymidiDeviceIn = pygame.midi.Input(self.pymidiIdIn)

		except:
			self.disconnect(_out)
			return


		self.sigConnectedState.emit(_out, True)
		return True



	def disconnect(self, _out=None):
		try:
			if _out==None or _out==True:
				self.pymidiDeviceOut and self.pymidiDeviceOut.close()
				self.pymidiDeviceOut = None

			if _out==None or _out==False:
				self.pymidiDeviceIn and self.pymidiDeviceIn.close()
				self.pymidiDeviceIn = None
		except:
			None


		self.sigConnectedState.emit(_out, False)



	def send(self, _ctrl, _val, channel=0, cmd=MidiCC):
		if channel>16 or channel<0:
			return
		if not self.isPlugged(True):
			return


		if not self.connect(True):
			return


		try:
			self.pymidiDeviceOut.write_short(cmd+channel, _ctrl, _val)
		except Exception as x:
			self.disconnect(True)

			self.sigFail.emit(True)
