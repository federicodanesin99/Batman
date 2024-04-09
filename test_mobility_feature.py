# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:57:42 2024

@author: franc
"""

import serial
import time
import sys
import datetime
import os
import numpy as np
import pandas as pd
import paramiko
import subprocess
from subprocess import Popen, PIPE
# from adant.rotation_board import AdantStepper
# from adant.digital_attenuator import DigitalAttenuator
from adant.remote_control import RemoteControl
import threading



class BatmanDevice(serial.Serial):

    def __init__(self, com):
        super().__init__()
        self.baudrate = 115200
        self.port = com
        self.timeout = 1.0
        self.open()

        self.getdump = "tftp -pl {} {} \r\n"
        
    def exec_command(self, text):
        self.write(bytes(text, 'utf-8'))
        return self.read().decode('utf-8')

    def smart_boot(self, duration):
        duration = int(duration + 1)  # account for timing drift
        line = f"cd /tmp; ./adant-agent > /tmp/adant.log & sleep {duration}; killall adant-agent \n"
        return self.exec_command(line)
        
    def manual_boot(self, antenna_code, duration):
        line = f'echo "default_antenna_index={antenna_code}\nsmartmode_enable=0" > /tmp/adant.conf \n'
        self.exec_command(line)
        
        line = f"cd /tmp; ./adant-agent & sleep {duration}; killall adant-agent \n"
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
    
def run_iperf_client(ip_client, duration, folder, iperf_name):
    os.system(r'C:\Users\franc\Desktop\iperf-3.1.3\iperf3.exe -c {} -P 4 -t {} > {}\{}'.format(ip_client,duration,folder,iperf_name))
    
def run_speed_test_mu(path, duration, outf1, outf2):
    script = 'iperf3_MU.bat'
    script_path = os.path.join(path,script)
    
    outfile1 = os.path.join(path, outf1)
    outfile2 = os.path.join(path, outf2)
    
    args = [script_path, duration, outfile1, outfile2]
    p = subprocess.Popen(args, stdout=PIPE, stderr=PIPE, shell=True, text=True)

    for line in p.stdout:
        print(line)

#%% Main

# Test 1 -> attenuation sweep
# Test 2 -> angle sweep
# Test 3 -> attenuation and angle sweep

folder = r'C:\Users\franc\Desktop\Batman\20240329'

ip_client = '192.168.10.210'

TEST = 2

test_duration = 60
run_sleep_time = 3

max_attenuation = 30
min_attenuation = 0 
step_att = 3

first_angle = 0
last_angle = 360
step_ang = 22.5

rotation_cmd = {90 : "0xe41b",
                45 : "0xfd02",
                22.5 : "0xfc03",
                'CW': "0xbb44",
                'ACW':"0xbe41"}

com_rotation_board = 'COM4'

conf = 42
run = 5

iperf_name = f'test{TEST}_conf{conf}_run{run}.log'

iperf_name_cl1 = f'cl1_test{TEST}_conf{conf}_run{run}.log'
iperf_name_cl2 = f'cl2_test{TEST}_conf{conf}_run{run}.log'


# print("> INITIALIZE DEV")
# access_point_com = "COM3"
# dev = BatmanDevice(access_point_com)

# if conf == -1:
#     dev.smart_boot(test_duration+2)
# else:
#     dev.manual_boot(conf, test_duration+2)

start = time.time()

if TEST == 1:
    
    # print("> INITIALIZE DigitalAttenuator")
    # dat = DigitalAttenuator()
    
    end = time.time()
    
    att = min_attenuation
    
    thread = threading.Thread(target=run_iperf_client, args=(ip_client, test_duration, folder, iperf_name))
    thread.start()
    
    while(end - start < test_duration):
        
        end = time.time()
        
        print(f'TEST: {TEST} - Attenuation: {att}dB')
        # dat.set_att(att)

        time.sleep(run_sleep_time)
        
        att = att + step_att
        
        if att == max_attenuation:
            att = min_attenuation
    
    thread.join()
    
    # dev.close()
    
elif TEST == 2: 
    
    # print("> INITIALIZE STEPPER")
    # stepper0 = AdantStepper(version=1)
    
    print("> INITIALIZE STEPPER")
    rc = RemoteControl("COM4")
    
    end = time.time()
    
    ang = first_angle
    
    # thread = threading.Thread(target=run_iperf_client, args=(ip_client, test_duration, folder, iperf_name))
    thread = threading.Thread(target=run_speed_test_mu, args=(folder, str(test_duration), iperf_name_cl1, iperf_name_cl2))
    thread.start()
    
    while(end - start < test_duration):
        
        end = time.time()
        
        time.sleep(run_sleep_time)
        
        # chamber rotation board
        # if (ang + step_ang == 360):
            # ang = first_angle
            # print("STEPPER: rotating to home:", ang)
            # stepper0.rotate(ang - step_ang)
            # time.sleep(10) # this is needed to let the rotation table coming to home
        # else:
        #     ang = ang + step_ang
        #     print("STEPPER: rotating to:", ang)
        #     stepper0.rotate(-step_ang)
        
        # TH rotation board
        if (ang + step_ang == 360):
            print("Test finished:", ang)
        else:
            print("STEPPER: rotating to:", ang+step_ang)
            rc.rc_cmd(rotation_cmd[step_ang])
            ang = ang + step_ang
            
        print(f'TEST: {TEST} - Angle: {ang}°')
        
    # dev.close()
    rc.close()
    # stepper0.close()
    
elif TEST == 3: 
    
    # print("> INITIALIZE STEPPER")
    # stepper0 = AdantStepper(version=1)
    
    # print("> INITIALIZE DigitalAttenuator")
    # dat = DigitalAttenuator()
    
    end = time.time()

    att = min_attenuation
    ang = first_angle
    
    thread = threading.Thread(target=run_iperf_client, args=(ip_client, test_duration, folder, iperf_name))
    thread.start()
    
    while(end - start < test_duration):
        
        end = time.time()
        
        print(f'TEST: {TEST} - Angle: {ang}°')
        print(f'TEST: {TEST} - Attenuation: {att}dB')
        # dat.set_att(att)
        
        time.sleep(run_sleep_time)
        
        att = att + step_att
        
        if att == max_attenuation:
            att = min_attenuation
        
        if (ang + step_ang == 360):
            ang = first_angle
            # print("STEPPER: rotating to home:", ang)
            # stepper0.rotate(ang - step_ang)
            time.sleep(10) # this is needed to let the rotation table coming to home
        else:
            ang = ang + step_ang
        #     print("STEPPER: rotating to:", ang)
        #     stepper0.rotate(-step_ang)
        
    # dev.close()
    # stepper0.close()
        
    