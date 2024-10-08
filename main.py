from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from form import Ui_MainWindow
import serial.tools.list_ports
from threadModbus import Worker
from  modbus import ModbusRTU
import datetime
import pandas as pd
import serial
import sys
import os
import csv
class GUI(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        if os.path.isfile("Kurchatov_Institute_logo.png"):
            self.setWindowIcon(QtGui.QIcon("Kurchatov_Institute_logo.png"))
        self.functions()
        self.text_edit_errors = ""
        self.text_edit_box = []
        self.max_errors = 15
        self.ModbusConnection = False
        self.modbus = None
        self.isConnection = False
        self.thread = Worker()
        self.thread.sinout.connect(self.update_value)
        self.ButtonStart.setEnabled(False)
        self.ButtonStop.setEnabled(False)
        self.setFixedSize(1200, 600)

        ports = serial.tools.list_ports.comports()
        if len(ports) == 0:
            self.ButtonStart.setEnabled(False)
        else:
            self.ports_name = []
            for port in ports:
                self.ports_name.append(port.name)
                self.comboBox.addItem(str(port))
            self.port = None
            self.choose_port()

        self.plot_date_period = 60

        self.dict_errors = {0:"Ошибка измерения P\n",
                       1:("Ошибка измерения T и RH\n"),
                       2:("Ошибка контрольной суммы датчика T и RH\n"),
                       3:("Выход за допустимый диапазон измерения P\n"),
                       4:("Выход за допустимый диапазон измерения T\n"),
                       5:("Выход за допустимый диапазон измерения RH\n"),
                       6:("Ошибка в работе интерфейса I2C\n")
                       }
        self.dict_valid_data = {7: self.textEdit_Pressure,
                                8: self.textEdit_Temperature,
                                9: self.textEdit_Humidity}

    def update_value(self,value):
        try:
            error = ""
            error_excepions = ["Modbus Error" , "Exception" , "Exception Response"]
            date_time = ((datetime.datetime.now()).strftime("%d.%m.%Y %H:%M:%S"))
            for err in error_excepions:
                if err in value:
                    self.set_text_edit_color("red","red","red")
                    self.display_errors(f"{date_time} Ошибка связи по Modbus (см. logs.txt)"
                                        + '\n',f"{date_time} Ошибка связи по Modbus: {value}" + '\n')
                    self.ModbusConnection = False
                    return
            else:
                if not self.ModbusConnection:
                    self.display_errors(f"{date_time} Связь по Modbus установлена" + '\n',False)
                    self.ModbusConnection = True

                value = (value.strip('][').split(', '))
                self.textEdit_Pressure.setText(str(int(value[1]) / 10))
                self.textEdit_Temperature.setText(str(int(value[2]) / 10))
                self.textEdit_Humidity.setText(str(int(value[3]) / 10))
                self.write_csv(date_time,value)
                for i in range(7):
                    if (int(value[0]) & 1 << i):
                        error +=f'{date_time} {self.dict_errors[i]}'

                for i in range(7, 10):
                    if not((int(value[0]) & 1 << i)):
                        self.dict_valid_data[i].setStyleSheet("background-color: red;")
                    else:
                        self.dict_valid_data[i].setStyleSheet("background-color: green;")
                if error !="":
                    self.display_errors( error,False)

        except:
            self.stop()
            self.q_message("Ошибка при попытке вывода данных")

    def log_error(self, error_message):
        self.text_edit_box.append(error_message)
        if len(self.text_edit_box) > self.max_errors:
            self.text_edit_box.pop(0)


    def write_csv(self,data,value):

        if not os.path.isfile("data.csv"):
            with open("data.csv", mode='a', newline='') as file:
                header = ["Время", "Ошибки", "Давление, кПа", "Температура,°С", "Влажность, %RH"]
                data_writer = csv.writer(file,delimiter=";")
                data_writer.writerow(header)
                os.chmod("data.csv", 0o444)
        else:
            os.chmod("data.csv", 0o777)
            with open("data.csv", mode='a', newline='') as file:
                data_writer = csv.writer(file,delimiter=";")
                val = [data,value[0],*[float(i)/10 for i in value[1:4]]]
                data_writer.writerow(val)
                os.chmod("data.csv", 0o444)

    def plot(self):
        if not os.path.isfile("data.csv"):
            self.q_message("Файл с данными не найден")
        else:
            try:
                df = pd.read_csv('data.csv',encoding='cp1251',delimiter=";")
                date = df['Время']
                pressure = df['Давление, кПа']
                temp = df['Температура,°С']
                humidity = df['Влажность, %RH']
                max_ticks = 1 if min(len(date[::60]),15)==0 else  min(len(date[::60]),15)
                plt.figure(figsize=(15, 8))
                plt.title('График давления',fontweight='bold',fontsize=16)
                plt.xlabel('Время',fontweight='bold',fontsize=16)
                plt.ylabel('Давление, кПа',fontweight='bold',fontsize=16)
                plt.plot(date[::self.plot_date_period], pressure[::self.plot_date_period], marker='o',markerfacecolor = "green", linestyle='-',linewidth = 1, color='black',markersize = 5, label='Давление')
                plt.subplots_adjust(bottom=0.2)
                ax = plt.gca()
                ax.xaxis.set_major_locator(MaxNLocator(nbins = max_ticks))
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid()

                plt.figure(figsize=(15, 8))
                plt.title('График температуры',fontweight='bold',fontsize=16)
                plt.xlabel('Время',fontweight='bold',fontsize=16)
                plt.ylabel('Температура,°С',fontweight='bold',fontsize=16)
                plt.plot(date[::self.plot_date_period], temp[::self.plot_date_period], marker='o',markerfacecolor = "red", linestyle='-',linewidth = 1, color='black',markersize = 5, label='Температура')
                plt.subplots_adjust(bottom=0.2,top=0.9)
                ax = plt.gca()
                ax.xaxis.set_major_locator(MaxNLocator(nbins = max_ticks))
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid()

                plt.figure(figsize=(15, 8))
                plt.title('График относительной влажности',fontweight='bold',fontsize=16)
                plt.xlabel('Время',fontweight='bold',fontsize=16)
                plt.ylabel('Влажность, %RH',fontweight='bold',fontsize=16)
                plt.plot(date[::self.plot_date_period], humidity[::self.plot_date_period], marker='o',markerfacecolor = "blue", linestyle='-',linewidth = 1, color='black',markersize = 5, label='Влажность')
                plt.subplots_adjust(bottom=0.2)
                ax = plt.gca()
                ax.xaxis.set_major_locator(MaxNLocator(nbins = max_ticks))
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid()
                plt.show()
            except:
                self.q_message("Ошибка при построении графика")

    def set_text_edit_color(self,color1, color2, color3):
        self.textEdit_Pressure.setStyleSheet(f'background-color: {color1};')
        self.textEdit_Temperature.setStyleSheet(f'background-color: {color2};')
        self.textEdit_Humidity.setStyleSheet(f'background-color: {color3};')

    def display_errors(self,display_error,log_error):
        if not log_error:
            log_error = display_error
        self.log_error(display_error)
        for i in self.text_edit_box[::-1]:
            self.text_edit_errors += i
        self.textEdit_Messages.setText(self.text_edit_errors)
        with open("logs.txt", "a") as logs:
            logs.write(log_error)
        self.text_edit_errors = ""

    def q_message(self, error):
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setText(error)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
    def functions(self):
        self.ButtonStart.clicked.connect(self.run_modbus)
        self.ButtonStop.clicked.connect(self.stop)
        self.comboBox.currentTextChanged.connect(self.choose_port)
        self.ButtonGraph.clicked.connect(self.plot)
    def stop(self):
        self.thread.terminate()
        self.thread.wait()
        self.isConnection = False
        self.ModbusConnection = False
        self.ButtonStart.setEnabled(True)
        self.ButtonStop.setEnabled(False)
        self.comboBox.setEnabled(True)
        if (self.modbus.client.is_socket_open()):
            try:
                self.modbus.client.close()
            except:
                pass

    def choose_port(self):
        self.port =  self.ports_name[self.comboBox.currentIndex()]
        self.ButtonStart.setEnabled(True)

    def run_modbus(self):
        if self.isConnection:
            self.ButtonStart.setEnabled(False)
            self.ButtonStop.setEnabled(True)
        else:
            self.modbus = ModbusRTU()
            self.isConnection = self.modbus.run_sync_simple_client(self.port)
            if not self.isConnection:
                self.q_message("Подключение не удалось")
                self.ButtonStart.setEnabled(True)
                self.comboBox.setEnabled(True)
            else:
                self.thread.modbus = self.modbus
                self.thread.start()
                self.ButtonStart.setEnabled(False)
                self.ButtonStop.setEnabled(True)
                self.comboBox.setEnabled(False)


if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = GUI()
        MainWindow.show()
        sys.exit(app.exec_())
