import csv
import sys

from ncclient import manager
from ncclient.xml_ import to_ele

# import logging
# logging.basicConfig(level=logging.DEBUG)

def get_data(m, show_cmd):
    rpc = to_ele(("""
    <rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <get>
        <filter>
          <oper-data-format-text-block xmlns="http://www.cisco.com/cpi_10/schema">
            <show>{}</show>
          </oper-data-format-text-block>
        </filter>
      </get>
    </rpc>
    """).format(show_cmd))
    m._session.send(rpc)
    import time; time.sleep(2)
    return m._session._buffer.getvalue().decode()

def parse_csv(file):
    with open(file, newline="") as csvconf:
        conf = csv.DictReader(csvconf)
        return [r for r in conf]

def netconf_config(file):
    ospf_mask = {'24' : '0.0.0.255'}
    ip_mask = {'24':'255.255.255.0'}
    routers = parse_csv(file)
    loop_conf = """
    interface loopback 99
    ip address {} {}
    no shutdown
    """
    ospf_conf = """
    router ospf 10
    network {} {} area {}
    """
    vals = ["index", 'hostname', 'loop_ip', 'ospf_area', 'ospf advertisement']
    print('| {:^5} | {:^8} | {:^8} | {:^7} | {:^9} |'.format(*vals))
    for i,r in enumerate(routers):
        m = manager.connect(
            host=f"198.51.100.1{i+1}",
            port="22",
            username="lab",
            password="lab123",
            timeout=10,
            hostkey_verify=False,
            look_for_keys=False,
            allow_agent=False,
            device_params={"name": "csr"},
        )
        (l_ip,l_mask) = r['loop_ip'].split("/")
        (a_ip,a_mask) = r['loop_ip'].split("/")
        l_mask = ip_mask[l_mask]
        a_mask = ospf_mask[a_mask]
        hname_rpc = to_ele(
            ("""
            <config>
              <cli-config-data-block>
                hostname {}
              </cli-config-data-block>
            </config>
            """).format(r['hostname']))
        loop_rpc = to_ele(
            ("""
             <config>
                <cli-config-data-block>
                {}
                </cli-config-data-block>
             </config>
             """).format(loop_conf.format(l_ip, l_mask))
        )
        # print(ospf_conf.format(a_ip, a_mask, r['ospf_area']))
        ospf_rpc = to_ele(
            ("""
             <config>
                <cli-config-data-block>
                {}
                </cli-config-data-block>
             </config>
             """).format(ospf_conf.format(a_ip, a_mask, r['ospf_area']))
        )
        # i can't fetch with netconf due to the cisco version
        # so I opted to check for confirmation that the config took effect
        ok = "<ok />" in str(m.edit_config(hname_rpc, target="running"))
        ok = ok and "<ok />" in str(m.edit_config(loop_rpc, target="running"))
        ok = ok and "<ok />" in str(m.edit_config(ospf_rpc, target="running"))
        if not ok:
            raise ValueError("Failed to send configuration")
        vals = [i+1, r['hostname'], l_ip, r['ospf_area'], a_ip]
        print('| {:^5} | {:^8} | {:^8} | {:^9} | {:^18} |'.format(*vals))

if __name__ == "__main__":
    file = sys.argv[1]
    netconf_config(file)
    print(("{:^58}").format("==All Routers Succesfully Configured=="))
