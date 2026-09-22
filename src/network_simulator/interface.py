# Represents an interface on a node
class Interface:
    """Represents an interface that appears on any and all nodes."""

    def __init__(self, id, node):
        self.id = id
        self.node = node
        self.mac = None

    def __str__(self):
        return f"\tMAC: {self.mac}"

    def __repr__(self):
        return f"{self.node.name} {self.id}"


class L3_Interface(Interface):
    """Represents an interface that appears on a layer node."""

    def __init__(self, id, node):
        super().__init__(id, node)
        self.ip = None
        self.netmask = None


class Router_Interface(L3_Interface):
    """Represents an interface that appears on a router."""


class Host_Interface(L3_Interface):
    """Represents an interface that appears on a host."""

    def __init__(self, id, node):
        super().__init__(id, node)
        self.gateway = None


class Switchport(Interface):
    def __init__(self, id, node):
        super().__init__(id, node)
        self.vlan_ids = set(1)


class Access_Interface(Interface):
    """Represents an access interface on a switch."""

    def __init__(self, id, node):
        super().__init__(id, node)
        self.vlan_id = 1


class Trunk_Interface(Interface):
    """Represents a trunk interface on a switch."""

    def __init__(self, id, node):
        super().__init__(id, node)
        self.native_vlan = 1
        self.allowed_vlans = set(range(1, 4095))
