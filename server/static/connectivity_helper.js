
/**
 * The purpose of this object type is to determine connectivity
 * information between connected hosts.  Then, color all connected
 * hosts the same.
 */
function ConnectivityHelper()
{
    // maps from ip_addr to host
    this.hosts_seen_dict = {};
    // maps from ip_addr to list of hosts
    this.host_connection_dict = {};
}

ConnectivityHelper.prototype.color = function(to_color_with)
{
    for (var host_ip_addr in this.hosts_seen_dict)
    {
        var host = this.hosts_seen_dict[host_ip_addr];

        if (host.traversed !== undefined)
            continue;

        var color = 'rgb(' +
            Math.round(Math.random()*256)+','+
            Math.round(Math.random()*256)+','+
            Math.round(Math.random()*256)+')';

        this.recursive_color(host,color);
    }


    // reset traversed to undefined
    for (host_ip_addr in this.hosts_seen_dict)
    {
        var host = this.hosts_seen_dict[host_ip_addr];
        host.traversed = undefined;
    }
};

/**
 * @param {Host object} host
 * 
 * @param {string} color
 * 
 * Color all nodes connected to host color.  Should not be called from
 * external code.
 */
ConnectivityHelper.prototype.recursive_color = function (host,color)
{
    host.color = color;
    if (host.traversed !== undefined)
        return;
    host.traversed = true;

    var conn_array = this.host_connection_dict[host.ip_addr];
    for (var i in conn_array)
    {
        var connected_host = conn_array[i];
        this.recursive_color(connected_host,color);
    }
};

ConnectivityHelper.prototype.add_link = function (host1,host2)
{
    this.add_host(host1);
    this.add_host(host2);

    this.host_connection_dict[host1.ip_addr].push(host2);
    this.host_connection_dict[host2.ip_addr].push(host1);
};

ConnectivityHelper.prototype.add_host = function (host)
{
    if (!(host.ip_addr in this.hosts_seen_dict))
    {
        this.hosts_seen_dict[host.ip_addr] = host;
        this.host_connection_dict[host.ip_addr] = [];
    }
};
