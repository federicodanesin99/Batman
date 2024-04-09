#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 14:44:50 2022

@author: riccardo
"""
import ctypes
import pandas as pd


MCSSET_LEN = 16
WL_MAXRATES_IN_SET = 16
WL_VHT_CAP_MCS_MAP_NSS_MAX = 8
WL_HE_CAP_MCS_MAP_NSS_MAX = 8
WL_STA_ANT_MAX = 4
WL_MAX_BAND = 8
WLC_MAX_ASSOC_OUI_NUM = 6
DOT11_OUI_LEN = 3
DOT11_RRM_CAP_LEN = 5


class wl_rateset_t(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_uint32),
        # rates in 500kbps units w/hi bit set if basic
        ("rates", ctypes.c_uint8 * 16),
    ]


class wl_rateset_args_v2_t(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint16),
        ("len", ctypes.c_uint16),
        ("count", ctypes.c_uint32),
        ("rates", ctypes.c_uint8 * WL_MAXRATES_IN_SET),
        ("mcs", ctypes.c_uint8 * MCSSET_LEN),
        ("vht_mcs", ctypes.c_uint16 * WL_VHT_CAP_MCS_MAP_NSS_MAX),
        ("he_mcs", ctypes.c_uint16 * WL_HE_CAP_MCS_MAP_NSS_MAX)
    ]


class adant_station_stats(ctypes.Structure):
    _fields_ = [
        ("ver", ctypes.c_uint16),
        ("len", ctypes.c_uint16),
        ("cap", ctypes.c_uint16),
        ("flags", ctypes.c_uint32),
        ("idle", ctypes.c_uint32),
        ("rateset", wl_rateset_t),
        ("in", ctypes.c_uint32),
        ("listen_interval_inms", ctypes.c_uint32),
        ("tx_pkts", ctypes.c_uint32),
        ("tx_failures", ctypes.c_uint32),
        ("rx_ucast_pkts", ctypes.c_uint32),
        ("rx_mcast_pkts", ctypes.c_uint32),
        ("tx_rate", ctypes.c_uint32),
        ("rx_rate", ctypes.c_uint32),
        ("rx_decrypt_succeeds", ctypes.c_uint32),
        ("rx_decrypt_failures", ctypes.c_uint32),
        ("tx_tot_pkts", ctypes.c_uint32),
        ("rx_tot_pkts", ctypes.c_uint32),
        ("tx_mcast_pkts", ctypes.c_uint32),
        ("tx_tot_bytes", ctypes.c_uint64),
        ("rx_tot_bytes", ctypes.c_uint64),
        ("tx_ucast_bytes", ctypes.c_uint64),
        ("tx_mcast_bytes", ctypes.c_uint64),
        ("rx_ucast_bytes", ctypes.c_uint64),
        ("rx_mcast_bytes", ctypes.c_uint64),
        ("rssi", ctypes.c_int8 * WL_STA_ANT_MAX),
        ("nf", ctypes.c_int8 * WL_STA_ANT_MAX),
        ("aid", ctypes.c_uint16),
        ("ht_capabilities", ctypes.c_uint16),
        ("vht_flags", ctypes.c_uint16),
        ("tx_pkts_retried", ctypes.c_uint32),
        ("tx_pkts_retry_exhausted", ctypes.c_uint32),
        ("rx_lastpkt_rssi", ctypes.c_int8 * WL_STA_ANT_MAX),
        ("tx_pkts_total", ctypes.c_uint32),
        ("tx_pkts_retries", ctypes.c_uint32),
        ("tx_pkts_fw_total", ctypes.c_uint32),
        ("tx_pkts_fw_retries", ctypes.c_uint32),
        ("tx_pkts_fw_retry_exhausted", ctypes.c_uint32),
        ("rx_pkts_retried", ctypes.c_uint32),
        ("tx_rate_fallback", ctypes.c_uint32),
        ("rx_dur_total", ctypes.c_uint32),
        ("chanspec", ctypes.c_uint16),
        ("rateset_adv", wl_rateset_args_v2_t),
        ("algo", ctypes.c_uint8),
        ("tx_rspec", ctypes.c_uint32),
        ("rx_rspec", ctypes.c_uint32),
        ("wnm_cap", ctypes.c_uint32),
        ("he_flags", ctypes.c_uint32),
        ("link_bw", ctypes.c_uint8),
        ("wpauth", ctypes.c_uint32),
        ("srssi", ctypes.c_int8),
        ("twt_info", ctypes.c_uint8),
        ("omi", ctypes.c_uint16),
        ("tx_mgmt_pkts", ctypes.c_uint32),
        ("tx_ctl_pkts", ctypes.c_uint32),
        ("rx_mgmt_pkts", ctypes.c_uint32),
        ("rx_ctl_pkts", ctypes.c_uint32),
        ("rrm_capabilities", ctypes.c_uint8 * DOT11_RRM_CAP_LEN),
        ("PAD", ctypes.c_uint8),
        ("map_flags", ctypes.c_uint16),
        ("bands", ctypes.c_uint8 * WL_MAX_BAND),
        ("eht_flags", ctypes.c_uint32),
        ("tx_acked_pkts", ctypes.c_uint32),
    ]


def read_dump(filename):
    """
    This functions reads an adant-dump file from a Charter-Broadcom dump.

    Parameters
    ----------
    filename : string
        Full path of the dump file.

    Returns
    -------
    pandas.DataFrame

    """

    def process_B1_dumpline(line):
        tag, ts, mac, raw = line.split(",")
        rawbytes = bytes.fromhex(raw)

        row = {'tag': tag,
               'ts': int(ts),
               'mac': mac}
        try:
            data = adant_station_stats.from_buffer_copy(rawbytes)
        except ValueError:
            print("Buffer size too small: skip dump line")
            return row

        for field, field_type in adant_station_stats._fields_:
            # FIXME: rateset_adv field is ignored
            if field == 'rateset_adv':
                continue
            # FIXME: rateset field is ignored
            if field == 'rateset':
                continue
            if "Array" in str(field_type):
                value = list(getattr(data, field))
            else:
                value = getattr(data, field)
            row[field] = value
        return row



    def process_B2_dumpline(line):
        # tag, ant, ts, mac, mcs, nss, raw = line.split(",")
        tag, ant, ts, mac, raw = line.split(",")
        rawbytes = bytes.fromhex(raw)

        row = {'tag': tag,
               'conf': int(ant),
               'ts': int(ts),
               'mac': mac}
               # 'mcs': int(mcs),
               # 'nss':int(nss)}
        try:
            data = adant_station_stats.from_buffer_copy(rawbytes)
        except ValueError:
            print("Buffer size too small: skip dump line")
            return row

        for field, field_type in adant_station_stats._fields_:
            # FIXME: rateset_adv field is ignored
            if field == 'rateset_adv':
                continue
            # FIXME: rateset field is ignored
            if field == 'rateset':
                continue
            if "Array" in str(field_type):
                value = list(getattr(data, field))
            else:
                value = getattr(data, field)
            row[field] = value
        return row
    
    def process_M1_dumpline(line):
        tag, ant, ts, mac, tx_rate, mcs, nss = line.split(",")
        # tag, ant, ts, mac, tx_rate = line.split(",")

        row = {'tag': tag,
               'conf': int(ant),
               'ts': int(ts),
               'mac': mac,
               'tx_rate': int(tx_rate),
               'mcs': int(mcs),
               'nss':int(nss)}

        return row
    
    

    def process_dumptext(text):
        rows = []
        for line in text.splitlines():
            if line.startswith("B1"):
                row = process_B1_dumpline(line)
                rows.append(row)
            elif line.startswith("B2"):
                row = process_B2_dumpline(line)
                rows.append(row)
            elif line.startswith("M1"):
                row = process_M1_dumpline(line)
                rows.append(row)
            else:
                continue
            
        return pd.DataFrame(rows)

    with open(filename) as f:
        text = f.read()
    return process_dumptext(text)
