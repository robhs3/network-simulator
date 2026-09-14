from network_simulator.L3_node import L3_Node
from network_simulator.other import *
from network_simulator.interface import Host_Interface


class Host(L3_Node):
    def __init__(self, name, num_ports):
        super().__init__(name, num_ports)
        self._configurable_interface_attributes = ["mac", "ip", "netmask", "gateway"]

        # Initialize all ports with empty interface attributes and empty connections
        for i in range(num_ports):
            interface = Host_Interface(i, self)
            self.interfaces[interface] = None
            self.port_map[i] = interface

    @property
    def configurable_interface_attributes(self):
        return self._configurable_interface_attributes

    # Send a raw message that is processed down the OSI stack. Tests for end-to-end communication
    def send_message(self, payload, egress_interface_id, dest_ip):
        # Find egress interface from id
        egress_interface = self.port_map[egress_interface_id]

        packet = Packet(payload, egress_interface.ip, dest_ip)

        # Case 1: Source and destination node on same subnet
        if (
            self.is_same_subnet(egress_interface.ip, egress_interface.netmask, dest_ip)
            == True
        ):
            next_hop_ip = dest_ip
        # Case 2: Source and destination node on different subnets
        else:
            next_hop_ip = egress_interface.gateway

        # Case 1: Source knows destination MAC.
        if next_hop_ip in self.arp_table:
            # Encapsulate and transmit
            frame = Frame(packet, egress_interface.mac, self.arp_table[next_hop_ip])
            self.tx(frame, egress_interface)
        # Case 2: Source does not know destination MAC
        else:
            # ARP discovery, then encapsulate and transmit
            self.tx_buffer.append(packet)
            arp_request = ARP_Request(
                egress_interface.ip,
                next_hop_ip,
                egress_interface.mac,
                "00:00:00:00:00:00",
            )
            frame = Frame(arp_request, egress_interface.mac, "ff:ff:ff:ff:ff:ff")
            self.tx(frame, egress_interface)

            if next_hop_ip in self.arp_table:
                frame = Frame(
                    self.tx_buffer.pop(),
                    egress_interface.mac,
                    self.arp_table[next_hop_ip],
                )
                self.tx(frame, egress_interface)

    def receive_packet(self, payload, ingress_interface):
        pass
