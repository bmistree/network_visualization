from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponse
import models
import re, json
import datetime
import settings
from geo import get_lat_long
from get_host_from_ip import get_hostname

def index(request):
    if request.user.is_authenticated():
        models.UserProfile.check_create_user_profile(request.user)

    render_params = {
        'default_center_latitude': settings.MAP_DEFAULT_LATITUDE,
        'default_center_longitude': settings.MAP_DEFAULT_LONGITUDE,
        'default_zoom_level': settings.MAP_DEFAULT_ZOOM,
        'default_map_satelite': 1 if settings.MAP_DEFAULT_SATELITE else 0
        }
    
    return render_to_response(
        'main.html',render_params,
        context_instance=RequestContext(request))

def add_links_response(str_msg):
    return HttpResponse(str_msg,mimetype='text/html')

def add_links_no_user(request):
    return add_links(request,False)

def add_links(request,check_user=False):
    '''
    Called in response to get
    '''
    if check_user:
        if not request.user.is_authenticated():
            return HttpResponse('Must log in to add links',mimetype='text/html')
        
    ip1 = request.GET.get('ip_addr_1',None)
    ip2 = request.GET.get('ip_addr_2',None)
    
    hostname1 = request.GET.get('hostname_1',None)
    hostname2 = request.GET.get('hostname_2',None)
    
    node1,new_node1 = add_node(ip1,hostname1)

    if node1 == None:
        return add_links_response('require first hostname and ip addr to be specified')
    
    node2,new_node2 = add_node(ip2,hostname2)

    new_link = False
    if node2 != None:
        # create a link
        new_link = create_link(node1,node2)

    msgs_to_display = []
    
    if not new_node1:
        msgs_to_display.append(
            'Already had a node with ip address ' + str(ip1) + '.  Keep trying.')
        
    else:
        msg = (
            'You were the first to upload node with ip address ' + str(ip1) +
            '!')
        msgs_to_display.append(msg)
        
        
    if (ip2 != None) and (ip2 != ''):
        if not new_node2:
            msg = (
                'Already had a node with ip address ' + str(ip2) +
                '.  Keep trying.')
            msgs_to_display.append(msg)
        else:
            msg = (
                'You were the first to upload node with ip address ' + str(ip2) +
                '!')
            msgs_to_display.append(msg)

        if not new_link:
            msg = (
                'Already had link between ' + str(ip1) + ' and ' + str(ip2) + '.  Keep trying.'
                )
            msgs_to_display.append(msg)
        else:
            msgs = 'You were the first to upload link between ' + str(ip1)
            msgs += ' and ' + str(ip2) + '!  Hit refresh to view.'
            msgs_to_display.append(msg)

            
    return add_links_response(msgs_to_display)


def create_link(node1, node2):

    user = None
    if request.user.is_authenticated():
        user = request.user
    
    # check if link already exists
    # all_links = node1.link_set.all()
    all_one_way_links = node1.node1.all()
    for link in all_one_way_links:
        if ((link.node1.ip_addr == node2.ip_addr) or
            (link.node2.ip_addr == node2.ip_addr)):
            link.increment_and_check_authenticate(user)
            return False


    all_other_way_links = node1.node2.all()
    for link in all_other_way_links:
        if ((link.node1.ip_addr == node2.ip_addr) or
            (link.node2.ip_addr == node2.ip_addr)):
            link.increment_and_check_authenticate(user)
            return False

    link = models.Links(node1=node1,node2=node2)
    link.save()
    link.increment_and_check_authenticate(user)
    return True

def get_updates_from(updates_since):
    '''
    @param {string or None} --- If None, get all updates since service
    started.  If string, string is formatted as a datetime.  Convert
    to datetime, and get all entries since then and return them.

    @returns json string
    '''

    if updates_since is None:
        links = models.Links.objects.all()
        nodes = models.Node.objects.all()
    else:
        dt = datetime.datetime.strptime(updates_since, '%Y-%m-%d %H:%M:%S')
        links = models.Links.objects.filter(creation_date__gte = dt, authenticated=True)
        nodes = models.Node.objects.filter(creation_date__gte = dt, authenticated=True)
        
    time_str = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_links = []
    updated_nodes = []

    for link in links:
        updated_links.append({
                'a': link.node1.ip_addr,
                'b': link.node2.ip_addr,
                })

    for node in nodes:
        updated_nodes.append({
                'latitude': node.latitude,
                'longitude': node.longitude,
                'ip_addr': node.hostname
                })

    update_map = {
        'nodes': updated_nodes,
        'links': updated_links,
        'time_str': time_str}
    
    return json.dumps(update_map)

def scoreboard(request):
    render_params = {
        'users': models.UserProfile.objects.all()
        }
    
    return render_to_response(
        'scoreboard.html',render_params,
        context_instance=RequestContext(request))
    
    
def get_updates(request):
    '''
    Returns updates since last time polled
    '''
    last_time_polled = request.GET.get('last_poll',None)
    updates = get_updates_from(last_time_polled)
    return HttpResponse(updates,mimetype='appliction/json')
    

def add_node(ip,hostname):
    '''
    @returns a,b ---
    
       a {None or Node} --- If ip isn't well formatted or hostname
       isn't well formatted, returns None.  Otherwise, creates a node
       if there isn't one with the existing ip or gets the one with
       the existing ip.

       b {bool} --- True if created a new node.  False otherwise.
    '''

    user = None
    if request.user.is_authenticated():
        user = request.user

    if hostname == None:
        return None,False

    if hostname == '':
        return None,False

    canon_ip = canonicalize_ip(ip)
    if canon_ip == None:
        return None,False

    # previously, nodes were uniquely identified by their ip
    # addresses.  Changing so that now they'll be uniquely identified
    # by hostname.
    hostname = get_hostname(canon_ip)
    if hostname == '':
        return None,False
    
    nodes = models.Node.objects.filter(hostname=hostname)
    if len(nodes) == 0:
        latitude, longitude = get_lat_long(canon_ip)
        node = models.Node(
            hostname=hostname,ip_addr=canon_ip,latitude=latitude,
            longitude=longitude)
        node.save()
        node.increment_and_check_authenticate(user)
        return node,True
    else:
        # increment the number of adders for this node
        node = nodes[0]
        node.increment_and_check_authenticate(user)
    
    return nodes[0],False


def canonicalize_ip(ip_addr):
    '''
    @param{String or None} ip_addr --- Check if it's a valid ip
    address in valid form.  If it is not, return None.  Otherwise,
    return it's standard representation as a string.
    '''
    if ip_addr == None:
        return None

    reg_exp = '^(\d+\.\d+\.\d+\.\d+)$'    
    matches = re.findall(reg_exp,ip_addr)

    if len(matches) == 0:
        return None

    return matches[0]
    

