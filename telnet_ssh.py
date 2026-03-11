import tomllib
import threading

from netmiko import ConnectHandler

router = {
    "device_type": "cisco_ios_telnet",
    "host": "localhost",
    "port": 0,
    "username": "",
    "password": "",
    "secret": ""
}

def config(router, data, r):
    """
    modify router with data from toml and send config
    """
    router["port"] = data[r]["port"]
    print(router)
    ssh_commands = [
        f"hostname {r}",
        "ip domain-name LAB.LOCAL",
        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",
        "enable secret cade1999",
        "username admin password cade1999",
        "line vty 0 4",
        "transport input ssh",
        "login local",
    ]
    ip_commands = [
        f"int {data[r]["int"]}",
        f"ip address {data[r]["ip"]} {data[r]["mask"]}",
        "no shutdown",
    ]
    with ConnectHandler(**router) as conn:
        conn.enable()
        conn.send_config_set(ssh_commands)
        conn.set_base_prompt()
        conn.send_config_set(ip_commands)
        conn.disconnect()

with open("ssh_conf.toml", "rb") as f:
    data = tomllib.load(f)

    threads = []

    for r in data.keys():
        t = threading.Thread(target=config, args=(router.copy(),data,r))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
