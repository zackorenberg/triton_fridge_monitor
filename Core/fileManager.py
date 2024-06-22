"""
Class that deals with log data
"""
import localvars
localvars.load_globals(localvars,globals())

from Core.fileMonitor import *
from Core.fileReader import parse, differential_read

from PyQt5 import QtCore

class LogChannels:
    def __init__(self, fname, log_path=LOG_PATH):
        self.fd = None
        self.fname = fname
        self.tell = 0
        self.creation_time = None
        self.channels = []

        self.titles = None
        self.labels = []
        self.units = []
        self.data = []
        self.last_data = {}
        self.last_time = None

        self.log_path = log_path



    def update_path_information(self, fname):
        self.close()
        self.fd = None
        self.fname = fname
        self.tell = 0

        # Determine date
        self.date = determine_creation_time(fname)

        return self.fname

    def open(self, fname = None):
        if fname:
            self.update_path_information(fname)
        self.close()
        self.fd = open(os.path.join(self.log_path, self.fname), 'rb')


    def update(self):
        if not localvars.KEEP_LOGFILES_OPEN or not self.fd: # We need to open it
            self.open()

        if self.tell > 0: # differential read, lets update
            titles, rawdata = differential_read(self.fd, self.titles, self.tell)
        else:
            titles, rawdata = parse(self.fd)

        self.tell = self.fd.tell()
        self.close()

        # If this was first update we need to write some stuff
        # Lets just right stuff anyways, if anything it'll warn that a new channel exists
        if True or self.titles is None or len(self.titles) < len(titles) or not all([t1==t2 for t1,t2 in zip(self.titles, titles)]):
            self.titles = titles
            self.labels = [s.split('(')[0].strip(' ') if '(' in s else s for s in self.titles[2:]]
            self.units = [s.split('(')[1].strip(' ()') if '(' in s else '' for s in self.titles[2:]]
        ln = rawdata[0] # line number
        ts = rawdata[1]
        data = rawdata[2:].T # Remove the line number and time and transpose it
        data_with_time = {t:dict(zip(self.labels, d)) for t,d in zip(ts, data)}


        if len(ln) > 0:
            self.data += (list(data_with_time.items()))
            if len(self.data) > MAXIMUM_DATAPOINT_HISTORY:
                self.data = self.data[-MAXIMUM_DATAPOINT_HISTORY:]

            last_time = max(ts)
            last_data = data_with_time[last_time]
        else:
            last_time = None
            last_data = None

        if not (last_time is None or last_data is None):
            self.last_time = last_time
            self.last_data = last_data

        if not localvars.KEEP_LOGFILES_OPEN:
            self.close()
        return last_time, last_data

    def close(self):
        if self.fd:
            self.fd.close()
            self.fd = None

    def __del__(self):
        self.close()


class FileManager(QThread):
    processedChanges = QtCore.pyqtSignal(dict)
    allData = QtCore.pyqtSignal(dict)
    def __init__(self, log_path = LOG_PATH):
        super().__init__()
        self.log_path = log_path
        self.overseer = Overseer(log_path)
        self.current_log_file = load_latest_log_file(log_path)
        #self.current_log_file = self.latest_log_files[np.max(self.latest_log_files.keys())]
        self.logChannels = LogChannels(self.current_log_file, log_path=log_path)
        self.__init_logchannel()

        self.overseer.changeSignal.connect(self.changeDetected)

        """
        for channel, date in self.latest_log_files.items():
            #print(channel, date)
            if channel in CHANNEL_BLACKLIST:
                continue
            self.logChannels[channel] = LogChannel(channel, log_path)
            self.logChannels[channel].open(date)
            self.logChannels[channel].update()
            self.logChannels[channel].close()
        """

        self.last_emitted_changes = {}
        self.most_recent_changes = {}

        self.changes_read = {}
        self._isRunning = False

    def __init_logchannel(self):
        try:
            self.logChannels.update()
        except Exception as e:
            # Log file is invalid, will try older ones until one is valid
            for date, fname in sorted(load_all_log_files(self.log_path).items(), key=lambda x:x[0], reverse=True):
                try:
                    self.logChannels.update_path_information(fname)
                    self.logChannels.update()
                    assert (self.logChannels.last_time is not None)
                except Exception as e:
                    logging.debug(f"Error reading {fname}: {str(e)}")
                else:
                    break
        finally:
            if self.logChannels.last_time is None:
                logging.error("No valid log files found")

    def emitData(self):
        self.allData.emit(self.dumpData())

    def dumpData(self):
        # convert list of [(t, {ch:data})] to {ch:(t,d)}
        ret = {}
        for t, values in self.logChannels.data:
            for ch, data in values.items():
                if ch not in ret:
                    ret[ch] = []
                ret[ch].append((t,data))
        return ret

    def run(self):
        self._isRunning = True
        self.overseer.start()
        while self._isRunning:
            time.sleep(1)
            continue
            logging.debug("Looping")
            if len(self.changes_read.keys()) > 0:
                logging.debug("Pending changes emitting")
                self.last_emitted_changes = self.changes_read
                self.changes_read = {}
                self.processedChanges.emit(self.last_emitted_changes)
                self.most_recent_changes.update(self.last_emitted_changes)
            time.sleep(CHANGE_PROCESS_CHECK)

    def stop(self):
        self._isRunning = False
        self.overseer.stop()
        self.overseer.wait()

    def __del__(self):
        self.logChannels.close()

    def changeDetected(self, change, date, fname): # Emit the changes right from here
        logging.debug(f"Change detected {change} {date} {fname}")
        if change == 'deleted':
            self.handleDeletionEvent(date, fname)
            return

        if fname != self.current_log_file or change == 'created':
            self.current_log_file = fname
            self.logChannels.update_path_information(fname)
        try:
            last_time, last_data = self.logChannels.update()
        except Exception as e:
            logging.warning(f"An error encountered while updating log file: {str(e)}. Rereading")
            self.logChannels.update_path_information(self.logChannels.fname)
            try:
                last_time, last_data = self.logChannels.update()
            except Exception as e:
                logging.error(f"Could not read log file! Monitor system may no longer work: {str(e)}")
                print(f"Could not read log file! Monitor system may no longer work: {str(e)}")
                return

        if last_time is None or last_data is None:
            return
        ## Make it into the channel:{time:value} format it needs to be in
        self.last_emitted_changes = self.changes_read = { # This is required for the case where multiple times but we do not consider that for the triton
            ch:{last_time:v}
            for ch,v in last_data.items()
        }
        self.processedChanges.emit(self.last_emitted_changes)
        self.most_recent_changes.update(self.last_emitted_changes)

    def handleDeletionEvent(self, date, fname):
        if fname == self.logChannels.fname:
            logging.warning("Current logfile was deleted, searching for next newest one")
            print("Current logfile was deleted, searching for next newest one")
        self.__init_logchannel()  # Since we are finding an older log channel, we don't need to send an alert
        if localvars.EMIT_ON_LOGFILE_DELETION:
            self.processedChanges.emit({  # This is required for the case where multiple times but we do not consider that for the triton
                ch: {self.logChannels.last_time: v}
                for ch, v in self.logChannels.last_data.items()
            })

    def currentStatus(self):
        return {ch: (self.logChannels.last_time, v) for ch,v in self.logChannels.last_data.items()}
        return {ch: (lc.last_time, lc.last_data) for ch, lc in self.logChannels.items()}

    def mostRecentChanges(self):
        return self.most_recent_changes


if __name__ == "__main__":
    from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QApplication
    import sys


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Watchdog and PyQt5 Integration")
            self.resize(800, 600)

            self.text_edit = QTextEdit()
            layout = QVBoxLayout()
            layout.addWidget(self.text_edit)

            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

            self.file_watcher_thread = FileManager()
            self.file_watcher_thread.processedChanges.connect(self.on_processed_changed)
            self.file_watcher_thread.start()

            self.data = (self.file_watcher_thread.dumpData())

        def on_processed_changed(self, change_dict):
            #print(change_dict)
            self.text_edit.append(str(change_dict))

        def closeEvent(self, event):
            self.file_watcher_thread.stop()
            self.file_watcher_thread.join()
            event.accept()


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())