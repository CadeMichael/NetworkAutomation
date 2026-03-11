import argparse
import csv
import subprocess
import threading
import tomllib
import yaml

from netmiko import ConnectHandler

def gen_vars():
    # hold router variables
    routers = {}
    # read csv and convert to python dict
    with open("config.csv", newline="") as csvconf:
        conf = csv.DictReader(csvconf)
        conf_data = [r for r in conf]
        # merge router entries
        for r in conf_data:
            hname = r["hostname"]
            # init router single params
            if hname not in routers:
                routers[hname] = {
                    "hostname": hname,
                    "ospf": r["ospf"],
                    "ospfID": r["ospf_proc"],
                    "ospfArea": r["ospf_area"],
                    "loopID": r["int_name"],
                    "loopIP": r["ip"].split("/")[0],
                    "interfaces": [],
                }
            else:
                # add additional interface to router
                ip = r["ip"].split("/")
                ip_address = ip[0]
                subnet = ".".join(ip_address.split(".")[:-1] + ["0"])
                routers[hname]["interfaces"] += [
                    {
                        "ip": ip_address,
                        "subnet": subnet,
                        "type": r["int_type"],
                        "id": r["int_name"],
                    }
                ]

    # open vars/main.yml and populate with configuration data
    with open("./roles/router/vars/main.yml", "w") as yamlvars:
        yaml.dump(
            {"routerConf": list(routers.values())}, yamlvars, default_flow_style=False
        )


def send_config(router):
    """
    send corresponding router config to router
    """
    print(router)
    conf_file = f"./{router["host"]}.conf"
    print(f"==sending {conf_file}==")
    with ConnectHandler(**router) as conn:
        conn.enable()
        conn.send_config_from_file(conf_file)
    print(f"sent {conf_file} ✓")


def load_confs():
    """
    load each routers respective config concurrently
    """
    device = {
        "device_type": "cisco_ios",
        "host": "",
        "ip": "",
        "username": "admin",
        "password": "cade1999",
        "secret": "cade1999",
        "port": 22,
    }
    with open("../ssh_conf.toml", "rb") as f:
        data = tomllib.load(f)
    threads = []
    for r in data.keys():
        # copy the dict so threads don't mutate it at the same time
        router = device.copy()
        # update with router specific info
        router["host"] = r
        router["ip"] = data[r]["ip"]
        # create thread and add to thread list
        t = threading.Thread(target=send_config, args=(router,))
        t.start()
        threads.append(t)
    # execute threads
    for t in threads:
        t.join()


def main(vars, ansible, load):
    if vars:
        print("==generating './roles/routers/vars/main.yml'==")
        gen_vars()
        print("==done==")
    if ansible:
        print("==running ansible==")
        subprocess.run(["ansible-playbook", "site.yml"])
    if load:
        print("==loading the following configs==")
        with open("./R1.conf", "r") as r1:
            print("===router 1===")
            print(r1.read())
        with open("./R2.conf", "r") as r2:
            print("===router 2===")
            print(r2.read())
        with open("./R3.conf", "r") as r3:
            print("===router 3===")
            print(r3.read())
        load_confs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="jinja config file lab",
        description="generate router configs and load onto routers",
    )
    parser.add_argument("-v", "--vars", action="store_true")
    parser.add_argument("-a", "--ansible", action="store_true")
    parser.add_argument("-l", "--load", action="store_true")

    args = parser.parse_args()
    main(args.vars, args.ansible, args.load)
