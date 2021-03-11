import serial
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtGui import QCloseEvent
from PyQt5.uic import loadUi


class Runnable(QRunnable):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser

    def run(self):
        # Your long-running task goes here ...
        while True:
            packet = self.ser.read(4)
            print(str(packet))
            time.sleep(1)


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        loadUi('main_window.ui', self)

        # with open("style.qss", "r") as f:
        #    _style = f.read()
        #    self.setStyleSheet(_style)
        # f.close()

        self.ser = serial.Serial()
        self.ser.baudrate = 115200

        self.pushButton.clicked.connect(self.emergency_stop)
        self.comboBox.addItems(self.serial_ports())
        self.pushButton_2.clicked.connect(self.serial_port_connect)

        self.pool = QThreadPool.globalInstance()
        self.runnable = Runnable(self.ser)

        self.show()

    def emergency_stop(self):
        self.ser.write("1".encode())

    def update_data(self):
        packet = self.ser.read(4)
        self.lineEdit_2.setText(str(packet[0]))
        self.lineEdit_6.setText(str(packet[1]))
        self.lineEdit_7.setText(str(packet[2]))
        self.lineEdit_8.setText(str(packet[3]))

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(self, "Message", "Czy na pewno chcesz wyłączyć program ?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.pool.stop(self.runnable)
            event.accept()
        else:
            event.ignore()

    def serial_ports(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        result = []
        result.append('COM#')
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def serial_port_connect(self):
        if int(self.comboBox.currentIndex()) > 0:
            self.ser.port = str(self.comboBox.currentText())
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(False)
            self.pool.start(self.runnable)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = AppWindow()

    sys.exit(app.exec_())
