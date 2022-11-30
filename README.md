# QMidiDevice
Abstract MIDI device for QT/PySide

https://github.com/NikolayRag/QMidiDevice

QMidiDevice handles nonblocking connection to device with automatic reconnection, sending and receiving complex data using device definition, and failure handling.



## Asynchronous QMidiDevice

QMidiDevice* is a nonblocking QObject* which can be bound to QT workflow by ordinary signal-slot* technique.



## Connection and reconnection

QMidiDevice is bound to [interface/]name* and its connection is done in background*, firing plugged/unplugged signals*.



## Data definition and flow

All data sent to QMidiDevice handled regardless* to plugged state and is buffered if set.
Data sent to actual device can be filtered by transform hooks* which can be table* definitions at default case.

Received data is nonblocked*, firing signals* and also filtered* back.


---

#### QMidiDevice rely on pygame.midi
https://github.com/pygame/pygame
