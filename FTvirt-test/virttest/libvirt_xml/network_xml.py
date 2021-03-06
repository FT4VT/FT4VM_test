"""
Module simplifying manipulation of XML described at
http://libvirt.org/formatnetwork.html
"""

import logging
from virttest import virsh, xml_utils
from virttest.libvirt_xml import base, xcepts, accessors


class RangeList(list):

    """
    A list of start & end address tuples
    """

    def __init__(self, iterable=None):
        """
        Initialize from list/tuple of two-item tuple start/end address strings
        """
        x_str = "iterable must contain two-item tuples of start/end addresses"
        newone = []
        for item in iterable:
            if not issubclass(type(item), tuple):
                raise xcepts.LibvirtXMLError(x_str)
            if len(item) is not 2:
                raise xcepts.LibvirtXMLError(x_str)
            # Assume strings will be validated elsewhere
            newone.append(tuple(item))
        super(RangeList, self).__init__(newone)

    def append_to_element(self, element):
        """
        Adds range described by instance to ElementTree.element
        """
        if not issubclass(type(element), xml_utils.ElementTree.Element):
            raise ValueError(
                "Element is not a ElementTree.Element or subclass")
        for start, end in self:
            serange = {'start': start, 'end': end}
            element.append(xml_utils.ElementTree.Element('range', serange))


class IPXML(base.LibvirtXMLBase):

    """
    IP address block, optionally containing DHCP range information

    Properties:
        dhcp_ranges: RangeList instances (list-like)
        address: string IP address
        netmask: string IP's netmask
    """

    __slots__ = base.LibvirtXMLBase.__slots__ + ('dhcp_ranges', 'address',
                                                 'netmask')

    def __init__(self, address='192.168.122.1', netmask='255.255.255.0',
                 virsh_instance=base.virsh):
        """
        Create new IPXML instance based on address/mask
        """
        accessors.XMLAttribute(
            'address', self, parent_xpath='/', tag_name='ip',
            attribute='address')
        accessors.XMLAttribute(
            'netmask', self, parent_xpath='/', tag_name='ip',
            attribute='netmask')
        super(IPXML, self).__init__(virsh_instance=virsh_instance)
        self.xml = u"<ip address='%s' netmask='%s'></ip>" % (address, netmask)

    def get_dhcp_ranges(self):
        """
        Returns all XML described DHCP ranges as a RangeList object
        """
        xmltreefile = self.dict_get('xml')
        newlist = []
        for element in xmltreefile.findall('/ip/dhcp/range'):
            start = element.get('start')  # attribute of range tag
            end = element.get('end')
            newlist.append((start, end, ))
        return RangeList(newlist)

    def set_dhcp_ranges(self, value):
        """
        Sets XML described DHCP ranges from a RangeList object
        """
        if not issubclass(type(value), RangeList) or value is not None:
            raise xcepts.LibvirtXMLError("Value is not a RangeList or subclassa"
                                         " instance.")
        # Always start from clean-slate
        self.del_dhcp_ranges()
        if value is None:
            return  # ip element has no dhcp block
        xmltreefile = self.dict_get('xml')
        dhcp = xml_utils.ElementTree.Element('dhcp')
        ip_elem = xmltreefile.find('/ip')
        if ip_elem is None:
            raise xcepts.LibvirtXMLError("Network contains no IP element")
        ip_elem.append(dhcp)
        value.append_to_element(dhcp)
        xmltreefile.write()

    def del_dhcp_ranges(self):
        """
        Removes all DHCP ranges from XML
        """
        xmltreefile = self.dict_get('xml')
        element = xmltreefile.find('/dhcp')
        if element is not None:
            xmltreefile.remove(element)


class NetworkXMLBase(base.LibvirtXMLBase):

    """
    Accessor methods for NetworkXML class.

    Properties:
        name: string, operates on XML name tag
        uuid: string, operates on uuid tag
        fwd_mode: string, operates on mode attribute of forward tag
        mac: string, operates on address attribute of mac tag
        ip: string operate on ip/dhcp ranges as IPXML instances
        bridge: dict, operates on bridge attributes
        defined: virtual boolean, callout to virsh methods
            get: True if libvirt knows network name
            set: True defines network, False undefines to libvirt
            del: Undefines network to libvirt
        active: virtual boolean, callout to virsh methods
            get: True if network is active to libvirt
            set: True activates network, False deactivates to libvirt
            del: Deactivates network to libvirt
        autostart: virtual boolean, callout to virsh methods
            get: True if libvirt autostarts network with same name
            set: True to set autostart, False to unset to libvirt
            del: Unset autostart to libvirt
        persistent: virtual boolean, callout to virsh methods
            get: True if network was defined, False if only created.
            set: Same as defined property
            del: Same as defined property
    """

    __slots__ = base.LibvirtXMLBase.__slots__ + ('name', 'uuid', 'bridge',
                                                 'defined', 'active',
                                                 'autostart', 'persistent',
                                                 'fwd_mode', 'mac', 'ip')

    __uncompareable__ = base.LibvirtXMLBase.__uncompareable__ + (
        'defined', 'active',
        'autostart', 'persistent')

    __schema_name__ = "network"

    def __init__(self, virsh_instance=base.virsh):
        accessors.XMLElementText('name', self, parent_xpath='/',
                                 tag_name='name')
        accessors.XMLElementText('uuid', self, parent_xpath='/',
                                 tag_name='uuid')
        accessors.XMLAttribute('fwd_mode', self, parent_xpath='/',
                               tag_name='forward', attribute='mode')
        accessors.XMLAttribute('mac', self, parent_xpath='/',
                               tag_name='mac', attribute='address')
        accessors.XMLElementDict('bridge', self, parent_xpath='/',
                                 tag_name='bridge')
        super(NetworkXMLBase, self).__init__(virsh_instance=virsh_instance)

    def __check_undefined__(self, errmsg):
        if not self.defined:
            raise xcepts.LibvirtXMLError(errmsg)

    def get_defined(self):
        """
        Accessor for 'define' property - does this name exist in network list
        """
        return self.name in self.virsh.net_state_dict(only_names=True).keys()

    def set_defined(self, value):
        """Accessor method for 'define' property, set True to define."""
        if not self.super_get('INITIALIZED'):
            pass  # do nothing
        value = bool(value)
        if value:
            self.virsh.net_define(self.xml)  # send it the filename
        else:
            del self.defined

    def del_defined(self):
        """Accessor method for 'define' property, undefines network"""
        self.__check_undefined__("Cannot undefine non-existant network")
        self.virsh.net_undefine(self.name)

    def get_active(self):
        """Accessor method for 'active' property (True/False)"""
        self.__check_undefined__("Cannot determine activation for undefined "
                                 "network")
        state_dict = self.virsh.net_state_dict()
        return state_dict[self.name]['active']

    def set_active(self, value):
        """Accessor method for 'active' property, sets network active"""
        if not self.super_get('INITIALIZED'):
            pass  # do nothing
        self.__check_undefined__("Cannot activate undefined network")
        value = bool(value)
        if value:
            if not self.active:
                self.virsh.net_start(self.name)
            else:
                pass  # don't activate twice
        else:
            if self.active:
                del self.active
            else:
                pass  # don't deactivate twice

    def del_active(self):
        """Accessor method for 'active' property, stops network"""
        self.__check_undefined__("Cannot deactivate undefined network")
        if self.active:
            self.virsh.net_destroy(self.name)
        else:
            pass  # don't destroy twice

    def get_autostart(self):
        """Accessor method for 'autostart' property, True if set"""
        self.__check_undefined__("Cannot determine autostart for undefined "
                                 "network")
        state_dict = self.virsh.net_state_dict()
        return state_dict[self.name]['autostart']

    def set_autostart(self, value):
        """Accessor method for 'autostart' property, sets/unsets autostart"""
        if not self.super_get('INITIALIZED'):
            pass  # do nothing
        self.__check_undefined__("Cannot set autostart for undefined network")
        value = bool(value)
        if value:
            if not self.autostart:
                self.virsh.net_autostart(self.name)
            else:
                pass  # don't set autostart twice
        else:
            if self.autostart:
                del self.autostart
            else:
                pass  # don't unset autostart twice

    def del_autostart(self):
        """Accessor method for 'autostart' property, unsets autostart"""
        if not self.defined:
            raise xcepts.LibvirtXMLError("Can't autostart nonexistant network")
        self.virsh.net_autostart(self.name, "--disable")

    def get_persistent(self):
        """Accessor method for 'persistent' property"""
        state_dict = self.virsh.net_state_dict()
        return state_dict[self.name]['persistent']

    # Copy behavior for consistency
    set_persistent = set_defined
    del_persistent = del_defined

    def get_ip(self):
        xmltreefile = self.dict_get('xml')
        try:
            ip_root = xmltreefile.reroot('/ip')
        except KeyError, detail:
            raise xcepts.LibvirtXMLError(detail)
        ipxml = IPXML(virsh_instance=self.dict_get('virsh'))
        ipxml.xmltreefile = ip_root
        return ipxml

    def set_ip(self, value):
        if not issubclass(type(value), IPXML):
            raise xcepts.LibvirtXMLError("value must be a IPXML or subclass")
        xmltreefile = self.dict_get('xml')
        # nuke any existing IP block
        self.del_ip()
        # IPXML root element is whole IP element tree
        root = xmltreefile.getroot()
        root.append(value.xmltreefile.getroot())
        xmltreefile.write()

    def del_ip(self):
        xmltreefile = self.dict_get('xml')
        element = xmltreefile.find('/ip')
        if element is not None:
            xmltreefile.remove(element)
            xmltreefile.write()


class NetworkXML(NetworkXMLBase):

    """
    Manipulators of a Virtual Network through it's XML definition.
    """

    __slots__ = NetworkXMLBase.__slots__

    def __init__(self, network_name='default', virsh_instance=base.virsh):
        """
        Initialize new instance with empty XML
        """
        super(NetworkXML, self).__init__(virsh_instance=virsh_instance)
        self.xml = u"<network><name>%s</name></network>" % network_name

    @staticmethod  # wraps __new__
    def new_all_networks_dict(virsh_instance=base.virsh):
        """
        Return a dictionary of names to NetworkXML instances for all networks

        :param virsh: virsh module or instance to use
        :return: Dictionary of network name to NetworkXML instance
        """
        result = {}
        # Values should all share virsh property
        new_netxml = NetworkXML(virsh_instance=virsh_instance)
        networks = new_netxml.virsh.net_state_dict(only_names=True).keys()
        for net_name in networks:
            new_copy = new_netxml.copy()
            new_copy.xml = virsh.net_dumpxml(net_name).stdout.strip()
            result[net_name] = new_copy
        return result

    @staticmethod
    def new_from_net_dumpxml(network_name, virsh_instance=base.virsh):
        """
        Return new NetworkXML instance from virsh net-dumpxml command

        :param network_name: Name of network to net-dumpxml
        :param virsh_instance: virsh module or instance to use
        :return: New initialized NetworkXML instance
        """
        netxml = NetworkXML(virsh_instance=virsh_instance)
        netxml['xml'] = virsh_instance.net_dumpxml(network_name).stdout.strip()
        return netxml

    @staticmethod
    def get_uuid_by_name(network_name, virsh_instance=base.virsh):
        """
        Return Network's uuid by Network's name.

        :param network_name: Network's name
        :return: Network's uuid
        """
        network_xml = NetworkXML.new_from_net_dumpxml(network_name,
                                                      virsh_instance)
        return network_xml.uuid

    def debug_xml(self):
        """
        Dump contents of XML file for debugging
        """
        xml = str(self)  # LibvirtXMLBase.__str__ returns XML content
        for debug_line in str(xml).splitlines():
            logging.debug("Network XML: %s", debug_line)

    def create(self):
        """
        Adds non-persistant / transient network to libvirt with net-create
        """
        self.virsh.net_create(self.xml)

    def orbital_nuclear_strike(self):
        """It's the only way to really be sure.  Remove all libvirt state"""
        try:
            self['active'] = False  # deactivate (stop) network if active
        except xcepts.LibvirtXMLError, detail:
            # inconsequential, network will be removed
            logging.warning(detail)
        try:
            self['defined'] = False  # undefine (delete) network if persistent
        except xcepts.LibvirtXMLError, detail:
            # network already gone
            logging.warning(detail)
