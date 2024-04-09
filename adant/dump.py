#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 15:05:52 2020
Updated on Jan 18 2021

@author: riccardo
"""

import os
import pandas as pd
import numpy as np
from collections import OrderedDict

patterns = ['0x8001',  '0x8003',  '0x8009',  '0x800b',  '0x8021',  '0x8023',
            '0x8029',  '0x802b',  '0x8081',  '0x8083',  '0x8089',  '0x808b',
            '0x80a1',  '0x80a3',  '0x80a9',  '0x80ab']


def find_datafolder(root, loc, angle, direction):
    import os.path
    for x in os.listdir(root):
        if loc != x:
            continue
        locdir = os.path.join(root, loc)
        if not os.path.isdir(locdir):
            continue
        tests = [x for x in os.listdir(
            locdir) if os.path.isdir(os.path.join(locdir, x))]
        print(len(tests), "test found in folder", locdir)

        for testname in tests:
            _, _, ang, d = testname.split("_")

            if ang == "Airgain":
                continue

            if int(ang) != angle:
                continue

            if direction != d:
                continue

            return os.path.join(locdir, testname)
    raise(FileNotFoundError("not found"))
    return None


class DumpFile():

    def __init__(self, folder, dumpname, loadh8=True):
        self.path = os.path.join(folder, dumpname)
        self.folder = folder
        self.dumpname = dumpname

        self.fone = self.read_dump("F1")
        self.gone = self.read_dump("G1")
        self.dx = self.read_dump("D3")
        if (self.dx.empty):
            self.dx = self.read_dump("D4")
        if (loadh8):
            self.heig = self.read_dump("H8")
       # self.train = self.read_dump("TR")
        self.u2 = self.read_dump("U2")
        # RX dump
        #self.rxdu = self.read_rxdump_u2()

    def read_rxdump(self):

        def classify(row, k): return {
            "tag": str(row[0]),
            'ts': int(row[1]),
            'mac': str(row[2]),
            'bw': int(row[3]),
            'ratecode': int(row[4]),
            'antenna': k,
            'evm': [int(x) for x in row[7:7+32]],
            'rssi': np.reshape([int(x) for x in row[40:40+56]], (8, 7)),
            'nframes': int(row[-1])
        }

        code = np.nan
        rows = []
        with open(self.path) as f:
            for line in f.readlines():
                if line.startswith("H8"):
                    code = line.split(",")[6]
                elif line.startswith("U1"):
                    row = line.rstrip().split(',')
                    try:
                        rows.append(classify(row, code))
                    except ValueError:
                        print(row)
        return pd.DataFrame(rows)

    def read_rxdump_u2(self):
        print("dsabhcsagksafdjg")
        import numpy as np

        def classify(row): return {
            "tag": str(row[0]),
            'ts': np.int64(row[1]),
            'mac': str(row[2]),
            'bw': np.int64(row[3]),
            'ratecode': np.int64(row[4]),
            'antenna': row[5],
            'nframes': np.int64(row[6]),
            'rssi': np.reshape([np.int64(x) for x in row[8:8+56]], (8, 7)),
        }
        with open(self.path) as f:
            lines = [line.rstrip().split(',') for line in f.readlines()
                     if line.startswith('U2')]
        rows = []
        for row in lines:
            try:
                rows.append(classify(row))
            except ValueError:
                print(row)

        return pd.DataFrame(rows)

    @staticmethod
    def parselines(filename, tag, coltypes):
        header = list(coltypes.keys())
        with open(filename) as f:
            lines = [line.rstrip().split(',')
                     for line in f.readlines() if line.startswith(tag)]
            df = pd.DataFrame(lines, columns=header).astype(coltypes)
        return df



    def read_dump(self, tag):
            
        if tag == "D5":
            coltypes = OrderedDict(
                {'tag': "string",
                 'ts': 'int64',
                 "mac": "string",
                 'tid': 'int64',
                 "code": "string",
                 'nfb': 'int64',
                 'nframes': 'int64',
                 "bitrate": 'int64',
                 "through": 'int64',
                 "ngood": 'int64',
                 "r0": "int64", "r1": "int64", "r2": "int64", "r3": "int64",
                 "value": "int64",
                 "nfeedback": 'int64',
                 'ts_min': 'int64',
                 'duration_ms': 'int64',
                 'feedback_rate': 'int64',
                 'cfun': 'int64',
                 'cfunmulti': 'int64'
                 })
            return DumpFile.parselines(self.path, tag, coltypes)

        if tag == "F1":
            dtype = OrderedDict(
                {'tag': str, 'ts': "int64", "mac": str,
                 "ai": "int64", 'fcost': "int64", 'retries': "int64",
                 "bdw": "int64", "nsample": "int64",
                 'h1': "int64", "h2": "int64", "h3": "int64",
                 'hfunc': "int64"})

            with open(self.path) as f:
                lines = [line.rstrip().split(',') for line in f.readlines()
                         if line.startswith(tag)]
            df = pd.DataFrame(lines, columns=dtype.keys()).astype(dtype)
            return df

        elif tag == "D3":
            dtype = OrderedDict(
                {'tag': str, 'ts': "int64", "mac": str, "code": str,
                 'nfb': "int64", 'nframes': "int64", "bitrate": "int64", "nbad": "int64",
                 'len': "int64", 'bw': int, "r0": int, "r1": int,
                 "r0": int, "r1": int, "r2": int, "r3": int,
                 'trh': str, "value": "int64", "samples": "int64", 'ar1': int,
                 'cfun': "int64"})

            with open(self.path) as f:
                lines = [line.rstrip().split(',') for line in f.readlines()
                         if line.startswith(tag)]
            df = pd.DataFrame(lines, columns=dtype.keys()).astype(dtype)

            # post
            df['through'] = [int(x, 16) for x in df['trh']]
            df = df.drop(columns="trh")
            return df

        elif tag == "G1":

            header = ["tag", "ts", "radio", "ai", "ai2", "code", "sample",
                      "done", "hfun", "tstamp1"]
            dtypes = [str, "int64", str, "int64", "int64", str,
                      "int64", "int64", "int64", "int64"]

            dtype = OrderedDict(zip(header, dtypes))

            with open(self.path) as f:
                lines = [x.rstrip().split(',')
                         for x in f.readlines() if x.startswith(tag)]
            df = pd.DataFrame(lines, columns=dtype.keys()).astype(dtype)
            df = df.drop(columns="ai2")
            return df

        elif tag == 'TR':
            coltypes = OrderedDict(
                {'tag': "string",
                 'mac': "string",
                 "ntrain": "int32",
                 "duration": "int32",
                 # "training_mode": "int32",
                 'code': "string",
                 "nfeedbacks": "int32"})
            header = list(coltypes.keys())
            with open(self.path) as f:
                lines = [line.rstrip().split(',')
                         for line in f.readlines() if line.startswith("TR")]
                df = pd.DataFrame(lines, columns=header).astype(coltypes)
            return df

        elif tag == "H8":
        
            # header = ['tag', 'ts', 'mac', 'nframes', 'nbad', 'bw', 'code', 'ratecode', 
            #   'xtries', 'bitrate', 'sr', 'through', 'y',
            #   'r0', 'r1', 'r2', 'r3', 'ar1', 'ar2']
            dtype = {'tag': "string",
                     'ts': "int64",
                     'mac': "string",
                     'nframes': "int",
                     'nbad': "int",
                     'bw': "int",
                     'code': "string",
                     'ratecode': "string",
                     'xtries': "int",
                     'bitrate': "string",
                     'sr': "int",
                     'through': "int",
                     'y': "int64",
                     'r0': "int",
                     'r1': "int",
                     'r2': "int",
                     'r3': "int",
                     'ar1': "int64",
                     'ar2': "int64"}
            
            return DumpFile.parselines(self.path, tag, dtype)

            # with open(self.path) as f:
            #     lines = [line.rstrip().split(',') \
            #              for line in f.readlines() \
            #                  if line.startswith(tag)]
            #     df = pd.DataFrame(lines, columns=header).astype(dtype)
        
            # return df
            
             

        elif tag == "U2":

            header = ['tag', 'ts', 'mac', 'bw',
                      'mcs', 'nss', 'code', 'npackets']

            dtype = {'tag': str, 'ts': "int64",
                     'bw': "int64", "mcs": "int64",
                     'nss': "int64", 'npackets': "int64"}

            with open(self.path) as f:
                lines = [line.rstrip().split(',')
                         for line in f.readlines() if line.startswith("U2")]
                df = pd.DataFrame(lines, columns=header).astype(dtype)

            return df

        elif tag == "U2":

            header = ['tag', 'ts', 'mac', 'bw',
                      'mcs', 'nss', 'code', 'npackets']

            dtype = {'tag': str, 'ts': "int64",
                     'bw': "int64", "mcs": "int64",
                     'nss': "int64", 'npackets': "int64"}

            with open(self.path) as f:
                lines = [line.rstrip().split(',')
                         for line in f.readlines() if line.startswith("U2")]
                df = pd.DataFrame(lines, columns=header).astype(dtype)

            return df

        return None


class CsvFile():

    def __init__(self, folder, csvname):
        self.path = os.path.join(folder, csvname)
        self.folder = folder
        self.csvname = csvname
        self.ai = int(self.csvname.split("_")[1])
        self.detail = self.load_details()
        self.traces = None

    def traces_save(self, tracename):
        tfile = os.path.join(self.folder, tracename)
        np.savez(tfile, self.traces)

    def traces_load(self, tracename):
        tfile = os.path.join(self.folder, tracename + ".npz")
        self.traces = np.load(tfile)
        return self.traces

    def get_avg_throughput(self, group_name="All Pairs"):
        from io import StringIO

        with open(self.path) as f:
            lines = f.readlines()
            m = [n for n, line in enumerate(
                lines) if "GROUP AVERAGES" in line][0]
            groups = pd.read_csv(StringIO("".join(lines[m+1:])))
            avgs = groups[groups['Group Name'] ==
                          group_name]['Throughput Avg.(Mbps)']
            value = avgs.array[0]
        return value

    def load_details(self):
        with open(self.path) as f:
            for n, line in enumerate(f):
                if "ENDPOINT PAIR DETAILS" in line:
                    a = n
                if "GROUP AVERAGES" in line:
                    b = n
        k = list(range(0, a + 1)) + list(range(b - 1, n + 1))
        df = pd.read_csv(self.path, skiprows=k)

        drop_columns = [
            label for label in df.columns if df[label].isna().all()]
        df = df.drop(columns=drop_columns)
        df['Payload'] = df['Throughput (Mbps)'] * df['Measured Time (sec)']
        return df

    def get_avg_throughput_omit(self, omit_seconds=15):
        df = self.detail
        total_size = df[df['Elapsed Time (sec)']
                        >= omit_seconds]['Payload'].sum()
        duration = df['Elapsed Time (sec)'].max() - omit_seconds
        throughput_omit = total_size / duration
        return throughput_omit

    def get_xy(self, step=0.5):
        import numpy as np
        k = self.detail
        amin = np.round(k['Elapsed Time (sec)'].min())
        amax = np.round(k['Elapsed Time (sec)'].max())

        y = []
        x = np.arange(amin, amax, step)
        for ts in x:
            values = k[k['Elapsed Time (sec)'].between(
                ts, ts + step)]['Payload']
            y.append(values.sum() / step)

        return x, y

    def get_xy2(self, step=0.1):
        import numpy as np
        k = self.detail

        k['a'] = k['Elapsed Time (sec)'] - k['Measured Time (sec)']

        amax = np.round(k['Elapsed Time (sec)'].max())
        amin = np.round(k['a'].min())
        x = np.arange(amin, amax, step)

        #k['b'] = k['Elapsed Time (sec)']

        y = [k[(k['a'] <= ts) & (ts < k['Elapsed Time (sec)'])]
             ['Throughput (Mbps)'].sum() for ts in x]

        # remove zeros
        v = [(a, b) for a, b in zip(x, y) if b > 0]
        return list(zip(*v))

        # return x, y, v

    def thorughputs_xy(self, direction='To', astep=0.005):
        import numpy as np

        self.detail['a'] = self.detail['Elapsed Time (sec)'] - \
            self.detail['Measured Time (sec)']

        amax = np.round(self.detail['Elapsed Time (sec)'].max())
        amin = np.round(self.detail['a'].min())

        self.traces = {}

        def _get_sumtp_at_ts(df, u): return df[(df['a'] <= u) & (
            u < k['Elapsed Time (sec)'])]['Throughput (Mbps)'].sum()

        self.detail['peer'] = self.detail[direction]

        for user in self.detail['peer'].unique():
            k = self.detail[self.detail['peer'] == user].copy()
            x = np.arange(amin, amax, astep)
            y = [_get_sumtp_at_ts(k, ts) for ts in x]
            self.traces[user] = (x[1:], y[1:])

        return self.traces


class DumpSet():

    def __init__(self, folder):
        self.root = folder
        # CSV filenames in the folder
        # and read throughput dataframes
        names = [x for x in os.listdir(self.root) if
                 x.endswith(".csv")]
        self.csvnames = sorted(names)
        self.csvs = [CsvFile(self.root, csvname) for csvname in self.csvnames]

        self.tpdf = self.read_throughput()
        # read dump
        self.dumpnames = self.get_dumpnames()
        self.dumps = [DumpFile(self.root, dn) for dn in self.dumpnames]

    def get_dumpnames(self):
        p = self.root
        e = [x for x in os.listdir(p) if x.startswith(
            "dump") and x.endswith(".log")]
        dumpnames = sorted(e)
        print(len(dumpnames), "dump found in", self.root)
        return dumpnames

    def get_rawdata(self, ai):
        """ Raw data is the .log dump that does not contain _in nor _fin"""
        raws = pd.concat(
            [d.heig for d in self.dumps if not "in" in d.dumpname])
        code = patterns[ai]
        return raws[raws['code'] == code]

    def get_traindata(self, ai):
        raws = pd.concat([d.heig for d in self.dumps if "in" in d.dumpname])
        code = patterns[ai]
        return raws[raws['code'] == code]

    def get_rawdata_valid(self, ai, k=1):
        raw = self.get_rawdata(ai)
        lower_limit = raw.ar1.mean() - (k * raw.ar1.std())
        x = raw[raw['ar1'] >= lower_limit].index.tolist()
        a, b = x[0], x[-1]-1
        return raw.loc[a:b]

    def read_throughput(self):
        rows = []
        for csv in self.csvs:
            rows.append({"ai":   csv.ai,
                         "value": csv.get_avg_throughput(),
                         "name":  csv.csvname})

        return pd.DataFrame(rows)
