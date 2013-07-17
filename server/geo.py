#!/usr/bin/env python

import httplib
import json


def get_lat_long(ip_addr):
    # FIXME: use real values eventually

    conn = httplib.HTTPConnection("freegeoip.net")
    conn.request("GET", "/json/" + ip_addr)
    resp = conn.getresponse()
    py_data = json.loads(resp.read())
    conn.close()

    return py_data['latitude'], py_data['longitude']
    
    # print '\n\n'
    # print py_data
    # print '\n\n'
    # # http://freegeoip.net/{format}/{ip_or_hostname}
    # return 37.426, -122.17054



if __name__ == '__main__':
    print '\n\n'
    print get_lat_long('171.67.76.132')
    print '\n\n'
