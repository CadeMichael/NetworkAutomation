from ncclient import manager
from ncclient.xml_ import to_ele

def demo(host, user, password, loopback_num, ip, mask):
    m = manager.connect(
        host=host,
        port="22",
        username=user,
        password=password,
        timeout=10,
        hostkey_verify=False,
        look_for_keys=False,
        allow_agent=False,
        device_params={"name": "csr"},
    )
    print(m.connected)
    for c in m.server_capabilities:
        print(c)
    rpc1 = to_ele("""
    <filter>
      <oper-data-format-text-block xmlns="http://www.cisco.com/cpi_10/schema">
        <show>ip interface brief</show>
      </oper-data-format-text-block>
    </filter>
    """)
    rpc = to_ele("""
    <config>
      <cli-config-data-block>
        hostname Router2
      </cli-config-data-block>
    </config>
    """)
    print(m.edit_config(rpc, target="running"))
    print(m.get(filter=rpc1)) # error message-id

if __name__ == "__main__":
    demo("198.51.100.12", "lab", "lab123", 1, "10.1.1.1", "255.255.255.0")
