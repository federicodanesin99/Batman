# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 14:52:12 2023

@author: emanuele
RemoteControl Turn table
"""
import serial
import codecs
import time

class RemoteControl(serial.Serial):
    def __init__(self, com):
        super().__init__() 
        self.baudrate = 115200
        self.port = com
        self.timeout = 1.0
        self.open()
    
    def rc_cmd(self, cmd):
        param = ''
        while "Send command" not in param:
            # self.close()
            # self.open()
            time.sleep(1)
            print("try")
            cmds=bytes("rc --cmd {}\r\n".format(cmd),'utf-8')
            self.write(cmds)
            param=codecs.decode(self.read(3000), 'UTF-8')
            
            print(param)
            cmds=bytes("\r\n",'utf-8')
            self.write(cmds)
            param1=codecs.decode(self.read(1000), 'UTF-8')
            if "Send command" not in param:
                
                self.close()
                self.open()
                time.sleep(1)
                cmds=bytes("restart\r\n",'utf-8')
                self.write(cmds)
                param=codecs.decode(self.read(1000), 'UTF-8')
                time.sleep(1)
                cmds=bytes("\r\n",'utf-8')
                self.write(cmds)
                param=codecs.decode(self.read(1000), 'UTF-8')
                print("send again")
                time.sleep(2)
                
