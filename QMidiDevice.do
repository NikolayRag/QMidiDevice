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

 plug, feature 10: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/06 08:40:02
	make case for replugging several devices with one name

 plug, feature 11: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/07 21:38:50
	allow similar names

 feature 12: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/06 08:40:10
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

-feature 19: +0 "src\QMidiDevice.py" Ki 23/01/06 07:54:34
	support 14bit data sending with two controllers

-feature 20: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:06
	support sending arbitrary data, including sysex

-feature 21: +0 "src\QMidiDevice.py" Ki 23/01/09 02:29:40
	support data pattern definition

-feature 22: +0 "src\QMidiDevice.py" Ki 23/01/06 06:33:08
	assign data pattern to re-/connected state

-feature 23: +0 "src\QMidiDevice.py" Ki 23/02/04 01:06:03
	support input filters

=feature 24: +0 "src\QMidiDevice.py" Ki 23/02/04 05:10:39
	buffer sended data in case of currently disconnected state

+feature 25: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/07 21:41:10
	make virtual QMidiDevice on demand to be bound later

 feature 26: +0 "src\QMidiDeviceMonitor.py" Ki 23/01/07 23:28:49
	allow renaming

