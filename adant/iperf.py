#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 12:27:33 2022

@author: riccardo
"""
import os
import re
import subprocess

IPERF3_EXE_PATH=r'C:\Users\franc\Desktop\iperf-3.1.3\iperf3.exe'

def get_throughput(filename):
    with open(filename) as f:
        text = f.read()
    regex = r'^\[SUM\]\s+([\d\.\-]+).*\s(\d+.\d+) Mbits/sec\s+(\w*)\n'
    matches = re.findall(regex, text, re.MULTILINE)
    values = [float(value) for ts, value, key in matches if key == '']
    total = {key : float(value) for ts, value, key in matches if key != ''}
    return text, values, total

def run_speedtest(client_address, duration, parallel='4', filename=None):
    cmd = [IPERF3_EXE_PATH,
    '-c', client_address,
    '-t', str(duration),
    '-P',parallel, '-i','1']
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True, text=True)
    text = p.stdout.read()
    if filename:
        with open(filename, 'w') as f:
            f.write(text)
    return text

def run_speedtest_low_TP(client_address, duration, parallel='1', filename=None):
    cmd = [IPERF3_EXE_PATH,
    '-c', client_address,
    '-t', str(duration),
    '-P',parallel,'-b','2M','-i','1']
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True, text=True)
    text = p.stdout.read()
    if filename:
        with open(filename, 'w') as f:
            f.write(text)
    return text

def run_speedtest_uplink(client_address, duration, parallel='4', filename=None):
    cmd = [IPERF3_EXE_PATH,
    '-c', client_address,
    '-t', str(duration),
    '-P',parallel, '-i','1', '-R']
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True, text=True)
    text = p.stdout.read()
    if filename:
        with open(filename, 'w') as f:
            f.write(text)
    return text

def run_speedtest_udp(client_address, duration, parallel='4', filename=None):
    cmd = [IPERF3_EXE_PATH,
    '-c', client_address,
    '-t', str(duration),
    '-P',parallel, '-i','1', '-p12410','-u','-b0']
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True, text=True)
    text = p.stdout.read()
    if filename:
        with open(filename, 'w') as f:
            f.write(text)
    return text
