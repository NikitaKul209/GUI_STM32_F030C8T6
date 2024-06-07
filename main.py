import subprocess

import pymodbus.framer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from form import Ui_MainWindow
import sys
import serial
import serial.tools.list_ports
import  modbus
import asyncio
class GUI(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.functions()

        self.pushButton_1.setEnabled(False)
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox.addItem(str(port.name))
        self.port = 0

    def functions(self):
        self.pushButton_1.clicked.connect(lambda: self.run_modbus() )
        self.pushButton_2.clicked.connect(lambda: self.choose_port())

    def choose_port(self):
        self.port =  self.comboBox.currentText()
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.comboBox.setEnabled(False)

    def run_modbus(self):
        try:
            asyncio.run(modbus.run_async_simple_client(port=self.port,framer=pymodbus.Framer.RTU))
        except BaseException as e:

            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()


            self.pushButton_1.setEnabled(False)
            self.pushButton_2.setEnabled(True)
            self.comboBox.setEnabled(True)



if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = GUI()
    MainWindow.show()
    sys.exit(app.exec_())
