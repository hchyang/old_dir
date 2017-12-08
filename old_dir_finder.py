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
    parse=argparse.ArgumentParser(description='a script to find old directories')
    default='./'
    parse.add_argument('-d','--dir',type=str,metavar='DIR',default=default,
        help='check the usage under this directory [{}]'.format(default))
    default=365
    parse.add_argument('-o','--old',type=int,metavar='DAY',default=default,
        help='only directory older than DAY will be output')
    parse.add_argument('-l','--level',type=int,metavar='N',
        help='the max levels (depth) to descend')
    args=parse.parse_args()

    now=int(subprocess.getoutput('date +%s'))
    span=args.old*24*60*60
    before=now-span
    date=subprocess.getoutput('date -d @{} -Idate'.format(before))
    duArgs=['du','-m','--time=ctime','--time-style=iso']
    if args.level:
        duArgs.append('--max-depth={}'.format(args.level))
    duArgs.append(args.dir)
    du=subprocess.Popen(args=duArgs,stdout=subprocess.PIPE)
    awkArgs=['awk','$2<"{}"'.format(date)]
    awk=subprocess.Popen(args=awkArgs,stdin=du.stdout,stdout=subprocess.PIPE)
    end_of_pipe=awk.stdout

    for line in end_of_pipe:
        print(line.decode('utf-8').strip())

if __name__=='__main__':
    main()    
