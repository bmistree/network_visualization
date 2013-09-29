#!/usr/bin/env python

import sys,os
import parse_traceroutes 
from node import emit_http

def http_from_traceroute_folder(
    folder_to_generate_from,addr_to_hit):

    all_nodes = {}
    generate_all_nodes(all_nodes,folder_to_generate_from)
    
    emit_http(all_nodes,addr_to_hit)


def generate_all_nodes(all_nodes,folder_to_generate_from):
    for (path,dirs,files) in os.walk(folder_to_generate_from):
        for single_filename in files:
            traceroute_file = os.path.join(path,single_filename)
            parse_traceroutes.parse_traceroute_file(all_nodes,traceroute_file)

        for single_dir in dirs:
            generate_all_nodes(all_nodes,os.path.join(path,single_dir))
            
if __name__ == '__main__':
    '''
    ./http_nodes.py <traceroute folder> <server address>

    Example server address: http://bcoli.stanford.edu:13998/add_links
    '''
    http_from_traceroute_folder(sys.argv[1],sys.argv[2])
    
