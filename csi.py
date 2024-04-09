# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:29:10 2024

@author: Federico Danesin
"""

import matplotlib.pyplot as plt
import ctypes
import numpy as np
import os
import sys
sys.path.append(r"C:\Users\franc\Desktop\Batman")
from broadcom_csimond import*

# %%
# n_good_tones = 256
# num_antennas = 4

def get_bandwidth(chanspec):
    chspec_bw_mhz = {0:0, 1:0, 2:20, 3:40, 4:80, 5:160, 6:320, 7:0}
    mask = 0x3800
    sr = 11
    index = (chanspec & mask) >> sr  
    return chspec_bw_mhz[index]
    
def get_good_tones(bandwidth):
    bw_good_tones = {20:10, 40:20, 80:60, 160:120, 320:240}
    return bw_good_tones[bandwidth]

def extract_csi_matrix(num_antennas,good_tones,record):
    CSI_rows = []
    v = [a.to_numpy() for a in record.phy_paylaod]
    for antenna_index in range(num_antennas):
        vn = v[antenna_index::num_antennas]
        vn = vn[:good_tones]
        CSI_rows.append(vn)
    csi = np.array(CSI_rows)
    return csi

def extract_csi_matrix_of_the_run(list_record,num_antennas):
    csi_list = []
    n_good_tones = get_good_tones(get_bandwidth(list_record[0].csi_header.chanspec))
    for record in list_record :
        csi_curr =  extract_csi_matrix(num_antennas,n_good_tones,record)
        csi_list.append(csi_curr)
    return csi_list

# return the time of each CSI record extracted  
def extract_csi_record_timing(list_record):
    time = []
    init_t = list_record[0].csi_header.report_ts
    for record in list_record :
        t_curr = record.csi_header.report_ts - init_t
        time.append(t_curr)
    return time

def get_module_of_csi_of_the_run(csi_list):
    abs_csi = [abs(x) for x in csi_list]
    return abs_csi
    

# %%

# # plot module of a subcarrier over time

# index_subcarrier = 30
# index_antenna = 1

# magnitude_subcarrier = []
# for csi in csi_list :
#     magnitude_subcarrier.append(abs(csi[index_antenna,index_subcarrier]))
    


# # Convert milliseconds to seconds for the time values
# time_seconds = [t / 1e7 for t in time]

# # Plot time vs. magnitude_subcarrier
# plt.plot(time_seconds, magnitude_subcarrier, marker='o', linestyle='-')
# plt.xlabel('Time (seconds)')
# plt.ylabel('Magnitude Subcarrier')
# plt.title('Magnitude of Subcarrier {} over Time'.format(index_subcarrier))
# plt.grid(True)


# plt.show()


# # Plot magnitude of subcarrier for each antenna index
# fig, axs = plt.subplots(4, 1, figsize=(8, 10))
# magnitude_data = []
# for i in range(4):
#     magnitude_antenna = [abs(csi[i, index_subcarrier]) for csi in csi_list]
#     magnitude_data.append(magnitude_antenna)
#     axs[i].plot(time_seconds, magnitude_antenna, marker='o', linestyle='-', label='Antenna {}'.format(i+1))
#     axs[i].set_xlabel('Time (seconds)')
#     axs[i].set_ylabel('Magnitude Subcarrier')
#     axs[i].set_title('Magnitude of Subcarrier {} for Antenna {}'.format(index_subcarrier, i+1))
#     axs[i].grid(True)
#     axs[i].set_yscale('log')
#     axs[i].legend()
    

# plt.tight_layout()
# plt.show()

# # Calculate correlation matrix
# correlation_matrix = np.corrcoef(magnitude_data)

# # Print correlation matrix
# print("Correlation Matrix:")
# print(correlation_matrix)

# # Plot the heatmap
# # plt.imshow(correlation_matrix, cmap='hot', interpolation='nearest')
# # plt.colorbar()  # Add color bar to show the scale
# # plt.title('Correlation Heatmap')
# # plt.xlabel('Antenna Index')
# # plt.ylabel('Antenna Index')
# # plt.show()

# import seaborn as sns
# heatmap = sns.heatmap(correlation_matrix, annot=True)
# heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':12}, pad=12)


# # %%
# from sklearn.preprocessing import StandardScaler
# from sklearn.decomposition import PCA

# scaler = StandardScaler().fit(csi)


# def normalizza_csi(csi):
#     norme_righe = np.linalg.norm(csi, axis=1, keepdims=True)
#     csi_normalizzata = csi / norme_righe
#     return csi_normalizzata


# csi_normalizzata = normalizza_csi(csi)

# plt.figure(figsize=(10, 6))
# plt.plot(np.abs(csi.flatten()), label='CSI Originale')
# plt.plot(np.abs(csi_normalizzata.flatten()), label='CSI Normalizzata')
# plt.xlabel('Indice')
# plt.ylabel('Valore')
# plt.title('Valori di CSI Originale e Normalizzata')
# plt.legend()
# plt.grid(True)
# plt.show()


# import numpy as np
# from sklearn.decomposition import PCA


# csi_run_p0 = extract_csi_matrix_of_the_run(n_good_tones,xs_1)

# csi_run_p15 = extract_csi_matrix_of_the_run(n_good_tones,xs_2)


# csi_run_p0 = csi_run_p0[:30]
# csi_run_p15 =csi_run_p15[:30]


# # Creare un insieme di dati fittizio
# # Sostituisci questo con i tuoi dati
# data_1 =csi_run_p0[0]
# data_2 = csi_run_p15[0]
# # Inizializzare l'oggetto PCA
# pca = PCA(n_components=2)  # Utilizzare due componenti principali per la visualizzazione

# # Inizializzare l'oggetto PCA
# pca = PCA(n_components=2)  # Utilizzare due componenti principali per la visualizzazione

# # Addestrare il modello PCA sui dati 1 e trasformarli nello spazio delle componenti principali
# transformed_data_1 = pca.fit_transform(data_1)

# # Addestrare il modello PCA sui dati 2 e trasformarli nello spazio delle componenti principali
# transformed_data_2 = pca.fit_transform(data_2)

# # Tracciare i punti nel piano delle prime due componenti principali
# plt.figure(figsize=(8, 6))
# plt.scatter(transformed_data_1[:, 0], transformed_data_1[:, 1], c='r', label='Data 1')
# plt.scatter(transformed_data_2[:, 0], transformed_data_2[:, 1], c='b', label='Data 2')
# plt.title('Visualizzazione delle prime due componenti principali')
# plt.xlabel('Prima componente principale')
# plt.ylabel('Seconda componente principale')
# plt.legend()
# plt.grid(True)
