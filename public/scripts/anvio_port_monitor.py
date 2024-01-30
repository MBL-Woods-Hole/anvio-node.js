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
locahost_path_to_pangenomes = '/Users/avoorhis/programming/github/pangenomes/'
server_path_to_pangenomes = '/home/ubuntu/anvio/pangenomes/'
port_monitor_log = 'port_monitor.log'
open_ports_txt = 'open_ports.txt'
log_file_template = '%s.pg.log'
up_file_template = '%s.up'
sh_file_template = '%s.sh'
port_range = ['8080','8081','8082','8083','8084','8085','8086'] #,'8087','8088','8089']
#port_range = ['8080','8081','8082','8083']
sleep_time = 4
time_stamp_max_diff = 200 #70
diff_epoch_til_now_limit = 100000

class Proc:
    def __init__(self, pid, port):
        self.pid = pid
        self.port = port
        self.age = 0
        self.diff = 0
        self.logfn = os.path.join(args.file_base, log_file_template % port)
        self.upfn  = os.path.join(args.file_base,  up_file_template % port)
        self.shfn  = os.path.join(args.file_base,  sh_file_template % port)
        
    def kill_proc(self):
        
        try:
            os.system('kill '+str(self.pid)+' 2>/dev/null')
            if args.debug:
                print('killing',self.pid)
            else:
                args.mainlogfilep.write('killing',self.pid,'\n')
        except:
            pass
            
    def delete_files(self):
        
        try:
            os.remove(self.upfn)
            if args.debug:
                print('deleting',self.upfn)
            else:
                args.mainlogfilep.write('deleting',self.upfn,'\n')
        except:
            pass
        try:
            os.remove(self.logfn)
            if args.debug:
                print('deleting',self.logfn)
            else:
                args.mainlogfilep.write('deleting',self.logfn,'\n')
        except:
            pass
        try:
            os.remove(self.shfn)
            if args.debug:
                print('deleting',self.shfn)
            else:
                args.mainlogfilep.write('deleting',self.shfn,'\n')
        except:
            pass
            
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def delete_file(fname):
    try:
        os.remove(fname)
        if args.debug:
            print('deleting',fname)
        else:
            args.mainlogfilep.write('deleting',fname,'\n')
    except:
        pass
        
# def delete_file_by_port(port):
#     port_log_file = os.path.join(args.file_base, log_file_template % port)
#     delete_file(port_log_file)
    
# def initialize(pid):
#     tmp = {}
#     tmp['port'] = port
#     tmp['lapsed'] = 
#     tmp['diff'] =
#     tmp['log'] = 
#     tmp['up'] =
    
def check_date_match(last_line):
    re_match = regExp.search(last_line)
    if re_match:
       # good to tell
       return 1
    else:
       time.sleep(5.5)
       return 0

def is_file_updated(fn):
    try:
        update_timestamp = os.stat(fn).st_mtime
        update_datetime = datetime.datetime.fromtimestamp(update_timestamp)
        current_datetime = datetime.datetime.now()
        difference = current_datetime - update_datetime
        return difference.total_seconds()
        
    except:
        return time_stamp_max_diff + 10  # plus ten 
        
def check_port_monitor_log_size():
    current_size = args.mainlogfilep.tell()
    if current_size > 6000000:  # 6,000,000
        args.mainlogfilep.truncate(0)
        
def clean_all():
    # remove all files (*.log and *.up) and procs
    for port in port_range:
        filename1 = os.path.join(args.file_base, log_file_template % port)
        delete_file(filename1)
        filename2 = os.path.join(args.file_base, port+'.up')
        delete_file(filename2)
        filename3 = os.path.join(args.file_base, port+'.sh')
        delete_file(filename3)
        
    res1 = subprocess.check_output('ps aux', shell=True)
    res = str(res1.decode('utf-8')).split('\n')
    for line in res:
        if 'anvi-display-pan' in line:
            line_parts = line.split()
            pid = line_parts[1]
            try:
                os.system('kill '+str(pid)+' 2>/dev/null')
                if args.debug:
                    print('killing',pid)
                else:
                    args.mainlogfilep.write('\n')
                
            except:
                if args.debug:
                    print('Fail ERROR kill '+str(pid))
                else:
                    args.mainlogfilep.write('\n')
        
def run(args):
    master = {}
    count = 0
    while 1:
        if count == 0:
            clean_all()
        count += 1 
        if count > 100000:
            count = 10  #just keeping count reasonable => don't reset to zero!
        sleep(sleep_time)
        check_port_monitor_log_size()  # on every pass???
        running_ports = []
        log_ports = []
        res1 = subprocess.check_output('ps aux', shell=True)
        res = str(res1.decode('utf-8')).split('\n')
        #print('res',res)
        #sys.exit()
        for line in res:
            if 'anvi-display-pan' in line:
                line_parts = line.split()
                #print('resLP',line_parts)
                # grab and kill unusual ports
                port_index = line_parts.index('-P') + 1
                pid = line_parts[1]
                port = line_parts[port_index]
                
                if port in master:
                    master[port].age += sleep_time 
                else:
                    master[port] = Proc(pid,port)
                
        running_ports = list(master.keys())
        
        for port in list(master):
            
            if master[port].age > 10 and not os.path.isfile(master[port].logfn):
                #kill_proc(pid,'No corresponding log file for '+str(port))
                if args.debug:
                    print('killig proc because no log > 10sec')
                else:
                    args.mainlogfilep.write('killig proc because no log > 10sec'+'\n')
                master[port].kill_proc()
                del master[port]
            if os.path.isfile(master[port].logfn):
                log_ports.append(port)
                try:
                    result = subprocess.check_output(['grep', 'http://127.0.0.1:', master[port].logfn])
                    print('grepcmd',grep_cmd)
                    if args.debug:
                        print(port+' grep result: '+(result.strip()).decode('utf-8'))
                    else:
                         args.mainlogfilep.write(p+' grep result: '+(result.strip()).decode('utf-8')+'\n')
                    fpup = open(master[port].upfn, "w")
                    fpup.write(port+'up')
                    fpup.close()
                except:
                     if args.debug:
                         print(port+' grep result 0')
                     else:
                         args.mainlogfilep.write(port+' grep result 0'+'\n')
            
            else:
                if args.debug:
                    print('Error -NOT isFile '+master[port].logfn)
                else:
                    args.mainlogfilep.write('Error -NOT isFile '+master[port].logfn+'\n')
        
        log_ports.sort()
        running_ports.sort()
        if args.debug:
            print('running_ports: '+str(running_ports))
        else:
            args.mainlogfilep.write('running_ports: '+str(running_ports)+'\n')
        if args.debug:
            print('log_ports '+str(log_ports))
        else:
            args.mainlogfilep.write('log_ports '+str(log_ports)+'\n')
        
        if log_ports != running_ports:
            if args.debug:
                print('ERROR running_ports != log_ports: ')
            else:
                args.mainlogfilep.write('ERROR running_ports != log_ports:\n')
        else:
            open_ports = list(set(port_range) - set(log_ports))
            open_ports.sort()
            if args.debug:
                print(str(len(open_ports))+' Open Ports: '+str(open_ports))
            else:
                args.mainlogfilep.write(str(len(open_ports))+' Open Ports: '+str(open_ports)+'\n')
            # keep an updated file of open ports for node code
            fp = open(os.path.join(args.file_base, open_ports_txt), "w")
            fp.write(str(open_ports))
            fp.close()
            
        # check time difference
        for port in list(master):
            # read the log files and if the time stamp is not current 
            # or there is no time stamp
            # kill the process and delete the log file
            
            difference_seconds = is_file_updated(master[port].logfn) # difference from current time
            if args.debug:
                print(port+' diff: '+str(difference_seconds))
            else:
                args.mainlogfilep.write(port+' diff: '+str(difference_seconds)+'\n')
            if difference_seconds > time_stamp_max_diff:
                if args.debug:
                    print('Deleting because DIFF between: '+str(time_stamp_max_diff))
                else:
                    args.mainlogfilep.write('Deleting because DIFF between: '+str(time_stamp_max_diff)+'\n')
                
                master[port].kill_proc()
                master[port].delete_files()
                del master[port]
                
                #remove port from master
                try:
                    running_ports.remove(port)
                except:
                    pass
                try:
                    log_ports.remove(port)
                except:
                    pass
        
        
if __name__ == '__main__':
    import argparse
    
    
    myusage = """usage: anvio_port_monitor.py  [options]
         
         must be run in the anvio docker container
         
         will monitor anvio ports in the 8080-8089 range
         and close down any unused ports by finding the orphan anvio process
         and killing it
         
         -host homd_dev  DEFAULT localhost
         
    """
    parser = argparse.ArgumentParser(description="" ,usage=myusage)                 
    
       
    parser.add_argument("-host", "--host",    
                required=False,  action="store",   dest = "host", default='localhost',
                help = '')
    parser.add_argument("-debug", "--debug",    
                required=False,  action="store_true",   dest = "debug", default=False,
                help = '-debug will print to STDOUT. Default: log to file')
    
    args = parser.parse_args()    
    if args.host == 'homd_dev':
        args.file_base = '/home/ubuntu/anvio/pangenomes/'
    elif args.host == 'localhost':
        args.file_base = '/Users/avoorhis/programming/github/pangenomes/'
    else:
        print(myusage)
        sys.exit()
        
        
    args.datetime     = str(datetime.date.today())    
    if args.host == 'localhost':
        args.file_base = locahost_path_to_pangenomes
    else:
        args.file_base = server_path_to_pangenomes
        
    args.mainlogfilep = open(port_monitor_log, 'w')
    
    run(args)
    #sys.exit('END: vamps_script_upload_metadata.py')
    
