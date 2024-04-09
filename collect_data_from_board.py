# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 10:02:06 2024

@author: franc
"""

import time
import sys
import datetime
import os
import numpy as np
import pandas as pd
import paramiko
import subprocess
from subprocess import Popen, PIPE
import adant.iperf as iperf3
import broadcom_csimond as bsci
import telnetlib

class BatmanDevice(telnetlib.Telnet):

    def __init__(self, hostname):
        super().__init__(hostname)
        self.read_until(b"Login: ")
        self.write(b"admin\n")
        self.read_until(b"Password: ")
        self.write(b"admin\n")
        self.write(b"sh\n")
        self.read_until(b"\n# ", timeout=1)
        
    def exec_command(self, cmd):
        self.write(cmd.encode('utf8'))
        response = self.read_until(b"\n~ # ", timeout=1)
        return response.decode()

    def smart_boot(self, duration):
        duration = int(duration + 1)  # account for timing drift
        line = f"cd /tmp; ./adant-agent > /tmp/adant.log & sleep {duration}; killall adant-agent \n"
        return self.exec_command(line)
        
    def manual_boot(self, antenna_code,duration):
        line = f'echo "default_antenna_index={antenna_code}\nsmartmode_enable=0" > /tmp/adant.conf \n'
        self.exec_command(line)
        line = f"cd /tmp; ./adant-agent > /tmp/adant.log & sleep {duration}; killall adant-agent \n"         
        return self.exec_command(line)
    
    def rm_dump(self):
        line = "rm /tmp/*.log \n"
        return self.exec_command(line)
    
    def get_dump(self, dumpname, ip_addr):
        out = self.exec_command("cat /tmp/adant.log >> /tmp/adant-dump.log \n")
        print(out)
        out = self.exec_command(f"cp /tmp/adant-dump.log /tmp/{dumpname} \n")
        print(out)
        # Get dumpfile
        out = self.exec_command(f"cd /tmp; tftp -pl {dumpname} {ip_addr} \n")
        print(out)           
              
    def set_config(self):
        line = "rm -rf /tmp/adant.conf \n"
        return self.exec_command(line)
    
    def enable_collect_cfr(self, interface, mac_address, nl, size, frequency,duration):
        line = f'wl -i wl{interface} csimon enable \n'
        self.exec_command(line)
        
        line = f'csimond {nl} {size} {frequency}  >> /tmp/cfr_dump.log & \n'
        self.exec_command(line)
        
    def start_collect_cfr(self,interface,mac_address):
        line = f'wl -i wl{interface} csimon add {mac_address} \n'
        self.exec_command(line)
        
    def stop_collect_cfr(self,interface, mac_address):
        line = f' wl -i wl{interface} csimon del {mac_address} \n'
        self.exec_command(line)
        
        line = f'wl -i wl{interface} status >> /tmp/cfr_dump.log \n'
        self.exec_command(line)
        
    def get_cfr_dump(self, cfrdumpname, ip_addr):
        out = self.exec_command(f"cp /tmp/cfr_dump.log /tmp/{cfrdumpname} \n")
        print(out)
        # Get dumpfile
        out = self.exec_command(f"cd /tmp; tftp -pl {cfrdumpname} {ip_addr} \n")
        print(out)           


#%% Main

def collect_cfr(ip_batman,ip_server,ip_client,mac_address,duration_test,conf,folder,dumpname,cfr_dumpname,iperf_name):
    print("> INITIALIZE DEV")
    dev = BatmanDevice(ip_batman)
    # ip_server = '192.168.20.50'
    # # test info
    # duration = 10
    # # adant-agent info
    # conf = 10
    # cfr inf
    interface = 1
    nl = 22
    size = 64
    frequency = 1000
    
    
    # filenames
    ipn = os.path.join(folder,iperf_name)
    
    
    # Start adant-agent
    dev.manual_boot(conf, duration_test+1)
    # Set cfr collection
    dev.enable_collect_cfr(interface, mac_address, nl, size, frequency,duration_test)
    # start cfr collection su dev
    dev.start_collect_cfr(interface, mac_address)
    # Start iperf test
    iperf3.run_speedtest(ip_client, duration_test, filename=ipn)
    #stop cfr collection
    dev.stop_collect_cfr(interface,mac_address)  
    # Download dump files
    dev.get_dump(dumpname, ip_server)
    dev.get_cfr_dump(cfr_dumpname, ip_server) 
    
    time.sleep(3)
    
    dev.rm_dump()
    dev.set_config()
    dev.close()

# filename = r"C:\Users\franc\Desktop\Batman\cfr_dump_test0.log"
# x = bsci.get_CSI_from_CSI_dump(filename)

# save_image_path = r"C:\Users\franc\Desktop\Batman\porcodio0.png"
# bsci.plot_a_CSI_of_the_record(x,save_image_path)


    #