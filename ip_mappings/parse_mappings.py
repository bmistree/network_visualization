#!/usr/bin/env python

import sys
import pickle
import json
from stanford_to_lat_long_mappings import stanford_to_lat_long_mappings

IP_RANGE_MODEL = 'IPRange'


class IPRange(object):
    def __init__(self,prefix,block,group_name):
        self.group_name = group_name
        self.prefix = prefix
        self.block = block
        
        self.lower_bound = self.ip_addr_to_num(self.prefix)
        self.upper_bound = self.lower_bound + (2** (32 - int(self.block)))

    def ip_addr_within(self,str_ip_addr):
        '''
        @returns {int} --- if int < 0, means ip addr is less than
        range.  if int > 0, means ip addr is greater than range.  if
        ing == 0, within range.
        '''
        num_addr = self.ip_addr_to_num(str_ip_addr)
        if num_addr > self.upper_bound:
            return 1
        elif num_addr < self.lower_bound:
            return -1
        return 0

    def ip_addr_to_num(self,str_ip_addr):
        str_ip_addr = str_ip_addr.split('.')
        to_return = 0
        for i in range(0,len(str_ip_addr)):
            multiplier = 256 ** (4-i)
            to_return += int(str_ip_addr[i])*multiplier
        return to_return
        
    def __str__(self):
        return self.prefix + '/' + self.block

    def dictify(self,pk,):
        lat_long_array = stanford_to_lat_long_mappings[self.group_name]
        # first element is latitude, second element is a longitude
        dictified = {
            'model': IP_RANGE_MODEL,
            'pk': pk,

            'fields': {
                'lower_bound': self.lower_bound,
                'upper_bound': self.upper_bound,
                'latitude': lat_long_array[0],
                'longitude': lat_long_array[1],
                }
            }
        return dictified

    
class Group(object):
    def __init__(self,name):
        self.name = name
        self.ip_ranges = []
    def add_ip_range(self,ip_range):
        self.ip_ranges.append(ip_range)


class Parser(object):

    def __init__(self):
        self.all_groups = []

    def print_names(self):
        for group in self.all_groups:
            print group.name

    def handle_line(self,line):
        if line.strip() == '':
            pass
        elif line[0] != ' ':
            # new building name
            self.create_group(line.strip())
        elif line.find(':') != -1:
            # skip ipv6 addresses
            pass
        else:
            # add ip to latest group
            last_group = self.all_groups[-1]
            ip_range = self.parse_ip_range(line.strip(),last_group.name)
            last_group.add_ip_range(ip_range)
            
    def create_group(self,group_name):
        self.all_groups.append(Group(group_name))
        
    def parse_ip_range(self,line,group_name):
        '''
        @param {string} line ---
        171.66.236.0/24       68    172.26.236.10 
        171.66.238.0/24       36                  
        10.21.252.0/22        13                  
        '''
        space_index = line.find(' ')
        ip_range_txt = line[0:space_index]
        slash_index = ip_range_txt.find('/')
        ip_addr = ip_range_txt[0:slash_index]
        block = ip_range_txt[slash_index+1:len(ip_range_txt)]

        return IPRange(ip_addr,block,group_name)

    def get_sorted_ip_ranges(self):
        '''
        @returns {list} --- Each element is an IPRange object.
        '''
        ip_ranges = []
        for x in self.all_groups:
            ip_ranges += x.ip_ranges

        ip_ranges.sort(key=lambda x: x.lower_bound)
        return ip_ranges

    def get_dictified_ip_ranges(self):
        pk_counter = 1
        dict_list = []
        for group in self.all_groups:
            for ip_range in group.ip_ranges:
                dict_list.append( ip_range.dictify(pk_counter))
                pk_counter += 1
        return dict_list

def run(input_filename,output_filename):
    '''
    @param{string} output_filename --- Output a json file that can be
    saved as a fixture for db.
    '''
    # read the file
    parser = Parser()
    filer = open(input_filename,'r')
    for line in filer:
        parser.handle_line(line)
    filer.close()

    # parser.print_names()

    # sorted_ip_ranges = parser.get_sorted_ip_ranges()
    # filer = open(output_filename,'w')
    # filer.write(pickle.dumps(sorted_ip_ranges))
    # filer.flush()
    # filer.close()

    # output the dict of ip ranges that gets loaded into the database
    # via fixtures.
    dictified_range = parser.get_dictified_ip_ranges()
    filer = open(output_filename,'w')
    filer.write(json.dumps(dictified_range,indent=4))
    filer.flush()
    filer.close()
    

if __name__ == '__main__':
    # first argument is ip_to_building.txt
    # second argument is file to output to.
    run(sys.argv[1],sys.argv[2])
