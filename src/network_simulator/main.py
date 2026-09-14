from network_simulator.host import Host
from network_simulator.switch import Switch
from network_simulator.router import Router
from network_simulator.other import IP
from network_simulator.node import Node

if __name__ == "__main__":
    # LAN 1
    PC1 = Host("PC3", 1)
    SW1 = Switch("SW1", 8)

    # LAN 2
    PC2 = Host("PC2", 1)
    SW2 = Switch("SW2", 4)

    PC1.assign_all_int_attributes(
        0, "aaaa.aaaa.aaaa", IP("10.0.0.1"), IP("255.255.255.0"), IP("192.168.1.254")
    )
    PC2.assign_all_int_attributes(
        0, "bbbb.bbbb.bbbb", IP("10.0.1.1"), IP("255.255.255.0"), IP("192.168.2.254")
    )

    R1 = Router("R1", 4)
    R1.assign_all_int_attributes(
        0, "zzzz.zzzz.zzzz", IP("192.168.1.254"), IP("255.255.255.0")
    )
    R1.assign_all_int_attributes(
        1, "yyyy.yyyy.yyyy", IP("192.168.2.254"), IP("255.255.255.0")
    )

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW2, 0)

    SW1.add_connection(1, R1, 0)
    SW2.add_connection(1, R1, 1)

    PC1.send_message("test", 0, IP("192.168.2.1"))
    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test"
