# QMidiDevice
Abstract MIDI device for QT/PySide

https://github.com/NikolayRag/QMidiDevice

`QMidiDevice` is a QObject that is bound to specific named hardware or virtual MIDI device, handling connection, automatic reconnection, failure handling, listening to incoming data and sending outgoing data.

`QMidiDevice` instances are created with `QMidiDeviceMonitor.maintain(time)` singletone call.

Only one `QMidiDevice` per device exists at a moment, maintained by QMidiDeviceMonitor. Both input and output ports for same device are bound within one `QMidiDevice`.

Each device with unique name get it's own `QMidiDevice` wrapper, being valid till app exit, even while device is unplugged physically. Device disconnections, reconnections and errors are handled by emitting `QMidiDevice`'s specific signals.



##QMidiDeviceMonitor

Singletone class, used to handle actual MIDI devices pool.

Start `QMidiDevice` flow by calling `QMidiDeviceMonitor.maintain(time)`, which will scan available MIDI devices repeatedly, with `time` cycle length in seconds. Providing `0` (default) will run maintainance proccess once and stop running cycle if any.

Static `QMidiDeviceMonitor.sigScanned(list)` signal will be emitted at each cycle, providing complete `QMidiDevice` list collected so far. This list holds all MIDI devices been found at any cycle. 

`QMidiDevice` list can be retreieved by `QMidiDeviceMonitor.midiList(bool)` call. While omitting argument will return complete list of devices, even disconnected, providing True or False will return only plugged devices with Output and Input ports respectively.

In addition to `sigScanned`, `sigAdded(object, bool)` and `sigMissing(object, bool)` are emitted when device is plugged and unplugged, boolean `True` standing for Output, and `False` for Input.

`sigCrit(object, bool)` emitted when device suddenly realised disconnected while being operated (bool = `False`), or reconnects back (bool = `True`)


*!
There's confusing issue, that prevent `QMidiDevice.sigFail()` pass to `QMidiDeviceMonitor.sigCrit(object,False)`, while being intercepted directly. It's going to be some scope or CG issue for sure, any help is welcome.*



## Plugging and connecting




## Data sending and receiving

All data sent to `QMidiDevice` handled regardless+ to plugged state and is buffered if set.
Data sent to actual device can be filtered by transform hooks+ which can be table+ definitions at default case.

Received data is nonblocked, firing signals and also filtered+ back.


---


`QMidiDevice` rely on `rtmidi`  
https://pypi.org/project/python-rtmidi/

