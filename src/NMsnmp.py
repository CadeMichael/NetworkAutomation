import asyncio
import json
from puresnmp import Client, V2C, PyWrapper
import matplotlib.pyplot as plt
import numpy as np

"""
easy snmp did not install, this pacakge has terrible documentation but seems to work
> https://puresnmp.readthedocs.io/en/latest/api/puresnmp.html#puresnmp.Client.walk
"""

result = {}

"""
I can't seem to get the Ipv6 addresses so I left it with IPv4, but was able to do
the plots.
"""

async def getIPs(host, name):
    result[name] = {}
    client = PyWrapper(Client(host, V2C("cade1999")))

    interfaces = {}
    async for item in client.walk('.1.3.6.1.2.1.2.2.1.2'):
        ifindex = item.oid.split('.')[-1]
        interfaces[ifindex] = item.value.decode()

    intIpv4 = client.walk("1.3.6.1.2.1.4.20.1.2")
    async for ip in intIpv4:
        v4 = '.'.join(ip.oid.split(".")[-4:])
        fa = interfaces[str(ip.value)]
        result[name][fa] = {}
        result[name][fa]["v4"] = v4


async def runAll():
    await getIPs("10.0.0.5", "R5")
    await getIPs("198.51.100.4", "R4")
    await getIPs("10.0.0.4", "R3")
    await getIPs("10.0.0.1", "R2")
    await getIPs("172.16.0.1", "R1")
    return result

def save_to_json(fname):
    res = asyncio.run(runAll())
    json_str = json.dumps(res, indent=4)
    with open(fname, "w") as f:
        f.write(json_str)

async def cpu_data(ip):
    client = PyWrapper(Client(ip, V2C("cade1999")))
    data = []
    for i in range(0, 24):
        cpu = await client.get('.1.3.6.1.4.1.9.9.109.1.1.1.1.6.1')
        data.append(cpu)
        print(f"interval {i+1} out of {24}")
        await asyncio.sleep(5.0)
    plt.plot(range(0,24), data, marker='x')
    plt.title('R1 CPU usage over 2 minutes')
    plt.xlabel('5s interval')
    plt.ylabel('% usage')
    plt.savefig('usage.jpg')
    plt.show()

def make_cpu_plot():
    asyncio.run(cpu_data("172.16.0.1"))
