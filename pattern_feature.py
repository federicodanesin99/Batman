# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:25:41 2024

@author: Francesco Renga
"""
from csi import *
import numpy as np
import tensorflow as tf

class Patternfeature:
    def __init__(self, pattern_id,csi_list, csi_time, adant_dump,client_mac_address=None):
        self.csi_list = csi_list
        self.csi_time = csi_time
        self.adant_dump = adant_dump
        self.client_mac_address = client_mac_address
        self.pattern_id = pattern_id
        if client_mac_address is not None:
            self.adant_dump = adant_dump[adant_dump['mac'].str.lower() == client_mac_address.lower()]
        
    def decomposition(self):
        self.csi_list_abs = np.abs(self.csi_list)
        self.csi_list_angle = np.angle(self.csi_list)
        return self.csi_list_angle
    
    def create_tensor(self):
        #separa in parte reale e immaginari la csi list e crea un tensore di 
        #dimesione  [2 * n csi raccolte * n antenne * sottoportanti]
        real_part = tf.math.real(self.csi_list)
        imag_part = tf.math.imag(self.csi_list)
        self.separate_csi_list = tf.stack([real_part,imag_part], axis=0)
        
        lab = [self.pattern_id] * (len(self.csi_list))
        # Creare un dataset a partire dal tuo array di etichette
        self.labels = tf.data.Dataset.from_tensor_slices(lab)
        self.data = tf.data.Dataset.from_tensor_slices(self.separate_csi_list)
        label_dataset = tf.data.Dataset.from_tensor_slices((self.separate_csi_list,tf.convert_to_tensor(lab)))
        # funzione di estrazione feature
    