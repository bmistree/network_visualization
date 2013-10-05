#!/usr/bin/env python

import socket

def get_hostname(ip_addr):
    hostnmae = ''
    try:
        hostname,_,_ = socket.gethostbyaddr(ip_addr)
    except:
        pass
    return hostname


if __name__ == '__main__':
    import sys
    ip_addr = sys.argv[1]
    print '\n\n'
    print get_hostname(ip_addr)
    print '\n\n'
