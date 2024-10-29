import pymodbus
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pymodbus import ExceptionResponse


class Worker(QThread):
    sinout=  pyqtSignal(str)
    def __init__(self, parent = None):
        super(Worker,self).__init__(parent)
        self.modbus = None

    def run(self):
        while True:
            value = self.modbus.client_read_data()
            if isinstance(value, pymodbus.exceptions.ModbusIOException):
                self.sinout.emit(str(value))
            elif isinstance(value, pymodbus.pdu.ExceptionResponse):
                self.sinout.emit(str(value))
            elif isinstance(value,pymodbus.exceptions.ConnectionException):
                self.sinout.emit(str(value))
            else:
                values = []
                for i in value.registers:
                    if i >= 2 ** 15:
                        signed_num = i - 2 ** 16
                        values.append(signed_num)
                    else:
                        signed_num = i
                        values.append(signed_num)
                self.sinout.emit(str(values))
            self.sleep(1)