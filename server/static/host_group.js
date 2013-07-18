var markers_array;

function Host(ip_addr,latitude,longitude)
{
    this.ip_addr = ip_addr;
    this.latitude = latitude;
    this.longitude = longitude;
}


var _host_group_uid_generator = 0;
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
            
            $('#' + NOTIFICATION_AREA_DIV_ID).html(msg);
            comp_marker.setIcon(COMPUTER_PNG_URL);
        });
    google.maps.event.addListener(
        comp_marker,'mouseout',
        function()
        {
            $('#' + NOTIFICATION_AREA_DIV_ID).html('');
            comp_marker.setIcon(COMPUTER_SMALL_PNG_URL);
        });
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

MAX_SIZE_TO_HOST = 100;
function get_circle_radius(map,num_hosts)
{
    var normalized_size = Math.min(1, num_hosts/MAX_SIZE_TO_HOST);
    var map_zoom = map.getZoom();
    var sixteen_zoom = 1200;
    var delta = 16 - map_zoom;
    return sixteen_zoom*Math.pow(2,delta)*normalized_size;
}


function distance_squared(ax,ay,bx,by)
{
    var dx = ax - bx;
    var dy = ay - by;
    return dx*dx + dy*dy;
}