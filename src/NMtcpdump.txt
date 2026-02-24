from scapy.all import IPv6, rdpcap, in6_addrtomac

"""
I did not want to do manual IPv6 EUI 64 deconstruction so I spent some time
looking into scapy docs and found the following.

https://scapy.readthedocs.io/en/latest/api/scapy.utils6.html
> provides the 'in6_addrtomac' function
"""

# hard coded
c1Ping = 'c1ping.pcap'
tap0 = "ea:1a:50:73:a3:7a" # from 'ip addr show'

def getMacs(pcap_f: str, tap0_mac: str) -> set[str]:
    """
    given
        - a pcap file name 
        - mac address of 'tap0'
    return
        - set of mac addresses that pinged 'tap0'
    """
    c1Ping = rdpcap(pcap_f)
    tap0 = tap0_mac

    macs = set()

    for frame in c1Ping:
        if IPv6 in frame:
            src = frame[IPv6].src
            mac = in6_addrtomac(src)
            if mac != tap0:
                macs.add(mac)

    print(macs)
    return macs
