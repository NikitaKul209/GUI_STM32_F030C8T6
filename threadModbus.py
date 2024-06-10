from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *




class Worker(QThread):
    sinout=  pyqtSignal(str)
    def __init__(self, parent = None):
        super(Worker,self).__init__(parent)
        self.modbus = None
        self.isWork = False



    def run(self):
        while True:
            while self.isWork:
                value = self.modbus.client_read_data()
                # Transmitting signal
                # print(f'Значение в потоке {(value)}')
                self.sinout.emit(str(value.registers))
                # Thread hibernates for 2 seconds
                self.sleep(1)