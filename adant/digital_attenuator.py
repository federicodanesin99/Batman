# -*- coding: utf-8 -*-
"""
Created on Thu May 10 18:26:46 2018

@author: Riccardo
"""

import serial
import serial.tools.list_ports


class DigitalAttenuator(object):
    
    def __init__(self):
        try:
            com = [x for x in serial.tools.list_ports.comports()
                if x.hwid.startswith("USB VID:PID=0403:6015")][-1].device
        except IndexError as e:
            raise Exception("DigitalAttenuator device not found")                
        self.serial = serial.Serial(com, 115200, timeout=1)
        self.att = self.get_att()
         
    def get_att_curr(self):
        self.serial.write(b"ATT?\n")
        return self.serial.readline().decode().rstrip()
    
    def set_att_curr(self, val):
        line = "ATT " + val + "\n"
        self.serial.write(line.encode())
        return self.serial.readline().decode().rstrip()
    
    def get_channel(self):
        self.serial.write(b"CHANNEL?\n")
        return self.serial.readline().decode().rstrip()
    
    def set_channel(self, ch):
        line = "CHANNEL " + ch + "\n"
        self.serial.write(line.encode())
        resp = self.serial.readline().decode().rstrip()
        return resp == "OK"
    
    def set_att(self, val):
        self.set_channel("1")
        self.set_att_curr(val)
        self.set_channel("2")
        err = self.set_att_curr(val)
        print(err)
        return err
    
    def get_att(self):
        res = {}
        val = self.get_channel()
        res[val] = self.get_att_curr()
        for ch in {"1", "2"} - {val} :
            self.set_channel(ch)
            res[ch] = self.get_att_curr()
        print(res)
        return res
    
        
if __name__ == "__main__":
    import sys
    try:
        val = sys.argv[1]
    except IndexError:
        val = "10"
    dat = DigitalAttenuator()
    dat.set_att(val)
    dat.get_att()
        
