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
time_stamp_max_diff = 50
# 69434 roughly diff between now and epoch
# this diff presents before log file is establised
# used to prevent premature deletion
# nothing above this number will get deleted
#diff_epoch_til_now_limit = 10000
diff_epoch_til_now_limit = 100000
def kill_proc(pid, note=''):
    if note:
        print('killproc note:',note)
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

        
        #seconds = time.time()
        
        #print('now',round(seconds, 0))
        print()
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
                                port = ''
                                kill_proc(pid,'port not in ps-aux line')
                    #print('Found port',port)
                    # potential log_file
                    port_log_file = os.path.join(args.file_base,'anvio.'+port+'.log')
                    if port not in port_range:
                        kill_proc(pid,'port not in port range')
                        delete_file_by_port(port)
                    elif not os.path.isfile(port_log_file):
                        # kill if no corresponding log file
                        kill_proc(pid,'No corresponding log file')
                    elif port in running_ports:
                        running_ports[port].append(pid)
                    else:
                        running_ports[port] = [pid]
                else:
                    print('Error line has "anvi-display-pan" but zero length',line)
        running_ports_keys = list(running_ports.keys())
        
        
        # now look for and parse log files
        log_files = glob.glob(os.path.join(args.file_base,'anvio.*.log'))
        #print('og_files',log_files)
        for logFileName in log_files:
            
            p = os.path.basename(logFileName).split('.')[1]
            #print('tport',p)
            # what if "anvio.0.log" ?
            if p not in port_range:
                delete_file(logFileName)
            else:
                if os.path.isfile(logFileName):
                    #print('found',logFileName1)
                    if p in running_ports_keys:
                        log_ports[p] = 1
                    else:
                        print('deleting this log file (no anvio running)',p)
                        delete_file(logFileName)
                        if p in log_ports:
                            log_ports.pop(p)
                else:
                    print('Error -NOT isFile',logFileName)
                    
                    
        log_ports_keys = list(log_ports.keys())
        log_ports_keys.sort()
        running_ports_keys.sort()
        print('running_ports',running_ports_keys)
        print('log_ports',log_ports_keys)
        open_ports = list(set(port_range) - set(log_ports_keys))
        print(len(open_ports),'Open Ports',open_ports)
        # keep an updated file of open ports for node code
        fp = open(os.path.join(args.file_base,'open_ports.txt'), "w")
        fp.write(str(open_ports))
        fp.close()
        #time.sleep(5.5)
        
        for p in log_ports_keys:
            # read the log files and if the time stamp is not current 
            # or there is no time stamp
            # kill the process and delete the log file
            
            fn = os.path.join(args.file_base, 'anvio.'+p+'.log')
            difference_seconds = is_file_updated(fn) # difference from current time
            print(p,'dif',difference_seconds)
            if difference_seconds > time_stamp_max_diff:
                print('Deleting because DIFF between',time_stamp_max_diff)
                
                delete_file(fn)
                
                for pid in running_ports[p]:
                    #print('pid',pid)
                    kill_proc(pid,'long time sep logfile from proc')
                 
#             #try:
#             fp = open(fn,'r')
#             for line in fp:
#                 line = line.strip()
#             last_line = line
#             #print('last line',last_line)
#             #re_match = re.match(regExp, last_line)
#             re_match = regExpLogDate.search(last_line)
#             #m = check_date_match(last_line)
#             
#             if re_match:
#                 re_matchg1 = re_match.group(1)
#                 #print('last line',last_line)
#                 print('re match',re_matchg1)
#                 date_time_obj = datetime.datetime.strptime(re_matchg1, dateformat)
#                 difference_seconds = abs((currentdt - date_time_obj).seconds)
#             else:
#                 
#                 #get the ls -l 
#                 #delete_file_by_port(p)
#                 #cmd = "ls -l "+fn
#                 #-rw-r--r-- 1 root root 809 Dec 21 21:10 anvio.8085.log
#                 z = os.stat(fn)
#                 print('stat',os.stat(fn))
#                 update_time = z.st_mtime 
#                 
#                 difference_seconds = is_file_updated(fn)
#                 print(p,fn,'using os.stat.mtime',difference_seconds)
#                 #timezone_naive_modified = datetime.fromtimestamp(os.stat(fn).st_mtime)
#                 #(t-datetime.datetime(1970,1,1)).total_seconds()
#                 #print((currentdt-datetime.datetime(1970,1,1)).total_seconds())
#                 #output = subprocess.check_output("ls -l "+fn, shell=True)
#                 #proc = subprocess.Popen(["ls -l", fn], stdout=subprocess.PIPE, shell=True)
#                 # pts = str(output).split()
# #                 print("program output:", pts)
# #                 month = pts[5]
# #                 day_of_month = pts[6]
# #                 seconds_pts = pts[7].split(':')  # '21:10'  9pm
# #                 hr_military = seconds_pts[0]
# #                 mint = seconds_pts[1]
# #                 year = datetime.date.today().year
# #                 m = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
# #                 print('year',year,'month',month,'day',day_of_month,'sec',seconds)
# #                 new Date(year, m[month], day [, hour, minute, second, millisecond ])
# #                 const date = new Date(year, m[month], day_of_month, hr_military, mint, 0);
#                 #difference_seconds = diff_epoch_til_now_limit + 10
#                 #print(p,'using artificial time to NOT delete',difference_seconds)
# #                 #epoch = datetime.datetime(1970, 1, 1,0,0,0)
# #                 epoch = datetime.datetime(1970, 1, 1)
# #                 
# #                 print(p,'using artificial time to delete',epoch)
# #                 #date_time_obj = epoch.replace(tzinfo=pytz.UTC)
# #                 date_time_obj = currentdt - timedelta(days=20)
# #                 difference_seconds = 500  # Must delete
#             # 69434 roughly diff between now and epoch
#             
#             print('Port:',p,'(Diff:',difference_seconds,'secs)')
#             
#             if difference_seconds > time_stamp_max_diff and difference_seconds < diff_epoch_til_now_limit:
#                 print('Deleting because DIFF between',time_stamp_max_diff,'and',diff_epoch_til_now_limit)
#                 logFileName = os.path.join(args.file_base, 'anvio.'+p+'.log')
#                 
#                 delete_file(logFileName)
#                 
#                 for pid in running_ports[p]:
#                     #print('pid',pid)
#                     kill_proc(pid)
                
                    
                    # get 
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
    
