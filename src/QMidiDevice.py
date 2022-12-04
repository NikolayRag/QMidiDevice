from PySide2.QtCore import *
from threading import *


import pygame.midi #   https://www.pygame.org/docs/   https://github.com/pygame/pygame



class QMidiDevice(QObject):

	def __init__(self):
		QObject.__init__(self)

		pygame.midi.init()

