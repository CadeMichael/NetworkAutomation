from netmiko import ConnectHandler
from NMtcpdump import getMacs, c1Ping, tap0

def findR5():
    try:
        R4 = {
            'device_type': 'cisco_ios',
            # 'ip' : '2001:DB8:1:0:C805:31FF:FEFC:0',
            'ip' : '198.51.100.4',
            'username': 'admin',
            'password': 'cade1999',
            'secret': 'cade1999',
        }
        conn = ConnectHandler(**R4)
        conn.enable()
        
        macs = list(getMacs(c1Ping, tap0))
        debug = conn.send_command("show ipv6 neighbors")
        # print(debug)
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

        conn.disconnect()

    except Exception as e:
        print(e)

