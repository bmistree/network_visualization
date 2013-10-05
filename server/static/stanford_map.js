
var COMPUTER_PNG_URL;
var COMPUTER_SMALL_PNG_URL;
var TO_SUBMIT_TO_URL;
var TO_GET_UPDATES_URL;

var DEFAULT_CENTER_LATITUDE;
var DEFAULT_CENTER_LONGITUDE;
var DEFAULT_ZOOM_LEVEL;
// true if should display satelite, false otherwise
var DEFAULT_MAP_SATELITE;

// how frequently to check for new updates
UPDATE_PERIOD_MS = 10000;


NOTIFICATION_AREA_DIV_ID = 'notification-area';

// each element is a Host object
var all_hosts = [];
// each link is an object with field a that is an ip address (string)
// and field b that is also an ip address (string)
var all_links = [];
var host_groups = [];
var host_ips_to_groups = {};
var markers_array = [];

var last_poll_time = null;

var map;

// true if map is expanded (next click on map expand will contract it
// to original size).
var map_expanded = false;

function map_initialize()
{
    var map_type_id = DEFAULT_MAP_SATELITE ?
        google.maps.MapTypeId.SATELLITE :
        google.maps.MapTypeId.ROADMAP;
    
    var map_options =  {
        zoom: DEFAULT_ZOOM_LEVEL,
        center: new google.maps.LatLng(
            DEFAULT_CENTER_LATITUDE, DEFAULT_CENTER_LONGITUDE),

        // mapTypeId: google.maps.MapTypeId.ROADMAP
        // mapTypeId: google.maps.MapTypeId.SATELLITE
        mapTypeId: map_type_id
    };
    map = new google.maps.Map(
        document.getElementById('map-canvas'),
        map_options);

    google.maps.event.addListener(
        map, 'zoom_changed',zoom_handler);


    $('#submitter').click(submit_listener);

    // listen for request to expand or contract map
    $('#map-expand').click(map_expand_clicked);
    
    query_server();
}

function map_expand_clicked()
{
    // message display at bottom of div holding map
    var click_text = 'Click here to contract map';
    var class_to_remove = 'map-parent';
    var class_to_add = 'overlay';
    if (! map_expanded)
    {
        click_text = 'Click here to expand map';
        var tmp = class_to_remove;
        class_to_remove = class_to_add;
        class_to_add = tmp;
    }

    $('#map-expand').html(click_text);
    $('#map-parent').removeClass(class_to_remove);
    $('#map-parent').addClass(class_to_add);
    
    google.maps.event.trigger(map, "resize");
    map_expanded = !map_expanded;
}


function query_server()
{
    var data = {};
    if (last_poll_time !== null)
        data['last_poll'] = last_poll_time;
    
    $.ajax(
        {
            type: "GET",
            url: TO_GET_UPDATES_URL,
            data: data,
            dataType: 'json',
            success: function(returned_data)
            {
                var nodes = returned_data.nodes;
                var links = returned_data.links;
                last_poll_time = returned_data.time_str;

                for (var node_index in nodes)
                {
                    var node = nodes[node_index];
                    add_host(node.latitude, node.longitude,node.ip_addr);
                }
                for (var link_index in links)
                {
                    var link = links[link_index];
                    add_link(link.a,link.b);
                }

                display_hosts();
                setTimeout(query_server,UPDATE_PERIOD_MS);
            }
        });
}


function submit_listener()
{
    // grab values from fields
    var ip_addr_1 = $('#ip_addr_1').val();
    var ip_addr_2 = $('#ip_addr_2').val();
    var hostname_1 = $('#hostname_1').val();
    var hostname_2 = $('#hostname_2').val();

    // clear input fields
    $('#ip_addr_1').val('');
    $('#ip_addr_2').val('');
    $('#hostname_1').val('');
    $('#hostname_2').val('');

    $.ajax(
        {
            type: "GET",
            url: TO_SUBMIT_TO_URL,
            data: {
                ip_addr_1: ip_addr_1,
                ip_addr_2: ip_addr_2,
                hostname_1: hostname_1,
                hostname_2: hostname_2
            }
        });

}


function zoom_handler()
{
    display_hosts();
}

function get_cluster_radius()
{
    var map_zoom = map.getZoom();
    // var sixteen_zoom = .002;
    var sixteen_zoom = .0002;
    var delta = 16 - map_zoom;
    return sixteen_zoom*Math.pow(2,delta);
}


function add_link(ip_addr_a,ip_addr_b)
{
    all_links.push(
        {
            a: ip_addr_a,
            b: ip_addr_b
        });
}

function add_host(latitude,longitude,title)
{
    var new_host = new Host(title,latitude,longitude);
    all_hosts.push(new_host);
}


/**
 * Clears existing markers and creates new ones.
 */
function display_hosts()
{
    host_groups = [];
    host_ips_to_groups = {};
    var cluster_radius = get_cluster_radius();
    
    // create first group before getting rid of previous
    for (var index = 0; index < all_hosts.length;++index)
    {
        var added = false;
        var host_to_add = all_hosts[index];
        for (var hg_index = 0; hg_index < host_groups.length; ++hg_index)
        {
            var host_group = host_groups[hg_index];
            
            if (host_group.add_if_can(host_to_add,cluster_radius))
            {
                host_ips_to_groups[host_to_add.ip_addr] = host_group;
                added = true;
                break;
            }
        }
        if (! added)
        {
            if ((host_to_add.latitude == -1) &&
                (host_to_add.longitude == -1))
                continue;
            
            var host_group = new HostGroup(
                host_to_add.latitude,host_to_add.longitude);
            host_ips_to_groups[host_to_add.ip_addr] = host_group;
            host_groups.push(host_group);
            // ensure adding by putting a number > 0 as second arg.
            host_group.add_if_can(host_to_add,10);
        }
    }

    // create connections between hosts
    var to_draw_func = create_connections_between_hosts();
    clear_markers();
    to_draw_func();

    for (var hg_index=0; hg_index < host_groups.length; ++hg_index)
    {
        var host_group = host_groups[hg_index];
        host_group.draw(map);
    }
}

function create_connections_between_hosts()
{
    var links_to_draw = {};
    for (var link_index =0; link_index< all_links.length; ++link_index)
    {
        var link = all_links[link_index];
        var group_a = host_ips_to_groups[link.a];
        var group_b = host_ips_to_groups[link.b];

        if ((group_a === undefined) || (group_b === undefined))
            continue;
        
        if (group_b.id < group_a.id)
        {
            var tmp = group_b;
            group_b = group_a;
            group_b = tmp;
        }
        var link_hash = group_a.id + '|' + group_b.id;
        if (! (link_hash in links_to_draw))
        {
            links_to_draw[link_hash] = {
                group_a: group_a,
                group_b: group_b,
                count: 0
                };
        }
        links_to_draw[link_hash].count += 1;
    }

    return function()
    {
        for (var link_to_draw_index in links_to_draw)
        {
            var link_to_draw = links_to_draw[link_to_draw_index];
            var group_a = link_to_draw.group_a;
            var group_b = link_to_draw.group_b;
            var path = [
                new google.maps.LatLng(
                    group_a.center_latitude,group_a.center_longitude),
                new google.maps.LatLng(
                    group_b.center_latitude,group_b.center_longitude)];

            // FIXME: use count for strokeWeight
            var link_line = new google.maps.Polyline(
                {
                    path: path,
                    strokeColor: "#FF0000",
                    strokeOpacity: 1.0,
                    strokeWeight: 2,
                    map: map
                });
            markers_array.push(link_line);
        }
    };
}

function clear_markers()
{
    for (var i = 0; i < markers_array.length; i++ )
        markers_array[i].setMap(null);

    markers_array = [];
}

