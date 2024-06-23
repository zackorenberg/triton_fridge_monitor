import localvars
localvars.load_globals(localvars,globals())
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logger

logging = logger.Logger(__file__)

import time
import os
from PyQt5.QtCore import QThread, pyqtSignal, QObject

COOLERSYSLOG_EXTENSION = ".slg"

class coolerSysLogFileWatchdog(FileSystemEventHandler, QObject):
    coolerSysChangeSignal = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()


    def on_created(self, event):
        fname = event.src_path.split(os.sep)[-1]
        if fname[-len(COOLERSYSLOG_EXTENSION):] == COOLERSYSLOG_EXTENSION:
            self.coolerSysChangeSignal.emit('created', fname)

    def on_modified(self, event):
        fname = event.src_path.split(os.sep)[-1]
        if fname[-len(COOLERSYSLOG_EXTENSION):] == COOLERSYSLOG_EXTENSION:
            self.coolerSysChangeSignal.emit('modified', fname)

    def on_deleted(self, event):
        fname = event.src_path.split(os.sep)[-1]
        if fname[-len(COOLERSYSLOG_EXTENSION):] == COOLERSYSLOG_EXTENSION:
            self.coolerSysChangeSignal.emit('deleted', fname)
