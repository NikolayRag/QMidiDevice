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

=check 13: +0 "src\QMidiDevice.py" Ki 22/12/29 13:44:39
	perform actual plugged check

=scan 14: +0 "src\QMidiDevice.py" Ki 22/12/30 02:39:16
	Rescan unnamed device list

-issue 15: +0 "src\QMidiDevice.py" Ki 23/01/02 03:54:09
	prevent multi-start

!demo 16: +0 "src\__main__.py" Ki 23/01/02 06:29:34
	dont reset 

=connect 17: +0 "src\QMidiDevice.py" Ki 23/01/02 17:07:41
	maintain last connected state after replug

