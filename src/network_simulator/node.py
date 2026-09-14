from abc import ABC, abstractmethod
from collections import defaultdict

from network_simulator.interface import Interface
from network_simulator.other import Frame, IP, Packet


class Node(ABC):
    """Represents a node in a network: host, switch, router, etc."""

    def __init__(self, name: str, num_ports: int) -> None:
        self.name = name
        self.num_ports = num_ports

        # Stores received frames before processing.
        self.rx_buffer: defaultdict[Interface, list[Frame]] = defaultdict(list)

        self.interfaces: dict[Interface, Interface | None] = {}
        self.port_map: dict[int, Interface] = {}

        # Stores outbound packets/frames before transmission.
        self.tx_buffer: list[Packet | Frame] = []

    def add_connection(
        self, self_interface_id: int, other_node: "Node", other_interface_id: int
    ) -> None:
        """Connect the interface of one node to the interface of another node."""
        # Connections are formed bidirectionally, so either node can initiate a complete connection
        self_interface = self.port_map[self_interface_id]
        other_interface = other_node.port_map[other_interface_id]

        self.interfaces[self_interface] = other_interface
        other_node.interfaces[other_interface] = self_interface

    def rx(self, frame: Frame, ingress_interface: Interface) -> None:
        """Receive a frame on a specified ingress interface."""
        self.rx_buffer[ingress_interface].append(frame)
        self.process_frame_in(frame, ingress_interface)

    def tx(self, frame: Frame, egress_interface: Interface) -> None:
        """Transmit a frame out of a specified egress interface."""
        for self_interface, other_interface in self.interfaces.items():
            if self_interface == egress_interface and other_interface is not None:
                other_interface.node.rx(frame, other_interface)

    @abstractmethod
    def process_frame_in(self, frame: Frame, ingress_interface: Interface) -> None:
        """Begin processing the received frame according to node type."""
        ...

    def __str__(self) -> str:
        """Display node information."""
        connections = []

        for self_interface, other_interface in self.interfaces.items():
            other_node_name = other_interface.node.name if other_interface else None
            connections.append(
                f"Port {self_interface.id} -> {other_node_name}\n{self_interface}"
            )

        return "\n".join(connections)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"
