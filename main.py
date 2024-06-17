from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from form import Ui_MainWindow
import sys
import serial
import serial.tools.list_ports
from  modbus import ModbusRTU
from threadModbus import Worker
import datetime

class GUI(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.functions()
        self.text_edit_errors = ""
        self.text_edit_iteration = 0
        self.text_edit_box=[]
        self.max_errors = 5

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


        self.dict_errors = {0:"Измерение давления не завершено\n\n",
                       1:("Измерение температуры и влажности не завершено\n\n"),
                       2:("Ошибка контрольной суммы датчика температуры и влажности\n\n"),
                       3:("Выход за допустимый диапазон измерения давления\n\n"),
                       4:("Выход за допустимый диапазон измерения температуры\n\n"),
                       5:("Выход за допустимый диапазон измерения влажности\n\n"),
                       6:("Ошибка в работе интерфейса I2C\n\n")
                       }

        self.dict_valid_data = {7: self.textEdit_2,
                           8: self.textEdit_3,
                           9: self.textEdit_4}


    def update_value(self,value):
        try:
            self.textEdit_5.setText("")
            if len(value) == 1:
                if 1 or 2 or 3 or 4 in int(value):
                    self.textEdit_2.setStyleSheet("background-color: red;")
                    self.textEdit_3.setStyleSheet("background-color: red;")
                    self.textEdit_4.setStyleSheet("background-color: red;")
                    self.textEdit_5.setText(value)

            elif "Modbus Error" in value:
                self.stop()
                self.QMessage(value)

            else:
                value = (value.strip('][').split(', '))
                self.textEdit_2.setText(value[1])
                self.textEdit_3.setText(value[2])
                self.textEdit_4.setText(value[3])

                error = ""
                for i in range(7):
                    if (int(value[0]) & 1 << i):
                        error += self.dict_errors[i]

                for i in range(7, 10):
                    if (int(value[0]) & 1 << i):
                        self.dict_valid_data[i].setStyleSheet("background-color: red;")
                    else:
                        self.dict_valid_data[i].setStyleSheet("background-color: green;")

                if error !="":
                    date_time = ((datetime.datetime.now()).strftime("%d.%m.%Y %H:%M:%S"))
                    error = f'{date_time}\n{error}'
                    self.log_error(error)
                    for i in self.text_edit_box[::-1]:
                        self.text_edit_errors+=i
                    self.textEdit_1.setText(self.text_edit_errors)
                    with open("logs.txt", "a") as logs:
                        logs.write(error + '\n')
                self.text_edit_errors = ""

        except:
            self.stop()
            self.QMessage("Ошибка при попытке вывода данных")

    def log_error(self, error_message):
        self.text_edit_box.append(error_message)
        if len(self.text_edit_box) > self.max_errors:
            self.text_edit_box.pop(0)  # Удаляем самую старую ошибку, если превышен лимит

    def QMessage(self,error):
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setText(error)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
    def functions(self):
        self.pushButton_1.clicked.connect(self.run_modbus)
        self.pushButton_2.clicked.connect(self.choose_port)
        self.pushButton_3.clicked.connect(self.stop)
    def stop(self):
        self.thread.isWork = False
        self.isConnection = False
        self.modbus.client.close()
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.comboBox.setEnabled(True)
        print("Client close")
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
                self.QMessage("Подключение не удалось")
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
