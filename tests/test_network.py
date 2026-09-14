from network_simulator.node import Node
from network_simulator.other import *
from network_simulator.host import Host
from network_simulator.router import Router
from network_simulator.switch import Switch
import pytest


def test_initializes_correct_num_interfaces():
    node = Host("N1", 8)
    assert len(node.interfaces) == 8


def test_assigns_correct_interface_ids():
    node = Host("N1", 8)
    i = 0
    for interface in node.interfaces:
        assert interface.id == i
        i += 1


def test_port_map_contains_correct_interfaces():
    node = Host("N1", 8)
    for port, interface in node.port_map.items():
        assert port == interface.id


def test_interfaces_start_with_no_connections():
    node = Host("N1", 8)
    for self_interface in node.interfaces:
        assert node.interfaces[self_interface] is None


def test_connections_create_twoway_connection():
    node1 = Host("N1", 8)
    node2 = Host("N2", 4)

    node1.add_connection(1, node2, 3)

    # Node interfaces connect to correct nodes
    assert node1.interfaces[node1.port_map[1]].node == node2
    assert node2.interfaces[node2.port_map[3]].node == node1

    # Node interfaces connect to correct ports
    assert node1.interfaces[node1.port_map[1]].id == 3
    assert node2.interfaces[node2.port_map[3]].id == 1


def test_host_to_host_communication():
    PC1 = Host("PC1", 1)
    PC2 = Host("PC2", 1)
    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("10.0.0.1"), IP("255.255.255.0"), IP("192.168.1.254"))
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("10.0.0.2"), IP("255.255.255.0"), IP("192.168.1.254"))
    PC1.add_connection(0, PC2, 0)

    PC1.send_message("test", 0, IP("10.0.0.2"))

    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test"


def test_inter_subnet_routing():
    # LAN 1
    PC1 = Host("PC3", 1)
    SW1 = Switch("SW1", 8)

    # LAN 2
    PC2 = Host("PC2", 1)
    SW2 = Switch("SW2", 4)

    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.2.1"), IP("255.255.255.0"), IP("192.168.2.254"))


    R1 = Router("R1", 4)
    R1.assign_all_int_attributes(0, "zzzz.zzzz.zzzz", IP("192.168.1.254"), IP("255.255.255.0"))
    R1.assign_all_int_attributes(1, "yyyy.yyyy.yyyy", IP("192.168.2.254"), IP("255.255.255.0"))

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW2, 0)

    SW1.add_connection(1, R1, 0)
    SW2.add_connection(1, R1, 1)

    PC1.send_message("test", 0, IP("192.168.2.1"))
    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test"


def test_static_routing():
    # LAN 1
    PC1 = Host("PC3", 1)
    SW1 = Switch("SW1", 8)

    # LAN 2
    PC2 = Host("PC2", 1)
    SW2 = Switch("SW2", 4)

    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.2.1"), IP("255.255.255.0"), IP("192.168.2.254"))

    R1 = Router("R1", 4)
    R1.assign_all_int_attributes(0, "zzzz.zzzz.zzzz", IP("192.168.1.254"), IP("255.255.255.0"))
    R1.assign_all_int_attributes(1, "yyyy.yyyy.yyyy", IP("1.1.1.253"), IP("255.255.255.252"))

    R2 = Router("R2", 4)
    R2.assign_all_int_attributes(0, "xxxx.xxxx.xxxx", IP("192.168.2.254"), IP("255.255.255.0"))
    R2.assign_all_int_attributes(1, "wwww.wwww.wwww", IP("1.1.1.254"), IP("255.255.255.252"))

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW2, 0)

    SW1.add_connection(1, R1, 0)
    SW2.add_connection(1, R2, 0)

    R1.add_connection(1, R2, 1)

    R1.add_static_route(IP("192.168.2.0"), IP("255.255.255.0"), IP("1.1.1.254"))
    R2.add_static_route(IP("192.168.1.0"), IP("255.255.255.0"), IP("1.1.1.253"))

    PC1.send_message("test", 0, IP("192.168.2.1"))
    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test"


def test_no_cross_vlan_switching():
    # VLAN 10
    PC1 = Host("PC1", 1)
    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))

    # VLAN 20
    PC2 = Host("PC2", 1)
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.1.2"), IP("255.255.255.0"), IP("192.168.1.254"))

    SW1 = Switch("SW1", 8)
    SW1.add_vlan(10, 20)
    SW1.port_map[0].vlan_id = 10
    SW1.port_map[1].vlan_id = 20

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW1, 1)

    PC1.send_message("test", 0, IP("192.168.1.2"))
    assert not PC2.rx_buffer


def test_same_vlan_switching():
    # VLAN 10
    PC1 = Host("PC1", 1)
    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))

    # VLAN 20
    PC2 = Host("PC2", 1)
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.1.2"), IP("255.255.255.0"), IP("192.168.1.254"))

    SW1 = Switch("SW1", 8)
    SW1.add_vlan(10, 20)
    SW1.port_map[0].vlan_id = 10
    SW1.port_map[1].vlan_id = 10

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW1, 1)

    PC1.send_message("test", 0, IP("192.168.1.2"))
    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test"


def test_broadcast_storm():
    with pytest.raises(RecursionError):
        # VLAN 10
        PC1 = Host("PC3", 1)
        PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))

        # VLAN 20
        PC2 = Host("PC2", 1)
        PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.2.1"), IP("255.255.255.0"), IP("192.168.2.254"))

        SW1 = Switch("SW1", 4)
        SW2 = Switch("SW1", 4)
        SW3 = Switch("SW1", 4)

        PC1.add_connection(0, SW1, 0)
        PC2.add_connection(0, SW2, 0)

        SW1.add_connection(1, SW2, 1)
        SW2.add_connection(2, SW3, 0)
        SW3.add_connection(1, SW1, 2)

        PC1.send_message("test", 0, IP("192.168.2.1"))

def test_trunkport_switching():
    # VLAN 10
    PC1 = Host("PC1", 1)
    PC1.assign_all_int_attributes(0, "aaaa.aaaa.aaaa", IP("192.168.1.1"), IP("255.255.255.0"), IP("192.168.1.254"))

    PC2 = Host("PC2", 1)
    PC2.assign_all_int_attributes(0, "bbbb.bbbb.bbbb", IP("192.168.1.2"), IP("255.255.255.0"), IP("192.168.1.254"))

    # VLAN 20
    PC3 = Host("PC3", 1)
    PC3.assign_all_int_attributes(0, "cccc.cccc.cccc", IP("192.168.2.1"), IP("255.255.255.0"), IP("192.168.2.254"))

    SW1 = Switch("SW1", 8)
    SW1.add_vlan(10)
    SW1.set_interface_trunk(1)
    SW1.set_allowed_vlans(1, 10)
    SW1.port_map[0].vlan_id = 10

    SW2 = Switch("SW2", 8)
    SW2.add_vlan(10, 20)
    SW2.port_map[0].vlan_id = 10
    SW2.set_interface_trunk(1)
    SW2.set_allowed_vlans(1, 10)
    SW2.port_map[2].vlan_id = 20

    PC1.add_connection(0, SW1, 0)
    PC2.add_connection(0, SW2, 0)
    PC3.add_connection(0, SW2, 2)
    SW1.add_connection(1, SW2, 1)

    PC1.send_message("test", 0, IP("192.168.1.2"))
    assert PC2.rx_buffer[PC2.port_map[0]][0].payload.payload == "test" and not PC3.rx_buffer