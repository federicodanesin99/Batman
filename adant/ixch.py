# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:21:01 2023

@author: emanu
"""
import os.path
import time
from datetime import datetime
import subprocess
import numpy as np
import csv
# ixia test

class IxiaLauncher():
    
    def __init__(self):
        path = r"C:\Program Files (x86)\Ixia\IxChariot"
        
        if os.path.isfile(os.path.join(path, "runtst.exe")):
            self._runtst = os.path.join(path, "runtst.exe")
        
        if os.path.isfile(os.path.join(path, "fmttst.exe")):
            self._fmttst = os.path.join(path, "fmttst.exe")
        
    def run(self, filename, output_dir, timeout=None,
            verbose=False, echo=True):
        """Run the test specified in filename"""
        # RUNTST test_filename [new_test_filename] [-t N] [-v]
        #
        #  "test_filename" is the IxChariot test file to run.  
        #  If a "new_test_filename"  is provided, the test setup and results are saved to this new file;
        #  otherwise, results are saved to test_filename.
        #
        #  The optional -t parameter tells RUNTST to stop a running test after
        #  N seconds.  N can be in the range from 1 to 99999 seconds.
        #
        #  The optional -p parameter tells RUNTST to poll to M interval minutes.
        #  M can be in the range from 1 to 60 minutes. This way you can see if endpoint
        #  is still up.
        #
        #  The optional -v parameter tells RUNTST to run in verbose mode.  Verbose
        #  mode causes RUNTST to display all run information to standard out as it
        #  is received
        
        if not os.path.isdir(output_dir):
            raise FileNotFoundError("{}".format(output_dir))
        if not os.path.isfile(filename):
            raise FileNotFoundError("{}".format(filename))

        logfile = os.path.join(output_dir, "test.log")
        f = open(logfile, 'a')

        ts = datetime.now().strftime("%Y%m%d_%H%M")
        tsname = os.path.basename(filename)
        output_tst = os.path.join(output_dir, "test_{}_{}".format(ts,tsname))
    
        cmd = [self._runtst, filename, output_tst] 

        if timeout:
            cmd.append("-t {}".format(timeout))
            
        if verbose:
            cmd.append( "-v ")
        
        # run it 
        proc = subprocess.Popen(cmd, shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        
        # following lines will be printed out
        string_filter = (   
            "Running test", "Starting time",
            "Initializing test",
            "Saving test", "exiting", "Pair",
            "Ending time", "Invalid", "ERROR")
        
        # read process stdout and stderr
        for line in iter(proc.stdout.readline, b''):
            string = line.decode()
            f.write(string)
            if string.startswith(string_filter) and echo:
                print(">> " + string.rstrip())
        
        f.close()
        return output_tst
        
    def export(self, 
               filename, output_filename, csv=None, html=None, 
               quiet_mode= True, echo=True):
        """Formatting Test Results to file.
    
        export(tst_filename, output_filename, csv=None, html=None, 
               quiet_mode= True, echo=True)
        Values:
        quiet_mode =  { True | False }
        csv  = { None | All | Options | *Summary* | Detailed }
        html = { None | LastConfig | template_name }
        """
        # FMTTST test_filename [output_filename] 
        #       [-v [-o] [-s] [-d] | [-h [-c | -t template_name]]] 
        #       [-q] 
        #      
        #-v  Creates a comma-separated output (with file extension .CSV). You can
        #   select which aspects of the tests to export by specifying the specific 
        #   .CSV options described below. If you use this flag without specifying 
        #   .CSV specific flags, the entire contents of the test are used to create
        #   the output. If you use this flag, you cannot use the -c or -t flag to 
        #   specify the print/options for the results.
        ### CSV option  .CSV Option Description  
        # -o  Provides a summary of any results and your run options.  
        # -s  Provides information contained in the Test Setup tab of the 
        #     Test window (Pair Summary table)  
        # -d  Provides the timing records for the pairs in your test
        #     (Pair Details table) 
        # -h  Creates HTML output. 
        #   This flag controls the format of the output. If you use this flag, 
        #   you cannot use the -s flag. 
        # -c  Generate the output according to the export configuration last used 
        #   in the IxChariot Console. The -c flag exports the test to text format, 
        #   or, in combination with the -h flag, to HTML, using the custom 
        #   configuration settings that were last selected at the IxChariot Console. 
        #   This is useful in limiting the output to the exact data you are 
        #   interested in. This flag controls what print/export options to use for 
        #   the results. If you use this flag, you cannot use the -s flag.  
        # -t  Creates output based on the print/export options saved in an output
        #   template. Enter the name of the output template after this parameter. 
        #   This flag controls what print/export options to use for the results. 
        #   If you use this flag, you cannot use the -c flag.  
        # -q  Run in quiet mode. There is no confirmation for file overwrites.  

        if not os.path.isfile(filename):
            raise FileNotFoundError("{}".format(filename))
            
        cmd = [self._fmttst, filename, output_filename ]
        if csv:
            cmd.append("-v")
            if csv == 'Options':
                cmd.append("-o")
            elif csv == 'Summary':
                cmd.append("-s")
            elif csv == 'Detailed':
                cmd.append("-d")
        elif html:
            cmd.append("-h")
            if csv == 'LastConfig':
                cmd.append("-c")
            else:
                cmd.append( str(html) )
        if quiet_mode:
            cmd.append("-q")
        # run it 
        proc = subprocess.Popen(cmd, shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        string_filter = ("Writing", "IxChariot", "Invalid", "ERROR")
        # read process stdout and stderr
        for line in iter(proc.stdout.readline, b''):
            string = line.decode().rstrip()
            if string.startswith(string_filter) and echo:
                print(">> " + string)
            
        return output_filename 
    
    
   

class TestInfo(object):
    """Collects values and methods form ixia testfile"""
    DELIMITER = ','
    QUOTECHAR = '|'
    
    def __init__(self, filename=None):
        self.ProductInformation = {}
        self.EndpointPairDetails = {}
        self.EndpointPairSummary = {}
        self.GroupAverages = {}
        if filename:
            self.dataimport(filename)
            self.getTP()
        
    def dataimport(self, filename):
        rows = []
        get_keys =  False
        data = {}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, 
                                delimiter=self.DELIMITER, 
                                quotechar=self.QUOTECHAR)
            rows = [row for row in reader]
        for row in rows:
        # Indentify start section
            if not row:
                continue
        
            if row[0].startswith('PRODUCT INFORMATION'):
                section = 'PI'
                data[section] = {}
                get_keys = True
            elif row[0].startswith('ENDPOINT PAIR DETAILS'):
                section = 'EPD'
                data[section] = {}
                get_keys = True
            elif row[0].startswith('ENDPOINT PAIR SUMMARY'):
                section = 'EPS'
                data[section] = {}
                get_keys = True
            elif row[0].startswith('GROUP AVERAGES'):
                section = 'GA'
                data[section] = {}
                get_keys = True
            elif get_keys:
                # First section row
                keys = row
                for key in keys:
                    data[section][key] = []
                get_keys = False
            else:
                # Data row
                for key, entry in zip(keys, row):
                    data[section][key].append(entry)
        # Final assigment
        self.ProductInformation = data.get('PI')
        self.EndpointPairDetails = data.get('EPD')
        self.EndpointPairSummary = data.get('EPS')
        self.GroupAverages = data.get('GA')
        return
        
    def getTP(self):
        """Return 'Throughput Avg.(Mbps)' form 'All Pair'."""
        # List with Group Names
        gnames = self.GroupAverages.get('Group Name')
        # List with Group TP Averages
        gavgs  = self.GroupAverages.get('Throughput Avg.(Mbps)')
        if 'All Pairs' in gnames:
            self.TP = gavgs[gnames.index('All Pairs')]
            return self.TP
        else:
            return None
        
    def getRTT(self):
        index_RTT = t.GroupAverages['Group Name'].index('RTT')
        value = t.GroupAverages['Response Time Avg. (sec)'][index_RTT]
        return float(value)
    
    def get_minMeasuredTime(self):
        times = self.EndpointPairSummary["Measured Time (sec)"]
        return min([float(x) for x in times])
    
    def get_badAquisitions(self, maxResponseTime):
        response_time = [float (e) for e in self.EndpointPairDetails['Response Time (sec)']]
        rt = np.array(response_time)
        return np.size(np.where(rt > maxResponseTime))
    
    def normcheck (self):
        y = np.array(self.EndpointPairDetails['Response Time (sec)']).astype(np.float)
        m = np.quantile(y, 0.5)
        s = 3 * y.std()
        v = np.logical_and((m - s) < y, y < (m + s))
        limit = 0.9973002039367398 #% norm.cdf(3) - norm.cdf(-3)
        k = v.sum() / v.size
        print(k > limit)
        return k > limit
    
    def timecheck (self):
        ts = np.array(self.EndpointPairDetails["Elapsed Time (sec)"]).astype(np.float)
        ts.sort()
        x = np.arange(0, ts.max(), 1)
        count = [np.sum(np.logical_and(n <= ts, ts < (n + 1))) for n in x]
        limit = np.quantile(count, 0.9) / 2
        return np.sum(count[1:-1] < limit) <= 1

    
    def validate(self, minExpectedDuration=30, maxResponseTime=0.15, maxBadAquisitions=50):
        
        if self.get_minMeasuredTime() < minExpectedDuration:
            print("meas time is too short")
            return False
        
        if not self.timecheck():
            print("more than 1 second is bad")
            return False
        
        if self.get_badAquisitions(maxResponseTime=maxResponseTime)>maxBadAquisitions:
            print("too much bad acquisitions")
            return False
        
        return True
