from node import Node
from interface import Access_Interface, Trunk_Interface
from other import Dot1q_Frame, Frame

class Switch(Node):
    def __init__(self, name, num_ports):
        super().__init__(name, num_ports)
        self.mac_table = {} # {mac : (interface, vlan_id)}
        self.vlans = set()

        # Initialize all ports with empty interface attributes, no connections, and default vlan configuration
        for i in range(num_ports):
            interface = Access_Interface(i, self)
            self.interfaces[interface] = None
            self.port_map[i] = interface

    def add_vlan(self, *vlan_ids):
        self.vlans.add(vlan_ids)

    def dot1q_encapsulate(self, frame: Frame, vid):
        return Dot1q_Frame(frame.payload, frame.source_mac, frame.dest_mac, vid)

    def dot1q_deencapsulate(self, dot1q_frame):
        return Frame(dot1q_frame.payload, dot1q_frame.source_mac, dot1q_frame.dest_mac)

    def process_frame_in(self, frame, ingress_interface):

        if isinstance(ingress_interface, Access_Interface):
            vid = ingress_interface.vlan_id
        elif isinstance(ingress_interface, Trunk_Interface):
            if isinstance(frame, Dot1q_Frame):
                vid = frame.vlan_tag
                frame = self.dot1q_deencapsulate(frame)
            elif isinstance(frame, Frame):
                vid = ingress_interface.native_vlan

        self.mac_table[frame.source_mac] = (ingress_interface, vid)

        if frame.dest_mac in self.mac_table and self.mac_table[frame.dest_mac][1] == vid:
            self.process_frame_out(frame, self.mac_table[frame.dest_mac][0], vid)
        else:
            for self_interface, other_interface in self.interfaces.items():
                if isinstance(self_interface, Access_Interface):
                    if self_interface != ingress_interface and self_interface.vlan_id == vid:
                        self.tx(frame, self_interface)

                if isinstance(self_interface, Trunk_Interface):
                    if self_interface != ingress_interface and vid in self_interface.allowed_vlans:
                        self.process_frame_out(frame, self_interface, vid)

    def process_frame_out(self, frame, egress_interface, vid):
        if isinstance(egress_interface, Access_Interface):
            self.tx(frame, egress_interface)
        elif isinstance(egress_interface, Trunk_Interface):
            if vid == egress_interface.native_vlan:
                self.tx(frame, egress_interface)
            else:
                frame = self.dot1q_encapsulate(frame, vid)
                self.tx(frame, egress_interface)

    def set_interface_trunk(self, interface_id):
        old_interface = self.port_map[interface_id]
        new_interface = Trunk_Interface(interface_id, self)

        # Update switch interface info
        self.interfaces[new_interface] = self.interfaces.pop(old_interface)
        self.port_map[interface_id] = new_interface

    def set_allowed_vlans(self, interface_id, *vlan_ids):
        interface = self.port_map[interface_id]
        interface.allowed_vlans = set(vlan_ids)
        interface.allowed_vlans.add(interface.native_vlan)

    def set_native_vlan(self, interface_id, vlan_id):
        interface = self.port_map[interface_id]
        interface.native_vlan = vlan_id
        interface.allowed_vlans.add(vlan_id)

        
    def flood(self, frame, ingress_interface):
        if isinstance(ingress_interface, Access_Interface):
            # Iterate through all connections
            for self_interface, other_interface in self.interfaces.items():
                # Transmit frame out of all interfaces with same VLAN ID except the ingress interface it was received on
                if self_interface.vlan_id == ingress_interface.vlan_id \
                    and self_interface.id != ingress_interface.id \
                    and other_interface is not None:
                    self.tx(frame, self_interface)