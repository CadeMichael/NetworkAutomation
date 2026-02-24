import asyncio

import NMdhcp
import NMsnmp
import NMgithub

def main():
    # get Router 5's ip
    r5_ip = NMdhcp.findR5()
    # configure DHCPv4
    NMdhcp.R5_dhcp_server(r5_ip)
    # save router IP's to json
    NMsnmp.save_to_json("json_str.txt")
    # make a plot
    asyncio.run(NMsnmp.cpu_data("172.16.0.1"))
    # add / commit / push git changes
    NMgithub.push_changes()

if __name__ == "__main__":
    main()
