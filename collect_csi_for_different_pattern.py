# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:11:34 2024

@author: Federico Danesin
"""
import time
import sys
import datetime
import os
import numpy as np
import pandas as pd
import broadcom_csimond as bsci
import collect_data_from_board as cdata
import shutil
from csi import *
sys.path.append("//Users/federicodanesin/Desktop/UNIVERSITA/INTERSHIPandTHESIS/Batman")
from adant.decode import read_dump
import pattern_feature as pf
import tensorflow as tf


batman_ip = '192.168.20.1'
ip_server = '192.168.20.36'
ip_client = '192.168.20.9'
mac_address = '28:C2:1F:F6:74:AB'
num_rx_antenna = 4
duration = 10
conf = 10
# pattern = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
pattern = [0,1,2]

# filenames
folder = r'C:\Users\franc\Desktop\Batman'
pattern_features = {}
#%%
for pn in pattern: 
    print(f"test pattern : {pn}")
    save_path = os.path.join(folder,f'test_per_pattern\pattern_id={pn}')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    os.chmod(save_path, 0o777)
    
    dumpname = f'dump_test_pattern={pn}.log'
    cfr_dumpname = f'cfr_dump_test_pattern={pn}.log'
    cfr_extract_name = f'cfr_extract_pattern={pn}.txt'
    cfr_plot_name = f'plot_a_cfr_pattern={pn}'
    iperf_name = f'iperf_test_pattern={pn}.log'
    
    cdata.collect_cfr(batman_ip,ip_server,ip_client,mac_address,duration,pn,folder,dumpname,cfr_dumpname,iperf_name)
    
    #move all the dump in their test directory based on the pattern id used in the test
    dump_destination_path = os.path.join(save_path,dumpname)
    cfr_destination_path = os.path.join(save_path,cfr_dumpname)
    iperf_dump_destination_path = os.path.join(save_path,iperf_name)
    
    shutil.move(os.path.join(folder,dumpname),dump_destination_path)
    shutil.move(os.path.join(folder,cfr_dumpname),cfr_destination_path)
    shutil.move(os.path.join(folder,iperf_name),iperf_dump_destination_path)

    #csi_extractin from row record 
    x = bsci.get_CSI_from_CSI_dump(cfr_destination_path)
    pp = os.path.join(save_path,cfr_extract_name)
    bsci.print_list_on_file(pp,x)
    path_plot = os.path.join(save_path,cfr_plot_name)
    bsci.plot_a_CSI_of_the_record(x,path_plot)
    
    #creazione oggetto pattern feature 
    dump = read_dump(dump_destination_path)
    csi_time = extract_csi_record_timing(x)
    name_obj = f'pattern_feature_id_{pn}'
    pattern_features[name_obj] = pf.Patternfeature(x, csi_time, dump)
    
#%% Load dump already got from the test 
folder= "/Users/federicodanesin/Desktop/UNIVERSITA/INTERSHIPandTHESIS/Batman"
for pn in pattern: 
    print(f"test pattern : {pn}")
    
    save_path = os.path.join(folder,f'test_per_pattern/pattern_id={pn}')
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    os.chmod(save_path, 0o777)
    
    #dumpname 
    dumpname = f'dump_test_pattern={pn}.log'
    cfr_dumpname = f'cfr_dump_test_pattern={pn}.log'
    cfr_extract_name = f'cfr_extract_pattern={pn}.txt'
    cfr_plot_name = f'plot_a_cfr_pattern={pn}'
    iperf_name = f'iperf_test_pattern={pn}.log'
    #path of all the dump
    dump_destination_path = os.path.join(save_path,dumpname)
    cfr_destination_path = os.path.join(save_path,cfr_dumpname)
    iperf_dump_destination_path = os.path.join(save_path,iperf_name)
    #csi_extractin from row record 
    x = bsci.get_CSI_from_CSI_dump(cfr_destination_path) 
    #creazione oggetto pattern feature 
    dump = read_dump(dump_destination_path)
    csi_time = extract_csi_record_timing(x)
    
    matrix_of_the_run = extract_csi_matrix_of_the_run(x,num_rx_antenna)
    name_obj = f'pattern_feature_id_{pn}'
    pattern_features[name_obj] = pf.Patternfeature(pn,matrix_of_the_run,csi_time,dump,mac_address)
    

#%% feature etraction pattern id = 0 

pf0 = pattern_features['pattern_feature_id_0']
pf1 = pattern_features['pattern_feature_id_1']
pf0.decomposition()

cc = pf0.csi_list_abs
mean_cc = np.mean(cc, axis=0)
covariance_matrix = np.cov(cc.reshape(cc.shape[0], -1), rowvar=False)

cov_1 = cc[0,:,:]
cov_2 = cov_1 - np.mean(cov_1)
covariance_matrix = np.cov(cov_2)




pf0.create_tensor()

print (pf0.label_dataset)


for data, label in pf0.label_dataset:
    print(data, label)




#%%

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Caricamento dei dati
# Supponiamo che 'data.csv' sia il tuo file di dati
df = pf0.adant_dump

# Calcolo della matrice di correlazione
correlation_matrix = df.corr()

# Visualizzazione della matrice di correlazione con seaborn
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True)
plt.title('Matrice di Correlazione tra le Feature')
plt.show()











# %%

dataset_list = [dataset_0,dataset_1]
# Combina i dataset utilizzando il metodo concatenate
combined_dataset = dataset_list[0]
for dataset in dataset_list[1:]:
    combined_dataset = combined_dataset.concatenate(dataset)
buffer_size = 10000  # Modifica la dimensione del buffer secondo le tue esigenze
# Permuta casualmente i dati nel dataset combinato
shuffled_dataset = combined_dataset.shuffle(buffer_size)

# Ora puoi utilizzare il dataset per iterare attraverso i dati etichettati
for data, label in shuffled_dataset:
    print(data, label)


def divide_by_magnitude(data, label):
  # Calcola il modulo dei numeri complessi
    magnitude = tf.abs(data)
    # Crea un tensore complesso con modulo fisso e fase 0
    magnitude_complex = tf.complex(magnitude, tf.cast(0.0, tf.float64))
    # Dividi ogni elemento per il suo modulo complesso
    normalized_data = tf.divide(data, magnitude_complex)
    return normalized_data, label

# Applica la funzione a ciascun elemento del dataset
normalized_dataset = shuffled_dataset.map(divide_by_magnitude)

for data, label in normalized_dataset:
    print(data, label)


import tensorflow as tf
from tensorflow.keras import layers, models




# %%
# Number of output classes
Q = 16  # Change this to your number of classes

model = models.Sequential([
    # Assuming the input layer is implicitly defined by the first layer's input shape
    # Let's add a placeholder first layer to represent your 2D inputs X 3 channels
    # Assuming the inputs are of size 32x32 for example, you should adjust this according to your actual input size
    layers.InputLayer(input_shape=(32, 32, 3)),
    
    # 2nd layer: Convolutional Layer
    layers.Conv2D(64, (2, 2), activation='relu', padding='same'),
    
    # 3rd layer: Max-Pooling
    layers.MaxPooling2D((2, 2)),
    
    # 4th layer: Convolutional Layer
    layers.Conv2D(64, (2, 2), activation='relu', padding='same'),
    
    # 5th layer: Max-Pooling
    layers.MaxPooling2D((2, 2)),
    
    # 6th layer: Convolutional Layer
    layers.Conv2D(64, (2, 2), activation='relu', padding='same'),
    
    # Flatten the output of the convolutional layers before feeding into the fully connected layers
    layers.Flatten(),
    
    # 7th layer: Fully Connected Layer with Dropout
    layers.Dense(1024, activation='relu'),
    layers.Dropout(0.5),
    
    # 8th layer: Fully Connected Layer with Dropout
    layers.Dense(1024, activation='relu'),
    layers.Dropout(0.5),
    
    # Output layer with Q units and softmax activation for classification
    layers.Dense(Q, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Summary of the model
model.summary()

from tensorflow.keras.utils import plot_model

# Genera l'immagine del modello
plot_model(model, to_file='modello_cnn.png', show_shapes=True, show_layer_names=True)

labeled_dataset = tf.data.Dataset.zip(dataset, '1')







    
    