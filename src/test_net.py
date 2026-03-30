import unittest
import csv

from netmiko import ConnectHandler

def parse_csv(file):
    """
    open given file and return an array of dicts representing csv info
    """
    with open(file, newline="") as csvconf:
        conf = csv.DictReader(csvconf)
        return [r for r in conf]

def router(routers, i):
    """
    given the routers array and index give the netmiko device config and extra
    information needed for testing such as loopback, area, etc
    """
    conf = {
        "device_type": "cisco_ios",
        "host": f"R{i+1}",
        "ip": routers[i]["Mgmt IP"],
        "username": routers[i]["Username"],
        "password": routers[i]["Password"],
        "secret": routers[i]["Password"],
        "port": 22,
    }
    extra = {
        "loop": routers[i]["Loopback IP"],
        "area": routers[i]["OSPF Area"],
        "network": routers[i]["Network"],

    }
    return (conf, extra)


class Stage4(unittest.TestCase):
    """
    run the three tests from stage 4
    """

    def test_r3_loop(self):
        routers = parse_csv("info.csv")
        conf, _ = router(routers, 2) 
        with ConnectHandler(**conf) as conn:
            conn.enable()
            # get ip's for router 3
            output = conn.send_command("show ip interface brief")
            # check that there is a looback ip of '10.1.3.1'
            self.assertIn("10.1.3.1", output)

    def test_r1_area(self):
        routers = parse_csv("info.csv")
        conf, _ = router(routers, 0)
        with ConnectHandler(**conf) as conn:
            conn.enable()
            # raw ospf debug info
            output = conn.send_command("show ip ospf")
            # find all lines with 'Area' text
            areas = [line for line in output.splitlines() if "Area" in line]
            # find all unique id's
            area_ids = set(line.split("Area")[1].strip().split()[0] for line in areas)
            # ensure there is only 1 unique id
            self.assertEqual(len(area_ids), 1)

    def test_r2_r5_ping(self):
        routers = parse_csv("info.csv")
        conf_r2, _ = router(routers, 1)
        _, extra_r5 = router(routers, 4)
        r5_loopback = extra_r5["loop"]
        with ConnectHandler(**conf_r2) as conn:
            conn.enable()
            # ping r5's loop with 5 attempts
            output = conn.send_command(f"ping {r5_loopback} repeat 5")
            # ensure the success markers '!' are present
            self.assertIn("!!!!!",  output)

if __name__ == "__main__":
    unittest.main()
