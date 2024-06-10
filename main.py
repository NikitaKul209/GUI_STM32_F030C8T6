import subprocess

import pymodbus.framer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from form import Ui_MainWindow
import sys
import serial
import serial.tools.list_ports
from  modbus import ModbusRTU
from threadModbus import Worker

import asyncio
class GUI(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.functions()

        self.modbus = None
        self.isConnection = False
        self.thread = Worker()
        self.thread.sinout.connect(self.update_value)
        self.thread.start()

        self.pushButton_1.setEnabled(False)
        self.pushButton_3.setEnabled(False)

        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox.addItem(str(port.name))
        self.port = 0

    def update_value(self,value):


        value = (value.strip('][').split(', '))

        self.textEdit_2.setText(value[1])
        self.textEdit_3.setText(value[2])
        self.textEdit_4.setText(value[3])
        error = ""
        if (int(value[0]) & 1 << 0):
            error+=("Измерение давления не завершено\n\n")

        if (int(value[0]) & 1 << 1):
            error+=("Измерение температуры и влажности не завершено\n\n")

        if (int(value[0]) & 1 << 2):
            error +=("Ошибка контрольной суммы датчика температуры и влажности\n\n")

        if (int(value[0]) & 1 << 3):
            error+=("Выход за допустимый диапазон измерения давления\n\n")

        if (int(value[0]) & 1 << 4):
            error +=("Выход за допустимый диапазон измерения температуры\n\n")

        if (int(value[0]) & 1 << 5):
            error +=("Выход за допустимый диапазон измерения влажности\n\n")

        if (int(value[0]) & 1 << 6):
            error +=("Ошибка в работе интерфейса I2C\n\n")
        self.textEdit_1.setText(error)


    def functions(self):
        self.pushButton_1.clicked.connect(self.run_modbus)
        self.pushButton_2.clicked.connect(self.choose_port)
        self.pushButton_3.clicked.connect(self.stop)

    def stop(self):
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.thread.isWork = False

    def choose_port(self):
        self.port =  self.comboBox.currentText()
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.comboBox.setEnabled(False)

    def run_modbus(self):
        if self.isConnection:
            self.thread.isWork = True
            self.pushButton_1.setEnabled(False)
            self.pushButton_3.setEnabled(True)

        else:
            self.modbus = ModbusRTU()
            self.isConnection = self.modbus.run_sync_simple_client(self.port)
            
            if not self.isConnection:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Подключение не удалось")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()

                self.pushButton_1.setEnabled(False)
                self.pushButton_2.setEnabled(True)
                self.comboBox.setEnabled(True)
            else:
                self.thread.modbus = self.modbus
                self.thread.isWork = True
                self.pushButton_1.setEnabled(False)
                self.pushButton_3.setEnabled(True)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = GUI()
    MainWindow.show()
    sys.exit(app.exec_())
