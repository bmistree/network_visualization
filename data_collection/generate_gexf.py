#!/usr/bin/env python

import sys,os
import parse_traceroutes 
from node import emit_gexf

def generate_gexf_file_from_traceroute_folder(
    folder_to_generate_from,gexf_filename):

    all_nodes = {}
    generate_all_nodes(all_nodes,folder_to_generate_from)

    emit_gexf(all_nodes,gexf_filename)

def generate_all_nodes(all_nodes,folder_to_generate_from):
    for (path,dirs,files) in os.walk(folder_to_generate_from):
        for single_filename in files:
            traceroute_file = os.path.join(path,single_filename)
            parse_traceroutes.parse_traceroute_file(all_nodes,traceroute_file)

        for single_dir in dirs:
            generate_all_nodes(all_nodes,os.path.join(path,single_dir))
            

# def generate_gexf_file_from_traceroute_folder(
#     folder_to_generate_from,gexf_filename):

#     all_nodes = {}
#     for (path,dirs,files) in os.walk(folder_to_generate_from):
#         for single_filename in files:
#             traceroute_file = os.path.join(path,single_filename)
#             parse_traceroutes.parse_traceroute_file(all_nodes,traceroute_file)

#     emit_gexf(all_nodes,gexf_filename)


if __name__ == '__main__':
    '''
    ./generate_gexf.py <traceroute folder> <gexf filename>
    '''
    generate_gexf_file_from_traceroute_folder(
        sys.argv[1],sys.argv[2])
    
