# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 16:37:05 2021

@author: Jin-youngjun
"""

import winsound as sd
import matplotlib.pyplot as plt
import serial
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import pyvisa
from time import sleep
import time
import os
import glob


form_class = uic.loadUiType("newApd16chTest_1-3.ui")[0]
#rm = pyvisa.ResourceManager()
#dmm = rm.open_resource('USB0::0x1AB1::0x09C4::DM3R232801949::INSTR')
#dmm.write(':FUNCtion:CAPacitance')

#Excell Datalogging export : create a time-stamped file, Option
dateString = time.strftime("%Y-%m-%d_%H%M")
filepath = "./" + dateString + ".csv"

def serial_ports():
     if sys.platform.startswith('win'):
         ports = ['COM%s' % (i + 1) for i in range(256)]
     elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
         # this excludes your current terminal "/dev/tty"
         ports = glob.glob('/dev/tty[A-Za-z]*')
     elif sys.platform.startswith('darwin'):
         ports = glob.glob('/dev/tty.*')
     else:
         raise EnvironmentError('Unsupported platform')
     result = []
     for port in ports:
         try:
             s = serial.Serial(port)
             s.close()
             result.append(port)
         except (OSError, serial.SerialException):
             pass
     return result

class Test:
    def __init__(self):
        name = ""

class Worker(QThread):
    sec_changed = pyqtSignal(str)
    ch_changed = pyqtSignal(str)
    function_changed = pyqtSignal(str)
    random_value = pyqtSignal(str)
    
    def __init__(self, sec=0, parent=None):
        super().__init__()
        #self.seri = seri
        self.chCount = ['5','6','3','4','5','6','7','8','A','B','C','D','E','F','A','B'] #220210 채널 변경을 위해 수정진행
        #self.fcChange = ['I','j'] 
        self.main = parent
        self.working = True
        self.sleep = sleep
        self.sec = sec
        self.num = 0
        
    def __del__(self):
        print("PlanningSun Goodbye~!")
        self.wait()

    def run(self):
        self.main.progressBar.setRange(0,15)
        self.num = 0#while self.working:
        self.main.vChart[0] = 0
        start_time = time.time()
        
        for i in range(16):
            if self.main._exit :                                                #220210 STOP Btn ceheck 
                break
            self.ch_changed.emit(self.chCount[i])
            self.sleep(self.main.doubleSpinBox_8.value())
            self.num = self.num + 1
            
            if self.main.checkBox_2.isChecked() == True :                       #Leak current measure
                self.function_changed.emit('I')
                self.sleep(self.main.doubleSpinBox_9.value())
                #self.sec = float(dmm.query(':MEASure:CURRent:DC?')) *1000000000
                self.main.vMeasured[0] = -14                                                        #임의 지정 -> 실제프로그램 사용시 삭제요망 
                #self.main.vMeasured[0] = float(dmm.query(':MEASure:CURRent:DC?')) *1000000000      #상기 임의 지성 삭제시 활성화 필요
                if (self.main.vMeasured[0]<=0):                                 #가상측정값 반영 음수 -14 -> 양수 1.4
                   self.main.vMeasured[0] =  abs(self.main.vMeasured[0]/10)
                if (self.main.vMeasured[0]>=self.main.doubleSpinBox.value()) and (self.main.vMeasured[0]<=self.main.doubleSpinBox_2.value()) :
                    self.main.vChart[i+1] = self.main.vMeasured[0]
                    self.main.vChart[0] += self.main.vChart[i+1]
                    #self.sec_changed.emit('Current {} = {:3.0f}[nA] ->Good'.format(self.num, self.main.vMeasured[0]))
                    self.main.result_v = 'good'
                    self.main.vResult[0] = 'good'
                else :
                    self.main.vMeasured[0] = float(dmm.query(':MEASure:CURRent:DC?')) *1000000000
                    if (self.main.vMeasured[0]>=self.main.doubleSpinBox.value()) and (self.main.vMeasured[0]<=self.main.doubleSpinBox_2.value()) :
                        self.main.vChart[i+1] = self.main.vMeasured[0]
                        self.main.vChart[0] += self.main.vChart[i+1]
                        #self.sec_changed.emit('Current {} = {:3.0f}[nA] ->Good'.format(self.num, self.main.vMeasured[0]))
                        self.main.result_v = 'good'
                        self.main.vResult[0] = 'good'
                    else :
                        self.main.vChart[i+1] = self.main.vMeasured[0]
                        self.main.vChart[0] += self.main.vChart[i+1]
                        #self.sec_changed.emit('Current {} = {:3.0f}[nA] ->NG'.format(self.num, self.main.vMeasured[0]))
                        self.main.result_h = 'ng'
                        self.main.vResult[1] = 'ng'
            else :
                self.main.vMeasured[0] = 0
                
                        
            if self.main.checkBox_3.isChecked() == True :
                self.function_changed.emit('I')
                self.sleep(self.main.doubleSpinBox_9.value())
                self.main.vMeasured[1] = float(dmm.query(':MEASure:CAPacitance?')) *1000000000
                if (self.main.vMeasured[1]>=self.main.doubleSpinBox_4.value()) and (self.main.vMeasured[1]<=self.main.doubleSpinBox_5.value()) :
                    #self.sec_changed.emit('Capacitance {} = {:3.0}[nF] ->Good'.format(self.num, self.main.vMeasured[1]))
                    self.main.result_v = 'good'
                    self.main.vResult[2] = 'good'                    
                else :
                    self.main.vMeasured[1] = float(dmm.query(':MEASure:CAPacitance?')) *1000000000
                    if (self.main.vMeasured[1]>=self.main.doubleSpinBox_4.value()) and (self.main.vMeasured[1]<=self.main.doubleSpinBox_5.value()) :
                        #self.sec_changed.emit('Capacitance {} = {:3.0}[nF] ->Good'.format(self.num, self.main.vMeasured[1]))
                        self.main.result_v = 'good'
                        self.main.vResult[2] = 'good'
                    else:
                        #self.sec_changed.emit('Capacitance {} = {:3.0}[nF] ->NG'.format(self.num, self.main.vMeasured[1]))
                        self.main.result_h = 'ng'
                        self.main.vResult[3] = 'ng'
            else : 
                self.main.vMeasured[1] = 0
                

            if self.main.checkBox_4.isChecked() == True :
                self.function_changed.emit('J')
                self.sleep(self.main.doubleSpinBox_9.value())
                self.main.vMeasured[2] = float(dmm.query(':MEASure:DIODe?'))
                if (self.main.vMeasured[2]>=self.main.doubleSpinBox_6.value()) and (self.main.vMeasured[2]<=self.main.doubleSpinBox_7.value()) : 
                    #self.sec_changed.emit('Vf {} = {:2.3f}[V] ->Good'.format(self.num, self.main.vMeasured[2]))
                    self.main.result_v = 'good'
                    self.main.vResult[4] = 'good'
                else :
                    self.main.vMeasured[2] = float(dmm.query(':MEASure:DIODe?'))
                    if (self.main.vMeasured[2]>=self.main.doubleSpinBox_6.value()) and (self.main.vMeasured[2]<=self.main.doubleSpinBox_7.value()) : 
                        #self.sec_changed.emit('Vf {} = {:2.3f}[V] ->Good'.format(self.num, self.main.vMeasured[2]))
                        self.main.result_v = 'good'
                        self.main.vResult[4] = 'good'
                    else :
                        #self.sec_changed.emit('Vf {} = {:2.3f}[V] ->NG'.format(self.num, self.main.vMeasured[2]))
                        self.main.result_h = 'ng'
                        self.main.vResult[5] = 'ng'
            else :
                self.main.vMeasured[2] = 0
                  
            if (self.main.result_v == 'good') & (self.main.result_h!='ng'): 
                self.main.result_v =''
                self.sec_changed.emit('No.{}-{:1}ch Current={:1.1f}[nA],Cap={:2.1f}[nF],Vf={:2.2f}[V],Test Good'
                                        .format(self.main.ttCount+1,i+1,self.main.vMeasured[0],self.main.vMeasured[1],self.main.vMeasured[2])) #220210 textbrower No 1-0ch->1-1ch '0'-> +1
                with open(filepath, "a") as file:
                    file.write("No.{}-{:1}ch,{:1.0f},{:2.1f},{:2.2f},{}\n".format(self.main.ttCount+1,i+1,self.main.vMeasured[0],
                                                                       self.main.vMeasured[1],self.main.vMeasured[2],'Good'))                  #220210 file No 1-0ch->1-1ch '0'-> +1 
            else:
                self.main.result_h=''
                self.sec_changed.emit('No.{}-{:1}ch Current={:1.1f}[nA],Cap={:2.1f}[nF],Vf={:2.2f}[V],Test NG'
                                      .format(self.main.ttCount+1,i+1,self.main.vMeasured[0],self.main.vMeasured[1],self.main.vMeasured[2])) #220210 textbrower No 1-0ch->1-1ch '0'-> +1
                with open(filepath, "a") as file:
                    file.write("No.{}-{:1}ch,{:1.0f},{:2.1f},{:2.2f},{}\n".format(self.main.ttCount+1,i+1,self.main.vMeasured[0],
                                                                      self.main.vMeasured[1],self.main.vMeasured[2],'NG'))                      #220210 file No 1-0ch->1-1ch '0'-> +1 
            self.random_value.emit(str(i))
            self.main.tCount += 1

        self.main.ttCount += 1
        self.main.tableWidget.setItem(self.main.ttCount-1, 0, QTableWidgetItem(str(self.main.ttCount))) 
        
        if self.main.checkBox_2.isChecked() == True : 
            if (self.main.vResult[0] == 'good') & (self.main.vResult[1]!='ng'):
                self.main.tableWidget.setItem(self.main.ttCount-1, 1, QTableWidgetItem('Pass')) 
            else:
                self.main.tableWidget.setItem(self.main.ttCount-1, 1, QTableWidgetItem('Fail'))
        else:
            self.main.tableWidget.setItem(self.main.ttCount-1, 1, QTableWidgetItem('Skip')) 
        if self.main.checkBox_3.isChecked() == True : 
            if (self.main.vResult[2] == 'good') & (self.main.vResult[3]!='ng'):
                self.main.tableWidget.setItem(self.main.ttCount-1, 2, QTableWidgetItem('Pass')) 
            else:
                self.main.tableWidget.setItem(self.main.ttCount-1, 2, QTableWidgetItem('Fail'))
        else:
            self.main.tableWidget.setItem(self.main.ttCount-1, 2, QTableWidgetItem('Skip'))
        if self.main.checkBox_4.isChecked() == True :     
            if (self.main.vResult[4] == 'good') & (self.main.vResult[5]!='ng'):
                self.main.tableWidget.setItem(self.main.ttCount-1, 3, QTableWidgetItem('Pass')) 
            else:
                self.main.tableWidget.setItem(self.main.ttCount-1, 3, QTableWidgetItem('Fail'))
        else:
            self.main.tableWidget.setItem(self.main.ttCount-1, 3, QTableWidgetItem('Skip'))
            
        if (self.main.vResult[1] == 'ng') | (self.main.vResult[3] == 'ng') | (self.main.vResult[5] == 'ng'):
            self.main.tableWidget.setItem(self.main.ttCount-1, 4, QTableWidgetItem('NG'))
            #1sd.Beep(8000, 1000)
            self.main.vResult= [0,0,0,0,0,0,0]
            self.main.result_ng += 1
            self.main.label_8.setText("{:5}".format(self.main.result_ng))
            self.main.label_8.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.main.label_9.setText("{:5}".format(self.main.result_good))
            self.main.label_9.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
    
        else:
            self.main.tableWidget.setItem(self.main.ttCount-1, 4, QTableWidgetItem('Good'))
            #1sd.Beep(4000, 500)
            self.main.vResult= [0,0,0,0,0,0,0]
            self.main.result_good += 1
            self.main.label_8.setText("{:5}".format(self.main.result_ng))
            self.main.label_8.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.main.label_9.setText("{:5}".format(self.main.result_good))
            self.main.label_9.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        
        self.main.vChart[0] = self.main.vChart[0]/16
        #print(self.vChart[0])
        if self.main.checkBox_2.isChecked() == True :
            for j in range(0,17):
                self.main.vsChart[j] = (1-(self.main.vChart[j]/self.main.vChart[0]))*100
                #print(self.main.vChart[j])    
        self.main.lcdNumber.display("{:5}".format(self.main.result_good+self.main.result_ng))
        self.main.result_yield = (self.main.result_good/(self.main.result_good+self.main.result_ng))*100
        self.main.label_10.setText("{:5.2f}%".format(self.main.result_yield))
        self.main.label_10.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.sec_changed.emit('------------------------------------------------------> [{}] '.format(self.main.result_good+self.main.result_ng))
        self.main.tableWidget.setRowCount(16*(1+(self.main.result_good+self.main.result_ng))) 
        end_time = time.time()
        self.main.textBrowser_2.append("No.{} Test tact time ={:3.1f}[sec]".format(self.main.ttCount,end_time-start_time)) #{:1.3f}",end_time-start_time)
        #1self.textBrowser_2.append("No.{} Test tact time ={:3.1f}[sec]".format(self.ttCount,end_time-start_time)) #{:1.3f}",end_time-start_time)
      
        self.main.btn_1.setEnabled(True)
        self.main.btn_2.setEnabled(True)
        #@pyqtSlot("PyQt_PyObject")    # @pyqtSlot(object) 도 가능..
        #def recive_instance_singal(self, inst):
        #    print(inst.name) 
        

class MyWindow(QMainWindow,form_class):
    #add_sec_signal = pyqtSignal()
    #send_instance_singal = pyqtSignal("PyQt_PyObject")     #class 객체로 보낼때는 ("PyQt_PyObject") 사용

    def __init__(self, parent=None):
        #super().__init__(parent)
        super().__init__()
        with open(filepath, "a") as file:
            file.write("No, L/C[nA], DC cap[nF], DC Vf[V], <Test Result>\n")
        self.setupUi(self)
        self.dialog = QDialog() 
        #self.seri = seri
        self.sleep = sleep
        self._exit = False
        
        self.result_v = ''
        self.result_h = ''
        self.result_good=0
        self.result_ng=0
        self.result_yield=0
        self.tCount = 0
        self.ttCount = 0
        
        self.tableWidget.setRowCount(16) 
        self.vMeasured = [0.001,0.001,0.001,0.001,0.001]
        self.vChart = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.vsChart = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.vResult= [0,0,0,0,0,0,0,0]

        self.btn_1.clicked.connect(self.time_start)
        self.btn_2.clicked.connect(self.time_stop)
        self.btn_3.clicked.connect(self.button3Function)
        self.btn_4.clicked.connect(self.button4Function)
        self.btn_5.clicked.connect(self.button5Function)
        self.btn_6.clicked.connect(self.button6Function)
        self.btn_7.clicked.connect(self.time_exit)
        
        self.checkBox.stateChanged.connect(self.ckFunction)                 
        #self.checkBox_2.stateChanged.connect(self.ck2Function)
        #self.checkBox_3.stateChanged.connect(self.ck3Function)
        #self.checkBox_4.stateChanged.connect(self.ck4Function)
        
        self.radioButton.clicked.connect(self.radioFunction)
        self.radioButton_2.clicked.connect(self.radio2Function)
        self.radioButton_3.clicked.connect(self.radio3Function)
        self.radioButton_4.clicked.connect(self.radio4Function)
        self.radioButton_5.clicked.connect(self.radio5Function)
        self.radioButton_6.clicked.connect(self.radio6Function)
        #self.radioButton_9.clicked.connect(self.radio9Function)
        #self.radioButton_10.clicked.connect(self.radio10Function) #light Condition
        self.radioButton_11.clicked.connect(self.radio11Function)
        self.radioButton_12.clicked.connect(self.radio12Function)
        self.radioButton_13.clicked.connect(self.radio13Function)
        self.radioButton_14.clicked.connect(self.radio14Function)
        self.radioButton_15.clicked.connect(self.radio15Function)
        self.radioButton_16.clicked.connect(self.radio16Function)
        self.radioButton_17.clicked.connect(self.radio17Function)
        self.radioButton_18.clicked.connect(self.radio18Function)
        self.radioButton_19.clicked.connect(self.radio19Function)
        self.radioButton_20.clicked.connect(self.radio20Function)
        self.radioButton_21.clicked.connect(self.radio21Function)
        self.radioButton_22.clicked.connect(self.radio22Function)
        self.radioButton_23.clicked.connect(self.radio23Function)
        self.radioButton_24.clicked.connect(self.radio24Function)
        #self.btn3.clicked.connect(self.add_sec)
        #self.btn4.clicked.connect(self.send_instance)
        allWords = serial_ports()
        self.comboBox.addItems(allWords)
        
        self.radioButton.setDisabled(True)
        self.btn_1.setDisabled(True)
        self.btn_4.setDisabled(True)
        self.radioButton_2.setDisabled(True)
        self.radioButton_3.setDisabled(True)
        self.radioButton_4.setDisabled(True)
        self.radioButton_5.setDisabled(True)
        self.radioButton_6.setDisabled(True)
        #self.radioButton_10.setDisabled(True)
        self.radioButton_11.setDisabled(True)
        self.radioButton_12.setDisabled(True)
        self.radioButton_13.setDisabled(True)
        self.radioButton_14.setDisabled(True)
        self.radioButton_15.setDisabled(True)
        self.radioButton_16.setDisabled(True)
        self.radioButton_17.setDisabled(True)
        self.radioButton_18.setDisabled(True)
        self.radioButton_19.setDisabled(True)
        self.radioButton_20.setDisabled(True)
        self.groupBox_4.setDisabled(True)

        self.checkBox.setDisabled(True)
        self.groupBox_4.setDisabled(True)
               

        self.th = Worker(parent=self)
        self.th.sec_changed.connect(self.time_update)  # custom signal from worker thread to main thread
        self.th.ch_changed.connect(self.ch_update)
        self.th.function_changed.connect(self.function_changed)
        self.th.random_value.connect(self.progressbar_update)
        
        #self.add_sec_signal.connect(self.th.add_sec)   # custom signal from main thread to worker thread
        #self.send_instance_singal.connect(self.th.recive_instance_singal)
        self.show()

    @pyqtSlot()
    def time_start(self):
        if self.th.isRunning():  # 쓰레드가 돌아가고 있다면 
            self.th.terminate()  # 현재 돌아가는 thread 를 중지시킨다
            self.th.wait()       # 새롭게 thread를 대기한후
            self.th.start() 
        self.th.start()
        self.btn_1.setDisabled(True)
        self.btn_2.setDisabled(True)
        self.th.working = True
        self._exit = False
        
    @pyqtSlot()
    def time_exit(self):
        self._exit = True
        #self.progressBar.setValue(0)

    @pyqtSlot()
    def time_stop(self):
       # self.wait(1000)
        #self.th.working = False
        #self.th.terminate()
        self.textBrowser.clear()
        self.tableWidget.clear()
        column_headers = ['No.', 'L/C[nA]','DC Cap[F]','DC Vf[V]','<Test Result>']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        #self.progressBar.setValue(0)
        self.result_good=0
        self.result_ng=0
        self.result_yield=0
        self.tCount=0
        self.ttCount=0
        self.tableWidget.setRowCount(16) 
        self.lcdNumber.display("{:5}".format(0))
        self.label_8.setText("{:5}".format(0))
        self.label_9.setText("{:5}".format(0))
        self.label_10.setText("{:5}".format(0))
           
    @pyqtSlot()
    def button3Function(self):
        global seri
        seri = serial.Serial(port=self.comboBox.currentText(),baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS) 
        self.btnDialog = QPushButton("OK!", self.dialog)
        self.btnDialog.move(140, 90)
        self.btnDialog.clicked.connect(self.dialog.close)
        self.dialog.setWindowTitle('COM Port 연결')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(400, 200)
        self.dialog.show()
        #seri.close()
        if seri.isOpen() == True:  #시리얼 포트가 open인지 확인
            self.btn_1.setEnabled(True)
            self.btn_3.setDisabled(True)
            self.btn_4.setEnabled(True)
            self.doubleSpinBox.setDisabled(True)
            self.doubleSpinBox_2.setDisabled(True)
            self.groupBox.setDisabled(True)
            self.checkBox.setEnabled(True)
            if self.checkBox.isChecked() == True :
                self.btn_1.setDisabled(True)
            else :
                self.btn_1.setEnabled(True)

    @pyqtSlot()
    def button4Function(self):
        self.btnDialog = QPushButton("끊김!", self.dialog)
        self.btnDialog.move(140, 90)
        self.btnDialog.clicked.connect(self.dialog.close)
        self.dialog.setWindowTitle('COM Port 끊기')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(400, 200)
        self.dialog.show()
        seri.close() 
        if seri.isOpen() == False :  #시리얼 포트가 open인지 확인
            self.btn_1.setDisabled(True)
            self.btn_3.setEnabled(True)
            self.btn_4.setDisabled(True)
            self.doubleSpinBox.setEnabled(True)
            self.doubleSpinBox_2.setEnabled(True)
            self.groupBox.setEnabled(True)
            self.checkBox.setDisabled(True)
        
    @pyqtSlot(str)
    def time_update(self, sec):
        self.textBrowser.append(sec)
        #self.sleep(0.5)
        #print("....")
    
    @pyqtSlot(str)
    def ch_update(self, ch):
        seri.write(bytes('eyes' + str(ch)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
        #self.sleep(0.5)
    
    @pyqtSlot(str)
    def function_changed(self, func):
        seri.write(bytes('eyes' + str(func)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
        #self.sleep(0.5)

    @pyqtSlot(str)
    def progressbar_update(self, val):
        self.progressBar.setValue(int(val))

    @pyqtSlot()
    def ckFunction(self):                                                   #11.SHM ch Btn Enable and Disable
        if self.checkBox.isChecked() == True :
            self.btn_1.setDisabled(True) 
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)
            self.radioButton_3.setEnabled(True)
            self.radioButton_4.setEnabled(True)
            self.radioButton_5.setEnabled(True)
            self.radioButton_6.setEnabled(True)
            self.radioButton_11.setEnabled(True)
            self.radioButton_12.setEnabled(True)
            self.radioButton_13.setEnabled(True)
            self.radioButton_14.setEnabled(True)
            self.radioButton_15.setEnabled(True)
            self.radioButton_16.setEnabled(True)
            self.radioButton_17.setEnabled(True)
            self.radioButton_18.setEnabled(True)
            self.radioButton_19.setEnabled(True)
            self.radioButton_20.setEnabled(True)
            self.groupBox_4.setEnabled(True)
            
        if self.checkBox.isChecked() == False :
            self.btn_1.setEnabled(True)
            self.radioButton.setDisabled(True)
            self.radioButton_2.setDisabled(True)
            self.radioButton_3.setDisabled(True)
            self.radioButton_4.setDisabled(True)
            self.radioButton_5.setDisabled(True)
            self.radioButton_6.setDisabled(True)
            self.radioButton_11.setDisabled(True)
            self.radioButton_12.setDisabled(True)
            self.radioButton_13.setDisabled(True)
            self.radioButton_14.setDisabled(True)
            self.radioButton_15.setDisabled(True)
            self.radioButton_16.setDisabled(True)
            self.radioButton_17.setDisabled(True)
            self.radioButton_18.setDisabled(True)
            self.radioButton_19.setDisabled(True)
            self.radioButton_20.setDisabled(True)
            self.groupBox_4.setDisabled(True) 

    @pyqtSlot()
    def button5Function(self):
        plt.figure(figsize=(13,8))
        levels = ['AVG.','1ch','2ch','3ch','4ch','5ch','6ch','7ch','8ch','9ch','10ch','11ch','12ch'
                  ,'13ch','14ch','15ch','16ch']    
        #plt.bar(levels,16,color="orange")
        colors = ['blue','orange','orange','orange','orange','orange','orange','orange','orange',
                  'orange','orange','orange','orange','orange','orange','orange','orange','orange',]
        plt.xlabel("Channel")
        plt.ylabel("[nA]")
        plt.title("16APD Leakage Current")
        for i, v in enumerate(levels):
            plt.bar(levels[i],self.vChart[i],color=colors[i])
            plt.text(v,self.vChart[i],"{:3.0f}".format(self.vChart[i]), fontsize=12, color="blue",
                     horizontalalignment='center',verticalalignment='bottom')
        plt.show()
    
    @pyqtSlot()
    def button6Function(self):
        plt.figure(figsize=(13,8))
        levels = ['AVG.','1ch','2ch','3ch','4ch','5ch','6ch','7ch','8ch','9ch','10ch','11ch','12ch'
                  ,'13ch','14ch','15ch','16ch'] 
        colors = ['blue','orange','orange','orange','orange','orange','orange','orange','orange',
                  'orange','orange','orange','orange','orange','orange','orange','orange','orange',]
        #plt.bar(levels,self.vsChart[i],color="orange")
        plt.xlabel("Channel")
        plt.ylabel("Avg.Vs[%]")
        plt.title("16APD Leakage Current")
        for i, v in enumerate(levels):
            plt.bar(levels[i],self.vsChart[i],color=colors[i])
            plt.text(v,self.vsChart[i],"{:3.1f}".format(self.vsChart[i]), fontsize=12, color="red",
                     horizontalalignment='center',verticalalignment='bottom')
        plt.show()  

    @pyqtSlot()
    def radioFunction(self):                                                
        seri.write(bytes('eyes' + str(5)+'\n', encoding='ascii'))               #220210 매뉴얼 작업시 1ch->5ch 변경됨.
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio2Function(self):
        seri.write(bytes('eyes' + str(6)+'\n', encoding='ascii'))               #220210 매뉴얼 작업시 2ch->6ch 변경됨.
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio3Function(self):
        seri.write(bytes('eyes' + str(3)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio4Function(self):    
        seri.write(bytes('eyes' + str(4)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio5Function(self):
        seri.write(bytes('eyes' + str(5)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio6Function(self):
        seri.write(bytes('eyes' + str(6)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio11Function(self):
        seri.write(bytes('eyes' + str(7)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio12Function(self):
        seri.write(bytes('eyes' + str(8)+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio13Function(self):                                                
        seri.write(bytes('eyes' + str('A')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio14Function(self):
        seri.write(bytes('eyes' + str('B')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio15Function(self):
        seri.write(bytes('eyes' + str('C')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio16Function(self):
        seri.write(bytes('eyes' + str('D')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio17Function(self):
        seri.write(bytes('eyes' + str('E')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio18Function(self):
        seri.write(bytes('eyes' + str('F')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio19Function(self):
        seri.write(bytes('eyes' + str('A')+'\n', encoding='ascii'))             #220210 매뉴얼 작업시 15ch->9ch 변경됨.
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio20Function(self):
        seri.write(bytes('eyes' + str('B')+'\n', encoding='ascii'))             #220210 매뉴얼 작업시 16ch->10ch 변경됨.
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
    @pyqtSlot()
    def radio21Function(self):
        seri.write(bytes('eyes' + str('I')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
        #dmm.write(':FUNCtion:VOLTage:DC')
        #@dmm.write(':FUNCtion:CURRent:DC')
        #print(dmm.query(':MEASure:CURRent:DC?'))
    @pyqtSlot()
    def radio22Function(self):
        seri.write(bytes('eyes' + str('I')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
        #dmm.write(':FUNCtion:VOLTage:DC')
        #@dmm.write(':FUNCtion:CAPacitance')
        #print(dmm.query(':MEASure:CAPacitance?'))
    @pyqtSlot()
    def radio23Function(self):
        seri.write(bytes('eyes' + str('J')+'\n', encoding='ascii'))
        #@if seri.readable():
        #@    res = seri.readline()
            #print(res.decode()[:len(res)-1])
        #dmm.write(':FUNCtion:VOLTage:DC')
        #@dmm.write(':FUNCtion:DIODe')
        #print(dmm.query('MEASure:DIODe?'))
    @pyqtSlot()
    def radio24Function(self):
        dmm.write('*RST')
        #rint(dmm.query('MEASure:DIODe?'))        
    #@pyqtSlot()
    #def send_instance(self):
    #    t1 = Test()
    #    t1.name = "SuperPower!!!"
    #    self.send_instance_singal.emit(t1)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MyWindow()
    form.show()
    app.exec_()