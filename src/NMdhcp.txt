import re
from netmiko import ConnectHandler
from NMtcpdump import getMacs, c1Ping, tap0

"""
> old implementation
> too brittle because after ip links become stale they don't show up
> after looking into cisco commands (link in lab report) I went with
>> "show cdn neighbors detail"

def findR5():
    try:
        R4 = {
            'device_type': 'cisco_ios',
            'ip' : '198.51.100.4',
            'username': 'admin',
            'password': 'cade1999',
            'secret': 'cade1999',
        }
        conn = ConnectHandler(**R4)
        conn.enable()
        
        macs = list(getMacs(c1Ping, tap0))
        debug = conn.send_command("show ipv6 neighbors")
        conn.disconnect()
        # make mac addrs of r2 and r3 look like link-locals
        macs[0] = macs[0].replace(':', '')
        macs[1] = macs[1].replace(':', '')
        m1 = macs[0][0:4] + "." + macs[0][4:8] + "." + macs[0][8:]
        m2 = macs[1][0:4] + "." + macs[1][4:8] + "." + macs[1][8:]
        # check each neighbor
        for line in debug.split('\n')[1:]:
            # shouldn't be R4's fa1/0 which was needed to connect to C1
            # shouldn't be R2 or R3 which only leaves R5
            # should not be link local address
            if line and not(m1 in line or m2 in line or "Fa1/0" in line or "FE80" in line):
                return line.split()[0] # R5 ip by process of elimination


    except Exception as e:
        print("unable to find ip for R5")
        print(e)
"""

R4 = {
    'device_type': 'cisco_ios',
    'ip' : '198.51.100.4',
    'username': 'admin',
    'password': 'cade1999',
    'secret': 'cade1999',
}

def findR5():
    try:
        conn = ConnectHandler(**R4)
        conn.enable()
        
        debug = conn.send_command("show cdp neighbors detail")
        conn.disconnect()
        ip_raw = re.search(r"IPv6 address: [\w\d:]+", debug)
        ip = ip_raw.group(0).split(" ")[2]
        return ip

    except Exception as e:
        print("unable to find ip for R5")
        print(e)

def R5_dhcp_server(ip):
    try:
        R5 = {
            'device_type': 'cisco_ios',
            'ip' : ip,
            'username': 'admin',
            'password': 'cade1999',
            'secret': 'cade1999',
        }
        macs = list(getMacs(c1Ping, tap0))
        conn = ConnectHandler(**R5)
        conn.enable()
        conn.send_config_set([
            "int f0/0",
            "ip address 10.0.0.5 255.255.255.0",
            "no shutdown",
        ])
        conn.send_config_set([
            # config R2 with it's mac
            'ip dhcp pool R2-F0/0',
            'host 10.0.0.2 255.255.255.0',
            f'hardware-address {macs[0]}',
            # config R3 with it's mac
            'ip dhcp pool R3-F0/0',
            'host 10.0.0.3 255.255.255.0',
            f'hardware-address {macs[1]}',
            # dynamic config for R4
            'ip dhcp pool R4-F0/0',
            'network 10.0.0.0 255.255.255.0',
            'ip dhcp excluded-address 10.0.0.2 10.0.0.4',
        ])

        dhcp_bindings = conn.send_command("show ip dhcp binding")
        conn.disconnect()
        ips = re.findall(r"10.\d+.\d+.\d+", dhcp_bindings)
        print(f"IPs from R5 DHCP bindings {ips}")
        return ips

    except Exception as e:
        print(f"unable to connect to and configure R5 @ {ip}")
        print(e)

