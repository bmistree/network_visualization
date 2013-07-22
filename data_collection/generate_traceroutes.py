#!/usr/bin/env python
import sys,os,subprocess

def issue_single_traceroute(host_dest,folder_to_save_to):
    cmd = ['traceroute',host_dest]

    file_to_save_to = open(os.path.join(folder_to_save_to,host_dest),'w')
    proc = subprocess.Popen(cmd,shell=False,stdout=file_to_save_to)
    proc.wait()
    file_to_save_to.flush()
    file_to_save_to.close()
    

def run(to_traceroute_to_filename,folder_to_save_traceroutes_to):

    to_tr_to = open(to_traceroute_to_filename,'r')
    for to_tr_to_line in to_tr_to:
        stripped_line = to_tr_to_line.strip()
        if stripped_line == '':
            continue

        issue_single_traceroute(stripped_line,folder_to_save_traceroutes_to)
        
        
    to_tr_to.close()
    
    

if __name__ == '__main__':
    run(sys.argv[1],sys.argv[2])
