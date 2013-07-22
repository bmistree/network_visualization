#!/usr/bin/env python
from node import Node
import re

def parse_traceroute_file(all_nodes,filename):
    filer = open(filename,'r')
    prev_node = None
    for line in filer:
        node = parse_traceroute_line(line)
        if node != None:
            all_nodes[node.ip_addr] = node
        
            if prev_node != None:
                node.bidirectional_add_connection(prev_node)
        prev_node = node
    filer.close()

def parse_traceroute_line(line):
    '''
    @returns {None or Node}

    @param {string} line --- Can have the following forms:
    traceroute to stanford.edu (171.64.13.26), 30 hops max, 60 byte packets
     1  172.19.152.2 (172.19.152.2)  22.270 ms * *
     2  res-wirelessa-rtr.Stanford.EDU (128.12.1.74)  1.805 ms  1.912 ms  1.902 ms
     3  east-res-rtr-po2-3964.SUNet (128.12.1.13)  3.470 ms * *
     4  west-rtr-vlan8.SUNet (171.64.255.193)  2.428 ms  2.519 ms  4.446 ms
     5  woz-srtr-vlan12.Stanford.EDU (172.20.11.35)  1.920 ms  2.374 ms  2.364 ms
     6  www-lb.Stanford.EDU (171.64.13.26)  4.388 ms  2.728 ms  2.632 ms
    '''
    # pattern is whitespace, number, expression without white space, whitespace, paren ipv4 paren
    expression = '\s*\d+\s+(?P<hostname>.*?)\s+\((?P<ip_addr>\d+\.\d+\.\d+\.\d+)\)'
    match = re.search(expression,line)

    if match == None:
        return None
    return Node(match.group('ip_addr'),match.group('hostname'))

