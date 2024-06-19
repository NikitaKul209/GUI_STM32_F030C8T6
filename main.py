from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from form import Ui_MainWindow
import serial.tools.list_ports
from threadModbus import Worker
from  modbus import ModbusRTU
import datetime
import serial
import sys
import os

class GUI(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        if os.path.isfile("Kurchatov_Institute_logo.png"):
            self.setWindowIcon(QtGui.QIcon("Kurchatov_Institute_logo.png"))
        self.functions()
        self.text_edit_errors = ""
        self.text_edit_iteration = 0
        self.text_edit_box=[]
        self.max_errors = 15
        self.ModbusConnection = False
        self.modbus = None
        self.isConnection = False
        self.thread = Worker()
        self.thread.sinout.connect(self.update_value)

        self.pushButton_1.setEnabled(False)
        self.pushButton_3.setEnabled(False)

        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)

        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox.addItem(str(port.name))
        self.port = 0
        
        self.dict_errors = {0:"Ошибка измерения P\n",
                       1:("Ошибка измерения T и RH\n"),
                       2:("Ошибка контрольной суммы датчика T и RH\n"),
                       3:("Выход за допустимый диапазон измерения P\n"),
                       4:("Выход за допустимый диапазон измерения T\n"),
                       5:("Выход за допустимый диапазон измерения RH\n"),
                       6:("Ошибка в работе интерфейса I2C\n")
                       }
        self.dict_valid_data = {7: self.textEdit_2,
                           8: self.textEdit_3,
                           9: self.textEdit_4}

    def update_value(self,value):
        try:
            error = ""
            self.textEdit_5.setText("")
            if len(value) == 1:
                self.set_text_edit_color_red("red", "red", "red")
                self.textEdit_5.setText(value)

            elif "No response" in value or "No Response" in value:
                self.set_text_edit_color("red","red","red")
                date_time = ((datetime.datetime.now()).strftime("%d.%m.%Y %H:%M:%S"))
                self.display_errors(f"{date_time} Отсутствует связь по Modbus" + '\n')
                self.ModbusConnection = False
                return

            elif "Modbus Error" in value:
                self.QMessage(value)
                self.stop()
            else:
                if not self.ModbusConnection:
                    date_time = ((datetime.datetime.now()).strftime("%d.%m.%Y %H:%M:%S"))
                    self.display_errors(f"{date_time} Связь по Modbus установлена" + '\n')
                    self.ModbusConnection = True

                value = (value.strip('][').split(', '))
                self.textEdit_2.setText(str(int(value[1])/10))
                self.textEdit_3.setText(str(int(value[2])/10))
                self.textEdit_4.setText(str(int(value[3])/10))

                for i in range(7):
                    if (int(value[0]) & 1 << i):
                        date_time = ((datetime.datetime.now()).strftime("%d.%m.%Y %H:%M:%S"))
                        error +=f'{date_time} {self.dict_errors[i]}'

                for i in range(7, 10):
                    if not((int(value[0]) & 1 << i)):
                        self.dict_valid_data[i].setStyleSheet("background-color: red;")
                    else:
                        self.dict_valid_data[i].setStyleSheet("background-color: green;")
                if error !="":
                    self.display_errors(error)

        except:
            self.stop()
            self.QMessage("Ошибка при попытке вывода данных")

    def log_error(self, error_message):
        self.text_edit_box.append(error_message)
        if len(self.text_edit_box) > self.max_errors:
            self.text_edit_box.pop(0)


    def set_text_edit_color(self,color1, color2, color3):
        self.textEdit_2.setStyleSheet(f'background-color: {color1};')
        self.textEdit_3.setStyleSheet(f'background-color: {color2};')
        self.textEdit_4.setStyleSheet(f'background-color: {color3};')

    def display_errors(self,error):
        self.log_error(error)
        for i in self.text_edit_box[::-1]:
            self.text_edit_errors += i
        self.textEdit_1.setText(self.text_edit_errors)
        with open("logs.txt", "a") as logs:
            logs.write(error + '\n')
        self.text_edit_errors = ""

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
        self.thread.terminate()
        self.thread.wait()
        self.isConnection = False
        self.ModbusConnection = False
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.comboBox.setEnabled(True)
        if (self.modbus.client.is_socket_open()):
            try:
                self.modbus.client.close()
            except:
                pass

    def choose_port(self):
        self.port =  self.comboBox.currentText()
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.comboBox.setEnabled(False)

    def run_modbus(self):
        if self.isConnection:
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
                self.thread.start()
                self.thread.isWork = True
                self.pushButton_1.setEnabled(False)
                self.pushButton_3.setEnabled(True)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = GUI()
    MainWindow.show()
    sys.exit(app.exec_())
