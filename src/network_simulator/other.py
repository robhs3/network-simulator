class Route:
    def __init__(self, type, dest_ip, dest_netmask, interface):
        self.type = type
        self.dest_ip = dest_ip
        self.dest_netmask = dest_netmask
        self.interface = interface
        self.next_hop_ip = None

    def __str__(self):
        return (
            f"Type: {self.type}, Destination: {self.dest_ip}, Netmask: {self.dest_netmask}, Interface: {self.interface.id}"
        )

class IP:
    def __init__(self, ip_string):
        self._octets = []
        for octet_string in ip_string.split("."):
            self._octets.append(int(octet_string))
        self._ip_string = ip_string

    @property
    def octets(self):
        return self._octets

    def __str__(self):
        return self._ip_string

    def __eq__(self, other):
        if isinstance(other, IP):
            return self._ip_string == other._ip_string
        return False

    def __hash__(self):
        return hash(self._ip_string)

    def __repr__(self):
        return f"{self._ip_string}"


class PDU:
    def __init__(self, payload):
        self.payload = payload


class Segment(PDU):
    def __init__(self, payload, source_port, dest_port):
        super().__init__(payload)
        self.source_port = source_port
        self.dest_port = dest_port


class Packet(PDU):
    def __init__(self, payload, source_ip, dest_ip):
        super().__init__(payload)
        self.source_ip = source_ip
        self.dest_ip = dest_ip


class Frame(PDU):
    def __init__(self, payload, source_mac, dest_mac):
        super().__init__(payload)
        self.source_mac = source_mac
        self.dest_mac = dest_mac
        self.payload = payload

    def __str__(self):
        return (
            f"Payload: {self.payload}\n"
            f"Source Mac: {self.source_mac}\n"
            f"Destination Mac: {self.dest_mac}"
        )

class Dot1q_Frame(Frame):
    def __init__(self, payload, source_mac, dest_mac, vlan_tag):
        super().__init__(payload, source_mac, dest_mac)
        self.vlan_tag = vlan_tag


class ARP_Object:
    def __init__(self, source_ip, dest_ip, source_mac, dest_mac):
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.source_mac = source_mac
        self.dest_mac = dest_mac
    

class ARP_Request(ARP_Object):
    def __init__(self, source_ip, dest_ip, source_mac, dest_mac):
        super().__init__(source_ip, dest_ip, source_mac, dest_mac)


class ARP_Reply(ARP_Object):
    def __init__(self, source_ip, dest_ip, source_mac, dest_mac):
        super().__init__(source_ip, dest_ip, source_mac, dest_mac)