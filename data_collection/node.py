import urllib
import urllib2
import time

class IPv4(object):
    def __init__(self,addr_str):
        '''
        Each octet is an integer from 0-255
        '''
        octets = addr_str.split('.')
        if len(octets) != 4:
            assert(False)
        self.octet1 = int(octets[0])
        self.octet2 = int(octets[1])
        self.octet3 = int(octets[2])
        self.octet4 = int(octets[3])

    def __str__(self):
        return (
            str(self.octet1) + '.' + str(self.octet2) + '.' +
            str(self.octet3) + '.' + str(self.octet4))
        
    def __hash__(self):
        return hash(str(self))

    def __eq__(self,eq_to):
        return str(self) == str(eq_to)
    
    def blue(self):
        if self.octet1 == 171:
            return 255
        return 0

    def green(self):
        return self.octet2

    def red(self):
        return self.octet3
    
        
class Node(object):
    next_id = 0
    
    def __init__(self,ip_addr_str,hostname=None):
        self.id = Node.next_id
        Node.next_id += 1
        
        self.ip_addr = IPv4(ip_addr_str)
        self.hostname = hostname
        # ip addresses to nodes
        self.connections = {}

    def bidirectional_add_connection(self,node):
        '''
        Adds self to node's connections.  Adds node to my connections.
        '''
        node.connections[self.ip_addr] = self
        self.connections[node.ip_addr] = node

    def node_size(self):
        if len(self.connections) == 0:
            return 1.0
        return len(self.connections)

    def export_connections(self,which_edge_exporting):
        all_connections = ''
        for conn_ip_addr in self.connections:
            connected_to_node = self.connections[conn_ip_addr]
            all_connections += '''
<edge id="%s" source="%s" target="%s" weight="1.0"/>
''' % (str(which_edge_exporting), str(self.id), str(connected_to_node.id))
            which_edge_exporting += 1

        return all_connections, which_edge_exporting
            
    
    def export_nodes (self):
        return '''
<node id="%s" label="%s">
<viz:size value="%s"/>
<viz:color b="%s" g="%s" r="%s"/>
<viz:position x="0.0" y="0.0" z="0.0"/>
</node>
''' % (str(self.id), str(self.ip_addr),
       str(self.node_size()),

       str(self.ip_addr.blue()), str(self.ip_addr.green()),
       str(self.ip_addr.red()))

def emit_http(all_nodes,addr_to_hit):
    counter = 0
    for single_node in all_nodes.values():
        print str(counter) + ' of ' + str(len(all_nodes))
        counter += 1
        for connected_to_node_ip in single_node.connections:
            connected_to_node = all_nodes[connected_to_node_ip]
            values = {
                'ip_addr_1' : str(single_node.ip_addr),
                'hostname_1' : str(single_node.hostname),

                'ip_addr_2' : str(connected_to_node.ip_addr),
                'hostname_2' : str(connected_to_node.hostname)
                }

            data = urllib.urlencode(values)
            # req = urllib2.Request(addr_to_hit, data)
            # response = urllib2.urlopen(req)
            response = urllib2.urlopen(addr_to_hit + '?' + data)
            the_page = response.read()
            

def emit_gexf(all_nodes,filename):
    '''
    @param {array} all_nodes --- Each element is a node
    '''
    filer = open(filename,'w')
    filer.write(header(len(all_nodes)))

    num_connections = 0
    for ip_addr in all_nodes:
        node = all_nodes[ip_addr]
        filer.write(node.export_nodes())
        num_connections += len(node.connections)
        
    filer.write('</nodes>\n')
    filer.write('<edges count="%s">' % str(num_connections))

    which_edge = 0
    for ip_addr in all_nodes:
        node = all_nodes[ip_addr]
        edge_text, which_edge = node.export_connections(which_edge)
        filer.write(edge_text)

    filer.write('</edges>')
    filer.write(footer())
    filer.flush()
    filer.close()


def footer ():
    return '''
    </graph>
    </gexf>'''

def header(num_nodes):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" version="1.1" xmlns="http://www.gexf.net/1.1draft">
<meta lastmodifieddate="2010-03-31+18:43">
<creator>Gephi 0.7</creator>
</meta>
<graph defaultedgetype="directed" idtype="string" type="static">
<attributes class="node" mode="static">
<attribute id="modularity_class" title="Modularity Class" type="integer"/>
</attributes>
<nodes count="%s">'''% str(num_nodes)
