#!/usr/bin/env python

##!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011, Marine Biological Laboratory
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
from stat import * # ST_SIZE etc
import sys
import shutil
import types
import time
import random
import glob
import csv
import re
from time import sleep
import configparser as ConfigParser
#sys.path.append( '/Users/avoorhis/programming/vamps-node.js/public/scripts/maintenance_scripts' )
import logging
import datetime
from datetime import timezone, timedelta
from dateutil import tz
import pytz
import time
#import moment
today = str(datetime.date.today())

import subprocess
#import pymysql as MySQLdb
import socket
from contextlib import closing

"""

"""
# Global:
#NODE_DATABASE = "vamps_js_dev_av"
#NODE_DATABASE = "vamps_js_development"
CONFIG_ITEMS = {}
# get the current time in seconds since the epoch

#https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python
#with open('file', 'w') as sys.stdout:
#    print('test')

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# same as range in 
port_range = ['8080','8081','8082','8083','8084']#,'8086','8087','8088','8089']
#port_range = ['8080','8081','8082','8083']
#sleep_time = 10
sleep_time = 3
time_stamp_max_diff = 50
# 69434 roughly diff between now and epoch
# this diff presents before log file is establised
# used to prevent premature deletion
# nothing above this number will get deleted
#diff_epoch_til_now_limit = 10000
#diff_epoch_til_now_limit = 100000
def kill_proc(pid, note=''):
    if note:
        if args.debug:
            print('killproc note: '+note)
        else:
            logging.info('killproc note: '+note)
    try:
        if args.debug:
            print('killing '+pid)
        else:
            logging.info('killing '+pid)
        os.system('kill '+str(pid)+' 2>/dev/null')
    except:
        if args.debug:
            print('FailERROR - kill '+str(pid))
        else:
            logging.info('FailERROR - kill '+str(pid))
        
def delete_file(fname):
    try:
        if args.debug:
            print('deleting '+fname)
        else:
            logging.info('deleting '+fname)
        os.remove(fname)
    except:
        if args.debug:
            print('FailERROR removing '+fname)
        else:
            logging.info('FailERROR removing '+fname)
def delete_file_by_port(p):
    port_log_file = os.path.join(args.file_base,'anvio.'+p+'.log')
    delete_file(port_log_file)

       
def is_file_updated(fn):
    last_forder_update_timestamp = os.stat(fn).st_mtime
    last_folder_update_datetime = datetime.datetime.fromtimestamp(last_forder_update_timestamp)
    current_datetime = datetime.datetime.now()
    difference = abs(current_datetime - last_folder_update_datetime)
    return difference.total_seconds()
    
def run(args):
    
    #regExp = '\[([^)]+)\]'  # captures date time in parens
    #regExp = '\[(.*?)\]'  # captures date time in parens
    #regExpLogDate = re.compile(r".*\[\s?(\d+/\D+?/.*?)\]")
    #dateformat = '%d/%b/%Y:%H:%M:%S %z'
    log_watch = []
    # [05/Dec/2023:22:18:04 +0000]
    #re_pattern = '([\d\.?]+) - - \[(.*?)\] "(.*?)" (.*?) (.*?) "(.*?)" "(.*?)"'
    # 172.16.0.3 - - [25/Sep/2002:14:04:19 +0200]
    while 1:
        sleep(sleep_time)
        #dt = datetime.datetime.now()
        #currentdt = dt.replace(tzinfo=timezone.utc)
        running_ports = {}
        running_ports_keys = []
        log_ports = {}
        log_port_keys = [] 

        if args.debug:
            print()
        #seconds = time.time()
        
        #print('now',round(seconds, 0))
        #logging.info()
        #cmd = 'ps aux|grep "\-P 80"'
        #res = os.system(cmd)
        res1 = subprocess.check_output('ps aux', shell=True)
        res = str(res1.decode('utf-8')).split('\n')
        #print(res.decode('utf-8'))
        #sys.exit()
        for line in res:
            if 'anvi-display-pan' in line:
                line_parts = line.split()
                #print('res',line_parts)
                # grab and kill unusual ports
                # parse port and pid
                if len(line_parts) > 0:
                    pid = line_parts[1]
                    if line_parts[14] == '-P':
                        
                        port = line_parts[15]
                        #print('GRABBING port from ps aux',port)
                    else:
                        # no descernable port
                        for p in port_range:
                            if p in line:
                               #print('lp',line_parts)
                               port = p
                               break
                            else:
                                pass
                                #port = ''
                                #kill_proc(pid,'port not in ps-aux line')
                    #print('Found port',port)
                    # potential log_file
                    port_log_file = os.path.join(args.file_base,'anvio.'+port+'.log')
                    if port not in port_range:
                        kill_proc(pid,'port ('+str(port)+') not in port range')
                        delete_file_by_port(port)
                    elif not os.path.isfile(port_log_file):
                        # kill if no corresponding log file
                        # kill_proc(pid,'No corresponding log file for '+str(port))
                        pass
                    elif port in running_ports:
                        running_ports[port].append(pid)
                    else:
                        running_ports[port] = [pid]
                else:
                    if args.debug:
                        print('Error line has "anvi-display-pan" but zero length: '+line)
                    else:
                        logging.info('Error line has "anvi-display-pan" but zero length: '+line)
        running_ports_keys = list(running_ports.keys())
        
        
        # now look for and parse log files
        log_files = glob.glob(os.path.join(args.file_base, 'anvio.*.log'))
        #print('og_files',log_files)
        for logFileName in log_files:
            
            p = os.path.basename(logFileName).split('.')[1]
            upFileName = os.path.join(args.file_base, p+'.up')
            
            #print('tport',p)
            # what if "anvio.0.log" ?
            if p not in port_range:
                delete_file(logFileName)
                delete_file(upFileName)
            else:
                if os.path.isfile(logFileName):
                    #print('found',logFileName1)
                    #grep_cmd = ['grep', '"http://127.0.0.1:80"',logFileName]
                    #result = subprocess.run(grep_cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                    #result = subprocess.Popen('grep "http://127.0.0.1:80" %s' % logFileName, stdout=subprocess.PIPE, shell=True)
                    #serving on 0.0.0.0:8080 view at http://127.0.0.1:8080
                    try:
                        result = subprocess.check_output(['grep', 'http://127.0.0.1:', logFileName])
                        #print('grepcmd',grep_cmd)
                        if args.debug:
                            print(p+' grep result: '+(result.strip()).decode('utf-8'))
                        else:
                            logging.info(p+' grep result: '+(result.strip()).decode('utf-8'))
                        fpup = open(os.path.join(args.file_base, p+'.up'), "w")
                        fpup.write(p+'up')
                        fpup.close()
                    except:
                        if args.debug:
                            print(p+' grep result 0')
                        else:
                            logging.info(p+' grep result 0')
                    
                    if p in running_ports_keys:
                        log_ports[p] = 1
                    else:
                        if args.debug:
                            print('deleting this log file (no anvio running) '+p)
                        else:
                            logging.info('deleting this log file (no anvio running) '+p)
                        delete_file(logFileName)
                        delete_file(upFileName)
                        if p in log_ports:
                            log_ports.pop(p)
                else:
                    if args.debug:
                        print('Error -NOT isFile '+logFileName)
                    else:
                        logging.info('Error -NOT isFile '+logFileName)
                    
                    
        log_ports_keys = list(log_ports.keys())
        log_ports_keys.sort()
        running_ports_keys.sort()
        if args.debug:
            print('running_ports: '+str(running_ports_keys))
        else:
            logging.info('running_ports: '+str(running_ports_keys))
        if args.debug:
            print('log_ports '+str(log_ports_keys))
        else:
            logging.info('log_ports '+str(log_ports_keys))
        open_ports = list(set(port_range) - set(log_ports_keys))
        logging.info(str(len(open_ports))+' Open Ports '+str(open_ports))
        # keep an updated file of open ports for node code
        fp = open(os.path.join(args.file_base,'open_ports.txt'), "w")
        fp.write(str(open_ports))
        fp.close()
        #time.sleep(5.5)
        
        for p in log_ports_keys:
            # read the log files and if the time stamp is not current 
            # or there is no time stamp
            # kill the process and delete the log file
            
            pfn = os.path.join(args.file_base, 'anvio.'+p+'.log')
            ufn = os.path.join(args.file_base, p+'.up')
            difference_seconds = is_file_updated(pfn) # difference from current time
            if args.debug:
                print(p+' dif '+str(difference_seconds))
            else:
                logging.info(p+' dif '+str(difference_seconds))
            if difference_seconds > time_stamp_max_diff:
                if args.debug:
                    print('Deleting because DIFF between: '+str(time_stamp_max_diff))
                else:
                    logging.info('Deleting because DIFF between: '+str(time_stamp_max_diff))
                
                delete_file(pfn)
                delete_file(ufn)
                for pid in running_ports[p]:
                    #print('pid',pid)
                    kill_proc(pid,'long time sep logfile from proc')
                 
        #sys.exit()
    
if __name__ == '__main__':
    import argparse
    
    
    myusage = """usage: anvio_port_monitor.py  [options]
         
         must be run in the anvio docker container
         
         will monitor anvio ports in the 8080-8089 range
         and close down any unused ports by finding the orphan anvio process
         and killing it
         
         -host anvio-homd  DEFAULT localhost
         
    """
    parser = argparse.ArgumentParser(description="" ,usage=myusage)                 
    
       
    parser.add_argument("-host", "--host",    
                required=False,  action="store",   dest = "host", default='localhost',
                help = '')
    parser.add_argument("-debug", "--debug",    
                required=False,  action="store_true",   dest = "debug", default=False,
                help = '')
    
    args = parser.parse_args() 
    
    logging.basicConfig(level=logging.DEBUG, filename="port_monitor.log", filemode="w",
                format="%(asctime)-15s %(levelname)-8s %(message)s") 
                  
    if args.host == 'homd_dev' or args.host == 'homd_prod':
        args.file_base = '/home/ubuntu/anvio/pangenomes/'
    elif args.host == 'localhost':
        args.file_base = '/Users/avoorhis/programming/github/pangenomes/'
    else:
        print(myusage)
        sys.exit()
        
        
    args.datetime     = str(datetime.date.today())    
    
    run(args)
    #sys.exit('END: vamps_script_upload_metadata.py')
    
