#!/usr/bin/env python

import httplib
import json
import models

def ip_addr_to_num(str_ip_addr):
    str_ip_addr = str_ip_addr.split('.')
    to_return = 0
    for i in range(0,len(str_ip_addr)):
        multiplier = 256 ** (3-i)
        middle_num =  int(str_ip_addr[i])*multiplier
        to_return += middle_num
    return to_return


def get_lat_long(ip_addr):
    # check if the lat-long of the ip address is already loaded in our
    # database
    
    num_ip_addr = ip_addr_to_num(ip_addr)
    ip_range_list = models.IPRange.objects.filter(
        lower_bound__lte = num_ip_addr, upper_bound__gte = num_ip_addr)

    ip_range_list = sorted(
        ip_range_list,
        key = lambda ip_range : (ip_range.upper_bound - ip_range.lower_bound))

    if len(ip_range_list) != 0:
        ip_range = ip_range_list[0]
        return [ip_range.latitude, ip_range.longitude]
    

    # ip addr not located in db.  Check with external service for ip
    # address
    # http://freegeoip.net/{format}/{ip_or_hostname}
    # return 37.426, -122.17054
    conn = httplib.HTTPConnection("freegeoip.net")
    conn.request("GET", "/json/" + ip_addr)
    resp = conn.getresponse()
    py_data = json.loads(resp.read())
    conn.close()

    return py_data['latitude'], py_data['longitude']
    


if __name__ == '__main__':
    print '\n\n'
    print get_lat_long('171.67.76.132')
    print '\n\n'
