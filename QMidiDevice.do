 support, decide 4: +0 "src\QMidiDevice.py" kii 22/12/12 22:35:34
	close DevicePool objects properly

!decide, lowlevel 5: +0 "" Ki 22/12/25 06:46:21
	non relevant to rtmidi

+ux, api 7: +0 "src\QMidiDevice.py" Ki 22/12/23 01:58:01
	join Input and Output into one QMidiDevice

+api 8: +0 "src\QMidiDevice.py" Ki 22/12/28 06:33:05
	move to python-rtmidi

+api 9: +0 "src\QMidiDevice.py" Ki 22/12/28 06:33:19
	make QMidiDeviceSeer singletone maintainer

 plug, features 10: +0 "src\QMidiDevice.py" Ki 22/12/29 03:44:06
	make case for replugging several devices with one name

 plug, features 11: +0 "src\QMidiDevice.py" Ki 22/12/28 14:00:19
	allow similar names

 features 12: +0 "src\QMidiDevice.py" Ki 22/12/29 03:44:48
	allow device to have multiple In's and Out's

+check 13: +0 "src\QMidiDevice.py" Ki 23/01/04 08:12:56
	perform actual plugged check

+scan 14: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/03 04:37:31
	Rescan unnamed device list

-issue 15: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/02 22:43:05
	blank maintain() cause multi-start

!demo 16: +0 "src\__main__.py" Ki 23/01/02 06:29:34
	dont reset 

+connect 17: +0 "src\QMidiDevice.py" Ki 23/01/04 08:56:40
	maintain last connected state after replug

=issue 18: +1 "src\QMidiDevice.py" Ki 23/01/05 04:21:39
	signals dont pass to QMidiMonitor (only!) from here somehow

-feature 19: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:04
	support 14bit data sending with two controllers

-feature 20: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:06
	support sending arbitrary data, including sysex

-feature 21: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:07
	support predefined data pattern

-feature 22: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:08
	assign data pattern to re-/connected state

-feature 23: +0 "src\QMidiDevice.py" Ki 23/01/06 06:34:57
	support input data recognition with provided reaction

-feature 24: +0 "src\QMidiDevice.py" Ki 23/01/06 06:36:13
	buffer sended data in case of currently disconnected state

