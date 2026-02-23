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
        devices = debug.split("\n")
        for i in range(0, len(devices)):
            if "R5" in devices[i]:
                return devices[i+2].strip().split(" ")[2]

    except Exception as e:
        print("unable to find ip for R5")
        print(e)

def connR5(ip):
    try:
        R5 = {
            'device_type': 'cisco_ios',
            'ip' : ip,
            'username': 'admin',
            'password': 'cade1999',
            'secret': 'cade1999',
        }
        conn = ConnectHandler(**R5)
        conn.enable()
        debug = conn.send_command("show ipv6 int brief")
        print(debug)
        conn.disconnect()
    except Exception as e:
        print(f"unable to connect to and configure R5 @ {ip}")
        print(e)

