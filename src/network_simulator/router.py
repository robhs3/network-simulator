from network_simulator.interface import Router_Interface
from network_simulator.l3_node import L3_Node
from network_simulator.other import *


class Router(L3_Node):
    def __init__(self, name, num_ports):
        super().__init__(name, num_ports)
        self._configurable_interface_attributes = ["mac", "ip", "netmask"]
        self.routes = []

        # Initialize all ports with empty interface attributes and empty connections
        for i in range(num_ports):
            interface = Router_Interface(i, self)
            self.interfaces[interface] = None
            self.port_map[i] = interface

    @property
    def configurable_interface_attributes(self):
        return self._configurable_interface_attributes

    def assign_all_int_attributes(self, interface_id, *attrs):
        """Assign all attributes to a router interface."""
        super().assign_all_int_attributes(interface_id, *attrs)
        self.add_initial_routes(interface_id)

    def add_initial_routes(self, interface_id):
        """Add connected/local routes for an interface to the routing table."""
        interface = self.port_map[interface_id]
        network_address = self.derive_network_address(interface.ip, interface.netmask)
        self.routes.append(
            Route("connected", network_address, interface.netmask, interface)
        )
        self.routes.append(
            Route("local", interface.ip, IP("255.255.255.255"), interface)
        )

    def add_static_route(self, dest_network, netmask, next_hop_ip):
        # Find interface associated with next_hop_ip
        for self_interface, other_interface in self.interfaces.items():
            if (
                isinstance(other_interface, Router_Interface)
                and other_interface.ip == next_hop_ip
            ):
                interface = self_interface
                break

        route = Route("static", dest_network, netmask, interface)
        route.next_hop_ip = next_hop_ip
        self.routes.append(route)

    def receive_packet(self, packet, ingress_interface):
        payload = packet.payload
        # If packet was destined for the router interface itself, do nothing (implement later)
        if packet.dest_ip == ingress_interface.ip:
            pass
        else:
            route = self.longest_prefix_route(packet.dest_ip)

            if route is None:
                print("No matching route")
            else:
                payload = packet.payload
                egress_interface = route.interface
                new_packet = Packet(payload, egress_interface.ip, packet.dest_ip)

                if route.type == "static":
                    if route.next_hop_ip in self.arp_table:
                        frame = Frame(
                            new_packet,
                            egress_interface.mac,
                            self.arp_table[route.next_hop_ip],
                        )
                        self.tx(frame, egress_interface)
                    else:
                        self.tx_buffer.append(new_packet)
                        arp_request = ARP_Request(
                            egress_interface.ip,
                            route.next_hop_ip,
                            egress_interface.mac,
                            "00:00:00:00:00:00",
                        )
                        frame = Frame(
                            arp_request, egress_interface.mac, "ff:ff:ff:ff:ff:ff"
                        )
                        self.tx(frame, egress_interface)

                        if route.next_hop_ip in self.arp_table:
                            frame = Frame(
                                self.tx_buffer.pop(),
                                egress_interface.mac,
                                self.arp_table[route.next_hop_ip],
                            )
                            self.tx(frame, egress_interface)
                else:
                    # Source knows destination MAC
                    if packet.dest_ip in self.arp_table:
                        frame = Frame(
                            new_packet,
                            egress_interface.mac,
                            self.arp_table[packet.dest_ip],
                        )
                        self.tx(frame, egress_interface)
                    # Source does not know destination MAC
                    else:
                        self.tx_buffer.append(new_packet)
                        arp_request = ARP_Request(
                            egress_interface.ip,
                            packet.dest_ip,
                            egress_interface.mac,
                            "00:00:00:00:00:00",
                        )
                        frame = Frame(
                            arp_request, egress_interface.mac, "ff:ff:ff:ff:ff:ff"
                        )
                        self.tx(frame, egress_interface)

                        if packet.dest_ip in self.arp_table:
                            frame = Frame(
                                self.tx_buffer.pop(),
                                egress_interface.mac,
                                self.arp_table[packet.dest_ip],
                            )
                            self.tx(frame, egress_interface)

    def longest_prefix_route(self, target_ip):
        match = None
        longest_prefix = 0
        for route in self.routes:
            if self.is_same_subnet(route.dest_ip, route.dest_netmask, target_ip):
                prefix_length = 0

                for octet in route.dest_netmask.octets:
                    prefix_length += (octet).bit_count()

                if prefix_length > longest_prefix:
                    longest_prefix = prefix_length
                    match = route

        return match
