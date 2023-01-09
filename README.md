# QMidiDevice
MIDI device interface for `PySide`

https://github.com/NikolayRag/QMidiDevice

`QMidiDevice` is bound to specific hardware or virtual MIDI device. It handle  connection, failure handling, automatic reconnection, listening to incoming data and sending outgoing data.

Both input and output ports for same device are bound within one `QMidiDevice`.  
Only one `QMidiDevice` per device exists at a time, maintained by QMidiDeviceMonitor. 

`QMidiDevice` instances are created and managed by `QMidiDeviceMonitor` singletone.  
Start with `QMidiDeviceMonitor.maintain(seconds)` static call, which will monitor available devices repeatedly every `seconds`.

Each device with unique name get it's own `QMidiDevice` wrapper, being valid till app exit, even while device is unplugged physically. Device disconnections, reconnections and errors are handled by emitting `QMidiDevice`'s specific signals.



### Plugging and connecting

`QMidiDevice` fires .sigPlugged(isOut, state) signal as device plugged state is changed.  
This can happen at `QMidiDeviceMonitor` maintainance, or by catching device error (state=False for unplugged).

`QMidiDevice` been unplugged by accident will reconnect when plugged back. `sigRestore(isOut, success)` emitted in this case.



### Data sending and receiving

Send raw data with `.send(list)` with bytes `list`.  
Control changes can be built and sent with '.cc()'.  

All data sent to `QMidiDevice` handled regardless to plugged state.

`sigRecieved(list)` signals emitted when data is received.  
Control Change input events are detected, emitting `sigCC()` event.


##QMidiDeviceMonitor

Singletone class, used to handle `QMidiDevice` pool.

`QMidiDeviceMonitor.maintain(seconds=0)` repeatedly scan available MIDI devices, with `seconds` cycle frequency. Providing `0` (default) will scan once and stop running cycle if any.

Static `QMidiDeviceMonitor.sigScanned(list)` signal will be emitted at each cycle, providing complete `QMidiDevice` list collected so far. This list holds all MIDI devices been found since first cycle, also with  currently disconnected ones.

`QMidiDevice` for non-yet-plugged device created with `QMidiDeviceMonitor.demand(name)`.

Last known `QMidiDevice` list can be retreieved by `QMidiDeviceMonitor.midiList(bool)` call. While omitting argument will return complete list of devices, providing True or False will return only plugged devices with Output and Input ports respectively.

`sigAdded(object, bool)` and `sigMissing(object, bool)` are emitted when device is plugged and unplugged, boolean `True` standing for Output, and `False` for Input.

`sigCrit(object, bool)` emitted when device suddenly realised disconnected while being operated with `False`, or reconnects back for `True`.

*!
There's confusing issue, that prevents `QMidiDevice.sigFail()` pass to `QMidiDeviceMonitor.sigCrit(object,False)`, while being intercepted directly. It's going to be some scope or CG issue for sure, any help is welcome.*

---


`QMidiDevice` rely on `rtmidi`  
https://pypi.org/project/python-rtmidi/


MIDI breef summary
https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message
