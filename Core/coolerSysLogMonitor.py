import localvars
localvars.load_globals(localvars,globals())
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logger
from Core.fileUtilities import load_latest_coolersyslog_file

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

class coolerSysLogManager(QObject):
    coolerSysLogLines = pyqtSignal(list)
    def __init__(self, coolersyslog_path = None):
        super().__init__()
        self.coolersyslog_path = coolersyslog_path
        self.watchdog = coolerSysLogFileWatchdog()
        self.watchdog.coolerSysChangeSignal.connect(self.changeCallback)
        self.observer = Observer()
        self.fds = {}
        self.positions = {}
        self._isRunning = False

    def getLatestLogLines(self, max_lines=localvars.COOLERSYSLOG_MAX_LINES_IN_READER):
        def tail(handle, max_lines, block_size=1024):
            handle.seek(0,2) # Go to end of file
            eof = handle.tell()
            block_end_byte, block_number, blocks, lines = handle.tell(), 1, [], max_lines

            while lines >= 0 and block_end_byte > 0: # WHile there is still lines and files to read
                if (block_end_byte - block_size > 0):  # Read full block
                    handle.seek(eof - block_number*block_size)
                    blocks.append(handle.read(block_size))
                else:  # File too small, just read from beginning
                    handle.seek(0)
                    blocks.append(handle.read(block_end_byte))
                lines -= blocks[-1].count('\n')
                block_end_byte -= block_size
                block_number += 1
            all_read = ''.join(reversed(blocks))
            return all_read.splitlines(True)[-max_lines:]  # Keep the newlines

        if self.coolersyslog_path and self.coolersyslog_path != '':
            latest_file = load_latest_coolersyslog_file(self.coolersyslog_path)

            if latest_file in self.fds and localvars.KEEP_LOGFILES_OPEN:
                fd = self.fds[latest_file]
                latest_lines = tail(fd, max_lines)
                fd.seek(self.positions[latest_file])
            else:
                with open(os.path.join(self.coolersyslog_path, latest_file), 'r') as fd:
                    latest_lines = tail(fd, max_lines)
            return latest_lines
        else:
            return []


    def changeCallback(self, change, fname):
        if self.coolersyslog_path is None:
            return

        if change == 'created':
            if localvars.KEEP_LOGFILES_OPEN:
                self.fds[fname] = open(os.path.join(self.coolersyslog_path, fname), 'r')
            self.positions[fname] = 0
        elif change == 'modified':
            if fname not in self.positions:
                self.positions[fname] = 0

            if localvars.KEEP_LOGFILES_OPEN:
                if fname not in self.fds:
                    self.fds[fname] = open(os.path.join(self.coolersyslog_path, fname), 'r')
            else:
                self.fds[fname] = open(os.path.join(self.coolersyslog_path, fname), 'r')
                self.fds[fname].seek(self.positions[fname])

            lines = self.fds[fname].readlines()
            self.positions[fname] = self.fds[fname].tell()
            if len(lines) > 0:
                self.coolerSysLogLines.emit(lines)

            if not localvars.KEEP_LOGFILES_OPEN:
                fd = self.fds.pop(fname)
                fd.close()
            #for line in self.fds[fname].readlines():
            #    self.coolerSysLogLine.emit(line)


    def startObserver(self):
        self._isRunning = True
        if self.coolersyslog_path is not None:
            self.schedule = self.observer.schedule(self.watchdog, self.coolersyslog_path, recursive=False)
        self.observer.start()

    def changePath(self, new_path):
        self.coolersyslog_path = new_path
        if self._isRunning:
            self.observer.unschedule_all()
            self.schedule = self.observer.schedule(self.watchdog, self.coolersyslog_path, recursive=False)

    def stopObserver(self):
        if self._isRunning:
            self.observer.stop()
            self.observer.join()
            self._isRunning = False

    def __del__(self):
        for _, fd in self.fds.items():
            if fd: fd.close()