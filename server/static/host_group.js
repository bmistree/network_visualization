var markers_array;
var all_links;
SIGMA_CANVAS_ID = 'sigma-canvas';
var highlighted_subgroup = null;


function Host(ip_addr,latitude,longitude)
{
    this.ip_addr = ip_addr;
    this.latitude = latitude;
    this.longitude = longitude;

    // for sigma.js library 
    this.x = Math.random();
    this.y = Math.random();
    this.size = 5.5;

    this.label = this.ip_addr;
    
    this.color = 'rgb(' +
        Math.round(Math.random()*256)+','+
        Math.round(Math.random()*256)+','+
        Math.round(Math.random()*256)+')';
}


var _host_group_uid_generator = 0;
/**
 * Each host group contains a list of hosts
 */
function HostGroup(center_lat,center_long)
{
    this.id = ++_host_group_uid_generator;
    this.hosts_in_group = [];
    this.hosts_in_group_dict = {};
    this.center_latitude = center_lat;
    this.center_longitude = center_long;
}

/**
 * @returns {bool} --- True could add to host group.  False otherwise.
 */
HostGroup.prototype.add_if_can = function(host_to_add,within_radius_lat_long)
{
    var within_radius_squared = within_radius_lat_long*within_radius_lat_long;

    var dist_squared = distance_squared(
        host_to_add.latitude, host_to_add.longitude,
        this.center_latitude, this.center_longitude);

    if (dist_squared < within_radius_squared)
    {
        this.hosts_in_group.push(host_to_add);
        this.hosts_in_group_dict[host_to_add.ip_addr] = host_to_add;
        return true;
    }

    return false;
};

HostGroup.prototype.host_in_group = function(ip_addr)
{
    return ip_addr in this.hosts_in_group_dict;
};

HostGroup.prototype.draw = function(map)
{
    this._draw_icon(map);
    this._draw_circle(map);
};

HostGroup.prototype._draw_icon = function (map)
{
    var lat_long = new google.maps.LatLng(
        this.center_latitude,this.center_longitude);
    
    var comp_marker = new google.maps.Marker(
        {
            position: lat_long,
            map: map,
            icon: COMPUTER_SMALL_PNG_URL
        });
    markers_array.push(comp_marker);

    var this_param = this;
    google.maps.event.addListener(
        comp_marker,'mouseover',
        function()
        {
            var msg = 'Cluster has ' + this_param.hosts_in_group.length + ' hosts';
            msg += '<ul>';
            for (var host_index = 0; host_index < this_param.hosts_in_group.length;
                 ++host_index)
            {
                var host = this_param.hosts_in_group[host_index];
                msg += '<li>';
                msg += host.ip_addr;
                msg += '</li>';
            }
            msg += '</ul>';

            if (highlighted_subgroup !== null)
                comp_marker.setIcon(COMPUTER_SMALL_PNG_URL);
            
            comp_marker.setIcon(COMPUTER_PNG_URL);
            highlighted_subgroup = comp_marker;
            
            // also draw the network for the moused-over part
            this_param.draw_subgraph();
        });
};


/**
 * {list} all_links --- Uses global all_links.  Each element is an
 * object that has two fields, a and b.  Each is a string ip address
 * for a host.
 * 
 * Runs through list.  Collects each link between hosts in the host
 * group.  Then, draws a connectivity graph in div.
 */
HostGroup.prototype.draw_subgraph = function()
{
    // clear previous sigma drawing
    $('#' + SIGMA_CANVAS_ID).empty();

    // draw new drawing
    var inner_group_links = [];
    for (var link_index in all_links)
    {
        var link = all_links[link_index];
        if ( (link.a in this.hosts_in_group_dict) &&
             (link.b in this.hosts_in_group_dict))
        {
            inner_group_links.push(link);
        }
    }

    // load into sigma.js
    var sigma_inst = sigma.init(
        document.getElementById(SIGMA_CANVAS_ID))
        .drawingProperties(
            {
                defaultLabelColor: '#fff'
            });

    // load hosts into nodes of sigma.js
    for (var host_index in this.hosts_in_group)
    {
        var host = this.hosts_in_group[host_index];
        sigma_inst.addNode(host.ip_addr,host);
    }
    
    // load edges into relevant edges of sigma.js
    for (var inner_link_index in inner_group_links)
    {
        var inner_link = inner_group_links[inner_link_index];
        sigma_inst.addEdge(inner_link_index,inner_link.a,inner_link.b);
    }
    sigma_inst.startForceAtlas2();

    setTimeout(
        function()
        {
            sigma_inst.stopForceAtlas2();
        }, 3000);
    
    // sigma_inst.draw();

};



HostGroup.prototype._draw_circle = function (map)
{
    var circle_radius = get_circle_radius(map,this.hosts_in_group.length);
    var lat_long = new google.maps.LatLng(
        this.center_latitude,this.center_longitude);
    var marker = new google.maps.Circle(
        {
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 1,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
            map: map,
            center: lat_long,
            radius: circle_radius
        });
    markers_array.push(marker);
};

MAX_SIZE_TO_HOST = 20;
function get_circle_radius(map,num_hosts)
{
    var normalized_size = Math.min(1, num_hosts/MAX_SIZE_TO_HOST);
    var map_zoom = map.getZoom();
    var sixteen_zoom = 100;
    var delta = 16 - map_zoom;
    return sixteen_zoom*Math.pow(2,delta)*normalized_size;
}


function distance_squared(ax,ay,bx,by)
{
    var dx = ax - bx;
    var dy = ay - by;
    return dx*dx + dy*dy;
}