from PyQt5 import QtCore, QtWidgets, QtGui
import localvars
import sys
from logger import Logger
logging = Logger(__file__)

SIDE_BY_SIDE_COOLERSYSLOGWIDGET = False

from Core.coolerSysLogMonitor import coolerSysLogManager


class coolerSysLogPathWidget(QtWidgets.QWidget):
    coolerSysLogPathSelected = QtCore.pyqtSignal(str)  # Outgoing
    coolerSysLogPathChanged = QtCore.pyqtSignal(str)   # Possible incoming
    def __init__(self):
        super().__init__()

        self.main_layout = QtWidgets.QHBoxLayout()

        self.directoryLineEdit = QtWidgets.QLineEdit()
        self.directoryLineEdit.setPlaceholderText("coolerSysLog Directory")
        self.directoryLineEdit.setReadOnly(True)
        self.selectButton = QtWidgets.QPushButton("Browse")

        self.selectButton.pressed.connect(self.selectCallback)

        self.coolerSysLogPathChanged.connect(self.set_current_directory)


        self.main_layout.addWidget(self.directoryLineEdit)
        self.main_layout.addWidget(self.selectButton)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.main_layout)


    def set_current_directory(self, current_value = None):
        self.directoryLineEdit.setText(current_value)


    def selectCallback(self):
        options = QtWidgets.QFileDialog.Options()
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "coolerSysLog Directory",
            "",
            options=options
        )
        self.set_current_directory(directory)
        self.emitChanges()

    def emitChanges(self):
        self.coolerSysLogPathSelected.emit(self.directoryLineEdit.text())


class coolerSysLogReaderWidget(QtWidgets.QWidget):
    coolerSysLogLines = QtCore.pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.coolerSysLogLines.connect(self.addLogTexts)
        self.coolerSysLogTextEdit = QtWidgets.QTextEdit()
        self.coolerSysLogTextEdit.setReadOnly(True)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.addWidget(self.coolerSysLogTextEdit)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.verticalLayout)

    def addLogTexts(self, lines=[]):
        """ get/set function of console box """
        if len(lines) == 0:
            return str(self.coolerSysLogTextEdit.toPlainText())
        else:
            self.coolerSysLogTextEdit.setPlainText("\n".join(self.addLogTexts().split("\n")[-400:]) + "".join(lines)) # No \n join because it is a direct readlines()
            self.automaticScroll()

    def automaticScroll(self):
        """ automatically scrolls so latest message is present """
        sb = self.coolerSysLogTextEdit.verticalScrollBar()
        sb.setValue(sb.maximum())

class coolerSysLogMonitorWidget(QtWidgets.QWidget):
    coolerSysLogMonitorChanged = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()

        class MonitorModel(QtCore.QStringListModel):
            def setData(self, index, value, role=QtCore.Qt.EditRole):
                if role == QtCore.Qt.EditRole:
                    monitors = self.stringList()
                    new_monitor = value.strip()
                    if new_monitor in monitors and monitors[index.row()] != new_monitor:
                        QtWidgets.QMessageBox.warning(None, 'Duplicate Monitor',
                                                      'Application is already looking for that string!')
                        return False
                return super().setData(index, value, role)

        self.input = QtWidgets.QLineEdit(self)
        self.input.setPlaceholderText(f'String to match')

        self.add_button = QtWidgets.QPushButton('Add', self)
        self.remove_button = QtWidgets.QPushButton('Remove', self)

        self.list_view = QtWidgets.QListView(self)
        self.model = MonitorModel()  # QtCore.QStringListModel()
        self.list_view.setModel(self.model)
        # Set up layouts
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.add_button)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.remove_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.list_view)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        main_layout.setContentsMargins(0,0,0,0)

        # Connect signals and slots
        self.add_button.clicked.connect(self.add_monitor)
        self.remove_button.clicked.connect(self.remove_monitor)
        # Do it in function instead self.email_input.returnPressed.connect(self.add_email)

    def add_monitor(self, monitor=None):
        if not monitor:
            monitor = self.input.text()
        print()
        if monitor:
            monitors = self.model.stringList()
            if monitor not in monitors:
                monitors.append(monitor)
                self.model.setStringList(monitors)
                self.input.clear()
            else:
                QtWidgets.QMessageBox.warning(self, 'Duplicate Monitor', 'This email address is already in the list.')
        self.coolerSysLogMonitorChanged.emit()

    def keyPressEvent(self, event):
        if (
                event.key() == QtCore.Qt.Key.Key_Delete or event.key() == QtCore.Qt.Key.Key_Backspace) and self.list_view.hasFocus():
            self.remove_monitor()
        elif (
                event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter) and self.input.hasFocus():
            self.add_monitor()
        else:
            super().keyPressEvent(event)

    def remove_monitor(self):
        selected_indexes = self.list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            emails = self.model.stringList()
            del emails[index.row()]
            self.model.setStringList(emails)
        else:
            QtWidgets.QMessageBox.warning(self, 'No Selection', 'Please select an email address to remove.')
        self.coolerSysLogMonitorChanged.emit()

    def remove_monitors(self):
        self.model.setStringList([])
        self.coolerSysLogMonitorChanged.emit()

    def get_monitors(self):
        return self.model.stringList()

    def getValue(self):
        return self.get_monitors()

    def setValue(self, values):
        # First remove all
        self.remove_monitors()
        for email in values:
            self.add_monitor(email)

    def text(self):
        emails = self.get_monitors()
        return emails if len(emails) > 0 else None



class coolerSysLogWidget(QtWidgets.QWidget):
    coolerSysLogMonitorTriggered = QtCore.pyqtSignal(str, list)
    coolerSysLogPathChanged = QtCore.pyqtSignal(str)
    def __init__(self, coolersyslog_path=None):
        super().__init__()
        self.coolersyslog_path = coolersyslog_path

        self.directoryWidget = coolerSysLogPathWidget()
        self.monitorWidget = coolerSysLogMonitorWidget()
        self.readerWidget = coolerSysLogReaderWidget()
        if SIDE_BY_SIDE_COOLERSYSLOGWIDGET:
            self.main_layout = QtWidgets.QGridLayout()
            self.main_layout.addWidget(self.directoryWidget, 0, 0, 1, 2)
            self.main_layout.addWidget(self.readerWidget, 1, 0,1,1)
            self.main_layout.addWidget(self.monitorWidget, 1, 1,1,1)
            self.setLayout(self.main_layout)
        else:
            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.directoryWidget)
            self.main_layout.addWidget(self.monitorWidget)
            self.main_layout.addWidget(self.readerWidget)
            self.setLayout(self.main_layout)

        # Create and start manager
        self.manager = coolerSysLogManager(coolersyslog_path=coolersyslog_path)
        self.manager.startObserver()

        #### Connect signals
        # Log file changes
        self.manager.coolerSysLogLines.connect(self.readerWidget.coolerSysLogLines)
        self.manager.coolerSysLogLines.connect(self.processesNewLines)
        # Monitors changed
        self.monitorWidget.coolerSysLogMonitorChanged.connect(self.monitorChange)
        # Directory changed
        self.directoryWidget.coolerSysLogPathSelected.connect(self.changePath)
        self.coolerSysLogPathChanged.connect(self.directoryWidget.coolerSysLogPathChanged)

        self.coolerSysLogMonitorTriggered.connect(self.monitorTriggered)

        self.monitors = []

    def changePath(self, new_path):
        self.coolersyslog_path = new_path
        self.manager.changePath(self.coolersyslog_path)
        self.coolerSysLogPathChanged.emit(new_path)

    def processesNewLines(self, lines):
        for line in lines:
            if any([m in line for m in self.monitors]):
                self.coolerSysLogMonitorTriggered.emit(line, [m for m in self.monitors if m in line])

    def monitorChange(self):
        self.monitors = self.monitorWidget.get_monitors()

    def monitorTriggered(self, s, monitors):
        logging.debug(f"coolerSysLog Monitor Triggered: {s}\ntriggered monitor(s): {', '.join(monitors)}")
        print(f"coolerSysLog Monitors Triggered: {s}")
        print(f"triggered monitor(s): {', '.join(monitors)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = coolerSysLogWidget()
    w.show()

    sys.exit(app.exec())

