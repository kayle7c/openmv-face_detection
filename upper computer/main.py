import sys
import serial
from openmv import Ui_Form
from PyQt5.QtWidgets import QApplication,QWidget,QInputDialog,QLineEdit
import serial.tools.list_ports
import threading
from typing import Iterable
import time
import datetime
import winsound
import os
import re

serial_flag=0         #串口是否打开
last_port=None        #上次打开的端口
ser=None              #成功打开的串口对象
ui=None               #全局UI
port_names: Iterable[str] = []         #已经搜索到的串口
data=None
now_time=None

record_path=""                        #记录文档的路径,文件格式为txt格式

def warning():
    global ui
    winsound.PlaySound(r"E:\pyqt5\电子报警.wav",winsound.SND_FILENAME)

#获取当前时间
def get_nowtime():
    global now_time
    current_time = datetime.datetime.now()
    now_time = current_time.strftime("[%Y-%m-%d %H:%M:%S]")

def add():
    global ser
    global ui
    value, ok = QInputDialog.getText(None, "添加用户", "请输入用户名", QLineEdit.Normal, "")
    if ser and ok:
        username=value


        time.sleep(3)
        ser.write(username.encode('utf-8'))
        ui.comboBox_2.addItem(username)
        show_window('添加成功！')
        print('add')

def search():
    os.startfile(record_path)

    print('search')

def delete():
    global ui
    global ser
    delete_user_index=ui.comboBox_2.currentIndex()
    delete_user=ui.comboBox_2.currentText()
    if(delete_user_index!=-1):
        ser.write("2".encode('utf-8'))  # 发送采集信号
        time.sleep(3)
        ser.write(delete_user.encode('utf-8'))
        ui.comboBox_2.removeItem(delete_user_index)
        show_window('删除成功！')
    else:
        show_window('请选择要删除的用户')
    print(delete_user)

def open_ser():
    global ser
    ser.write("open".encode('utf-8'))
#接收数据线程
def receive_thread():
    global ser
    global ui
    while(True):
        if ser:
            num=ser.inWaiting()
            if(num!=0):
                data=ser.read(num)
                data=data.decode('utf-8')
                receive_handle(data)
                print(data)
            time.sleep(0.5)

def write_log(data):
    with open(record_path, 'a') as file:
        file.write(now_time+":"+data+'\n')

def receive_handle(data):
    if (data == "warning"):
        warning()
        show_window("陌生人闯入")
        write_log("陌生人闯入")
    if (data == "noperson"):
        return
    if (data != "warning" and data != "noperson"):
        if("warn" in data):
            show_window("陌生人%s号闯入" % (re.findall(r'\d+', data)))
            write_log("陌生人%s号闯入" % (re.findall(r'\d+', data)))
            return
        show_window("用户%s刷脸成功" % (data))
        write_log("用户%s刷脸成功" % (data))

#显示框显示内容显示框显示内容
def show_window(data):
    global ui
    get_nowtime()
    ui.textBrowser.append(now_time + ":" + data)

#串口打开与关闭处理
def serial_handle():
    global serial_flag
    global ui
    global last_port
    global ser
    if serial_flag == 0:
        port = ui.comboBox.currentText()
        if len(port) <= 1:  #没有检测到串口
            print(None)
            return
        else:
            try:
                ser = serial.Serial(port, baudrate=9600)
                print("打开成功")
                ui.pushButton_2.setEnabled(True)
                ui.pushButton.setEnabled(True)
                ui.pushButton_4.setEnabled(True)
                ui.pushButton_5.setEnabled(True)
                serial_flag = 1
                last_port=port
                ui.button_3_change("关闭串口")
            except serial.SerialException as e:
                print("无法打开串口:", e)
    else:
        serial_flag = 0
        ser.close()
        ser = None
        print("关闭成功")
        ui.pushButton_4.setEnabled(False)
        ui.pushButton_2.setEnabled(False)
        ui.pushButton.setEnabled(False)
        ui.pushButton_5.setEnabled(False)
        ui.button_3_change("打开串口")

#串口查找线程
def serial_search_thread():
    global port_names,serial_flag
    while(not serial_flag):
        available_ports = list(serial.tools.list_ports.comports())
        port_names = [port.device for port in available_ports]
        update_combobox(port_names)
        time.sleep(4)

#更新串口列表
def update_combobox(ports):
    global ui
    ui.comboBox.clear()
    ui.comboBox.addItems(ports)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    ui.pushButton.clicked.connect(add)
    ui.pushButton_2.clicked.connect(search)
    ui.pushButton_3.clicked.connect(serial_handle)
    ui.pushButton_4.clicked.connect(delete)
    ui.pushButton_5.clicked.connect(open_ser)
    ui.pushButton_4.setEnabled(False)
    ui.pushButton_2.setEnabled(False)
    ui.pushButton.setEnabled(False)
    ui.pushButton_5.setEnabled(False)
    threading.Thread(target=serial_search_thread, daemon=True).start()
    threading.Thread(target=receive_thread, daemon=True).start()
    sys.exit(app.exec_())
