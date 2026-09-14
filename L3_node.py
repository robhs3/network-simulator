from abc import ABC, abstractmethod

from interface import Interface
from node import Node
from other import ARP_Reply, ARP_Request, Frame, IP, Packet


class L3_Node(Node, ABC):
    """Represents a layer 3 node in a network."""

    def __init__(self, name: str, num_ports: int):
        super().__init__(name, num_ports)
        self.arp_table: dict[IP, str] = {}

    @property
    @abstractmethod
    def configurable_interface_attributes(self) -> list[str]:
        """Get the list of attributes that can be configured on a layer 3 interface."""
        ...

    def is_same_subnet(self, source_ip: IP, netmask: IP, dest_ip: IP) -> bool:
        """Return True if two IP addresses are on the same subnet, given a netmask."""
        return self.derive_network_address(source_ip, netmask) == self.derive_network_address(dest_ip, netmask)
    
    def derive_network_address(self, ip: IP, netmask: IP) -> IP:
        """Return the network address of an IP address's subnet, given its netmask."""
        return IP(".".join(str(ip_octet & netmask_octet) for ip_octet, netmask_octet in zip(ip.octets, netmask.octets)))

    def process_frame_in(self, frame: Frame, ingress_interface: Interface) -> None:
        """Begin processing the received frame based on its payload."""
        if frame.dest_mac == ingress_interface.mac or frame.dest_mac == "ff:ff:ff:ff:ff:ff":
            payload = frame.payload

            match payload:
                case ARP_Request():
                    self.receive_arp_request(payload, ingress_interface)
                case ARP_Reply():
                    self.receive_arp_reply(payload, ingress_interface)
                case Packet():
                    self.receive_packet(payload, ingress_interface)

    def receive_arp_reply(self, arp_reply: ARP_Reply, ingress_interface: Interface):
        """Process a received ARP Reply message."""
        self.rx_buffer[ingress_interface].pop()
        self.arp_table[arp_reply.source_ip] = arp_reply.source_mac

    def receive_arp_request(self, arp_request: ARP_Request, ingress_interface: Interface):
        """Process a received ARP Request message."""
        self.rx_buffer[ingress_interface].pop()

        if arp_request.dest_ip == ingress_interface.ip:
            self.arp_table[arp_request.source_ip] = arp_request.source_mac
            arp_reply = ARP_Reply(ingress_interface.ip, arp_request.source_ip, ingress_interface.mac, arp_request.source_mac)
            frame = Frame(arp_reply, ingress_interface.mac, arp_request.source_mac)
            self.tx(frame, ingress_interface)

    @abstractmethod
    def receive_packet(self, packet: Packet, ingress_interface: Interface):
        """Process a received packet according to layer 3 node type."""
        ...

    def assign_all_int_attributes(self, interface_id, *attrs):
        """Assign all attributes to an interface according to the layer 3 node type."""
        interface = self.port_map[interface_id]
        for attribute_type, attribute_value in zip(self.configurable_interface_attributes, attrs):
            setattr(interface, attribute_type, attribute_value)

    def __str__(self):
        connection_string = ""

        for self_interface, other_interface in self.interfaces.items():
            connection_string += f"\n\tPort {self_interface.id} -> {other_interface.node.name if other_interface is not None else None}\t\n{self_interface}\n"
        
        return (
            f"Name: {self.name}\n"
            f"Interfaces: {connection_string}"
            f"RX Buffer: {self.rx_buffer}\n"
        )

    def __repr__(self):
        return(f"{self.name}")