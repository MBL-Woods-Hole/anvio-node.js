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


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# same as range in 
port_range = ['8080','8081','8082','8083','8084','8085']#,'8086','8087','8088','8089']
#port_range = ['8080','8081','8082','8083']
sleep_time = 6
time_stamp_max_diff = 30
# 69434 roughly diff between now and epoch
# this diff presents before log file is establised
# used to prevent premature deletion
# nothing above this number will get deleted
#diff_epoch_til_now_limit = 10000
diff_epoch_til_now_limit = 100000
def kill_proc(pid):
    try:
        print('killing',pid)
        os.system('kill '+str(pid)+' 2>/dev/null')
    except:
        print('FailERROR','kill '+str(pid))
        
def delete_file(fname):
    try:
        print('deleting',fname)
        os.remove(fname)
    except:
        print('FailERROR removing',fname)
def delete_file_by_port(p):
    port_log_file = os.path.join(args.file_base,'anvio.'+p+'.log')
    delete_file(port_log_file)
# def kill_proc_by_port(p):
#     try:
#         print('killing',pid)
#         os.system('kill '+str(pid)+' 2>/dev/null')
#     except:
#         print('FailERROR','kill '+str(pid))        
def check_date_match(last_line):
    re_match = regExp.search(last_line)
    if re_match:
       # good to tell
       return 1
    else:
       time.sleep(5.5)
       return 0
       
def is_file_updated(fn):
    last_forder_update_timestamp = os.stat(fn).st_mtime

    last_folder_update_datetime = datetime.datetime.fromtimestamp(last_forder_update_timestamp)
    current_datetime = datetime.datetime.now()

    difference = current_datetime - last_folder_update_datetime
    
    return difference.total_seconds()
    
def run(args):
    
    #regExp = '\[([^)]+)\]'  # captures date time in parens
    #regExp = '\[(.*?)\]'  # captures date time in parens
    regExpLogDate = re.compile(r".*\[\s?(\d+/\D+?/.*?)\]")
    dateformat = '%d/%b/%Y:%H:%M:%S %z'
    log_watch = []
    # [05/Dec/2023:22:18:04 +0000]
    #re_pattern = '([\d\.?]+) - - \[(.*?)\] "(.*?)" (.*?) (.*?) "(.*?)" "(.*?)"'
    # 172.16.0.3 - - [25/Sep/2002:14:04:19 +0200]
    while 1:
        sleep(sleep_time)
        dt = datetime.datetime.now()
        currentdt = dt.replace(tzinfo=timezone.utc)
        running_ports = {}
        running_ports_keys = []
        log_ports = {}
        log_port_keys = [] 
        
        
        #seconds = time.time()
        
        #print('now',round(seconds, 0))
        print()
        #cmd = 'ps aux|grep "\-P 80"'
        #res = os.system(cmd)
        res1 = subprocess.check_output('ps aux', shell=True)
        res = str(res1.decode('utf-8')).split('\n')
        for line in res:
            if 'anvi-display-pan' in line:
                line_parts = line.split()
        
    
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
    
    
    args = parser.parse_args()    
    if args.host == 'anvio-homd':
        args.file_base = '/home/ubuntu/anvio/pangenomes/'
    elif args.host == 'localhost':
        args.file_base = '/Users/avoorhis/programming/github/pangenomes/'
    else:
        print(myusage)
        sys.exit()
        
        
    args.datetime     = str(datetime.date.today())    
    
    run(args)
    #sys.exit('END: vamps_script_upload_metadata.py')
    
