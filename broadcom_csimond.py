# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:29:10 2024

@author: riccardo.bersan
"""

import ctypes
import numpy as np


def hex_words_to_bytes(text):
    """Converts space-separated hexadecimal words (with optional 0x prefix) to a byte string."""
    import struct

    hex2int = lambda word: int(word[2:], 16) if word.startswith("0x") else int(word, 16)
    hex_words = (hex2int(word) for word in text.split())
    return b"".join(struct.pack("<I", i) for i in hex_words)


# typedef struct wlc_csimon_hdr {
class wlc_csimon_hdr(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        # uint32 format_id; /* id / version for the CSI report format */
        ("format_id", ctypes.c_uint32),
        # uint16 client_ea[3]; /* client MAC address: 3 16-bit words */
        ("client_ea", ctypes.ARRAY(ctypes.c_uint8, 6)),
        # uint16 bss_ea[3]; /* BSS address: 3 16-bit words */
        ("bss_ea", ctypes.ARRAY(ctypes.c_uint8, 6)),
        # chanspec_t chanspec; /* band, channel, bandwidth */
        ("chanspec", ctypes.c_uint16),
        # uint8 txstreams; /* number of tx spatial streams*/
        ("txstreams", ctypes.c_uint8),
        # uint8 rxstreams; /* number of rx spatial streams */
        ("rxstreams", ctypes.c_uint8),
        # uint32 report_ts; /* CSI Rx TSF timer timestamp */
        ("report_ts", ctypes.c_uint32),
        # uint32 assoc_ts; /* client association timestamp */
        ("assoc_ts", ctypes.c_uint32),
        # int8 rssi[4]; /* RSSI for each rx chain: 2’s complement, ‘dB’ resolution */
        ("rssi", ctypes.ARRAY(ctypes.c_int8, 4)),
        # 32 bytes zero padding
        ("_pad", ctypes.ARRAY(ctypes.c_int8, 32)),
    ]

    def __str__(self):
        mac = ":".join([f"{a:02x}" for a in self.client_ea])
        bss = ":".join([f"{a:02x}" for a in self.bss_ea])
        return (
            f"format_id: {self.format_id}\n"
            f"client_ea: {mac}\n"
            f"bss_ea   : {bss}\n"
            f"chanspec : {hex(self.chanspec)}\n"
            f"txstreams: {self.txstreams}\n"
            f"rxstreams: {self.rxstreams}\n"
            f"report_ts: {self.report_ts} microseconds\n"
            f"assoc_ts : {self.assoc_ts} microseconds\n"
            f"rssi     : {[a for a in self.rssi]}\n"
        )


class wlc_csimon_phy_header(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("phy_cfg", ctypes.ARRAY(ctypes.c_uint8, 16)),
        ("phy_cfg2", ctypes.ARRAY(ctypes.c_int8, 16)),
    ]

    def __str__(self):
        return (
            f"phy_cfg: {[hex(a) for a in self.phy_cfg]}\n"
            f"phy_cfg: {[(a) for a in self.phy_cfg]}\n"
            f"oth: {[hex(a) for a in self.phy_cfg2]}\n"
        )


class wlc_csimon_tone(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("imag", ctypes.c_int16), ("real", ctypes.c_int16)]

    def to_numpy(self):
        return self.real + (1j * self.imag)

    def __repr__(self):
        return f"{self.to_numpy()}"


IQ_SAMPLE_SIZE = 4  # bytes
MAX_NUM_IQ_SAMPLES = (2048 - 64 - 32) // IQ_SAMPLE_SIZE


class wlc_csimon_record(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("csi_header", wlc_csimon_hdr),
        ("phy_header", wlc_csimon_phy_header),
        ("phy_paylaod", ctypes.ARRAY(wlc_csimon_tone, MAX_NUM_IQ_SAMPLES)),
    ]

    def __init__(self, text=None):
        pass

    def __new__(self, text=None):
        buffer = hex_words_to_bytes(text)
        return self.from_buffer_copy(buffer)

    def __str__(self):
        return (
            f"> csi_header:\n{self.csi_header}\n"
            f"> phy_header:\n{self.phy_header}\n"
            f"> phy_paylaod:\n {[a for a in self.phy_paylaod]}\n"
        )


class wlc_csimon_record_bytes(wlc_csimon_record):
    def __init__(self, bytes=None):
        pass

    def __new__(self, bytes=None):
        return self.from_buffer_copy(bytes)


# %%
def split_log_into_CSI_records(text):
    samples = [""]
    for line in text.splitlines():
        if "CSI record:" in line:
            samples.append("")
        else:
            samples[-1] += line
    return samples

# %%
def print_list_on_file(file_path,my_list):
    with open(file_path, 'w') as file:
        for item in my_list:
            file.write(str(item) + '\n')
#%%

def read_list_from_file(file_path):
    my_list = []
    with open(file_path, 'r') as file:
        for line in file:
            my_list.append(line.strip())
    return my_list


# %%%%%%%%
def get_CSI_from_CSI_dump(path_csi):
    # filename = r"C:\Users\franc\Desktop\Batman\cfr_dump_test0.log"
    filename = path_csi
    with open(filename) as f:
        text = f.read()
    
    samples = split_log_into_CSI_records(text)
    samples = samples[:-1]
    xs = []
    
    for num, sample_text in enumerate(samples):
        if not sample_text.startswith("0x"):
            continue
    
        # Constructor
        x = wlc_csimon_record(sample_text)
    
        # obj = wlc_csimon_record_bytes(x)
    
        #print(x)
        xs.append(x)
    return xs
#%%
import matplotlib.pyplot as plt
# nsamples = 480//2


# def rms(a, b):
#     return np.abs(np.sqrt(np.mean((a - b)**2)))
#     #return np.abs(np.sqrt(np.mean((a - b)))

# ps = []
# for n in range(len(xs)):
#     x = xs[0]
#     v1 = np.array([a.to_numpy() for a in x.phy_paylaod][:nsamples])    
#     x = xs[n]
#     #print(x.csi_header)
#     v2 = np.array([a.to_numpy() for a in x.phy_paylaod][:nsamples])    
#     p = rms(v1, v2)
#     ps.append(p)

# plt.plot(ps)
# %%

def plot_a_CSI_of_the_record(csi_record,save_path):
    plt.close("all")
    
    #plt.plot(np.absolute(v))
    
    fig, axes = plt.subplot_mosaic("AB;AC")
    
    num_antennas = 4
    ntones = 256
    
    
    calibration = {}
    v = [a.to_numpy() for a in csi_record[0].phy_paylaod]
    for antenna_index in range(num_antennas):
        vn = v[antenna_index::num_antennas]
        vn = vn[:ntones]
        calibration[antenna_index] = vn
    
    for sample_index, x in enumerate(csi_record):
        v = [a.to_numpy() for a in x.phy_paylaod]
    
        for antenna_index in range(num_antennas):
            vn = v[antenna_index::num_antennas]
            vn = vn[:ntones]
    
            # calvec = calibration[antenna_index]
    
            # pn = np.divide(vn,  calvec)
            pn = vn
    
            axes["A"].plot(np.absolute(pn), "-x", label=f"antenna-{antenna_index}")
            axes["B"].plot(np.angle(pn), "-x", label=f"antenna-{antenna_index}")
            axes["C"].plot(np.unwrap(np.angle(pn)), "-x")
    
        plt.legend()
        plt.suptitle(f"Sample index {sample_index}")
        
        #save image
        plt.savefig(save_path)
        plt.close(fig)
        break
    
        plt.pause(5)

# %%

# from scipy import optimize

# fig, axes = plt.subplot_mosaic("A;B;C")

# # k = np.pi / 4

# fc = np.arange(len(pn))


# # qx =
# v


# # funzione da minimizzare
# def x(k):
#     return np.sum(
#         np.power(
#             (np.angle(pn[:60]) - np.angle(np.exp(-1j * k * fc[:60])) - np.angle(pn[0])),
#             2,
#         )
#     )

#     #       (np.multiply(((2*math.pi * f_delta * tau)+epsilon), matrix_n)), 2))


# f_min = optimize.fmin(func=x, x0=[np.pi / 4], maxiter=40000, disp=True)


# qx = np.exp(-1j * f_min[0] * fc + 1j * np.angle(pn[0]))


# axes["A"].plot(np.absolute(pn[:100]), "-x", label=f"antenna-{antenna_index}")
# axes["B"].plot(np.angle(qx), "-x", label=f"antenna-{antenna_index}")
# axes["B"].plot(np.angle(pn), "-x", label=f"antenna-{antenna_index}")
# axes["C"].plot(np.angle(pn / qx), "-x", label=f"antenna-{antenna_index}")

# %%
# path = r'C:\Users\franc\Desktop\Batman\test_per_pattern\pattern_id=0\cfr_dump_test_pattern=0.log'
# x = get_CSI_from_CSI_dump(path)

# pppp =  plot_a_CSI_of_the_record(x,r'C:\Users\franc\Desktop\Batman\test_per_pattern')




