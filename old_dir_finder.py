#!/usr/bin/env python

#########################################################################
# Author: Hechuan Yang
# Created Time: 2017-12-07 20:25:28
# File Name: old_dir_finder.py
# Description: 
#########################################################################

import os
import sys
import argparse
import subprocess

#handle the error below
#python | head == IOError: [Errno 32] Broken pipe 
from signal import signal, SIGPIPE, SIG_DFL 
signal(SIGPIPE,SIG_DFL)

def main():
    parse=argparse.ArgumentParser(description='A script to find out big old directories (Linux only)')
    parse.add_argument('dir',type=str,metavar='DIR',nargs='+',
        help='check the disk usage under this directory')
    default=365
    parse.add_argument('-d','--day',type=int,metavar='DAY',default=default,
        help="directories' status was last changed DAY ago[{}]".format(default))
    default=1024
    parse.add_argument('-s','--size',type=int,metavar='SIZE',default=default,
        help="directories' size larger than or equal with SIZE (Mb) [{}]".format(default))
    parse.add_argument('-l','--level',type=int,metavar='N',
        help='the deepest levels (depth) to descend')
    default='concise'
    parse.add_argument('-m','--mode',choices=['concise','full'],default=default,
        help='output mode ('+
        'concise: do not output subfolder if its parent satisfy the criteria; '+
        'full: output all folders) [{}]'.format(default))
    args=parse.parse_args()

    now=int(subprocess.getoutput('date +%s'))
    span=args.day*24*60*60
    before=now-span
    date=subprocess.getoutput('date -d @{} -Idate'.format(before))
    duArgs=['du','-m','--time=ctime','--time-style=iso']
    if args.level:
        duArgs.append('--max-depth={}'.format(args.level))
    duArgs.extend(args.dir)
    du=subprocess.Popen(args=duArgs,stdout=subprocess.PIPE)
    awkArgs=['awk','$1>={} && $2<="{}"'.format(args.size,date)]
    awk=subprocess.Popen(args=awkArgs,stdin=du.stdout,stdout=subprocess.PIPE)
    end_of_pipe=awk.stdout

    print('#size(Mb)\ttime\tdir')
    if args.mode=='concise':
        table={}
        for line in end_of_pipe:
            size,time,folder=line.decode('utf-8').strip().split()
            if len(table)>0:
                for k in list(table):
                    if k.startswith(folder):
                        del(table[k])
                        table[folder]=[size,time]
                    elif folder.startswith(k):
                        pass
                    else:
                        table[folder]=[size,time]
            else:
                table[folder]=[size,time]
        for folder in sorted(table.keys(),key=lambda x: table[x][1]):
            print('\t'.join(table[folder]+[folder]))
    else:
        for line in end_of_pipe:
            print(line.decode('utf-8').strip())

if __name__=='__main__':
    main()    
