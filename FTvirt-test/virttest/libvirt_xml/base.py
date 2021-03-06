
from autotest.client import utils
from virttest import propcan, xml_utils, virsh
from virttest.libvirt_xml import xcepts


class LibvirtXMLBase(propcan.PropCanBase):

    """
    Base class for common attributes/methods applying to all sub-classes

    Properties:
        xml: virtual XMLTreeFile instance
            get: xml filename string
            set: create new XMLTreeFile instance from string or filename
            del: deletes property, closes & unlinks any temp. files
        xmltreefile: XMLTreeFile instance
        virsh: virsh module or Virsh class instance
            set: validates and sets value
            get: returns value
            del: removes value
        validates: virtual boolean, read-only, True/False from virt-xml-validate
    """

    __slots__ = ('xml', 'virsh', 'xmltreefile', 'validates')
    __uncompareable__ = __slots__
    __schema_name__ = None

    def __init__(self, virsh_instance=virsh):
        """
        Initialize instance with connection to virsh

        :param virsh_instance: virsh module or instance to use
        """
        self.dict_set('xmltreefile', None)
        self.dict_set('validates', None)
        super(LibvirtXMLBase, self).__init__({'virsh': virsh_instance,
                                              'xml': None})
        # Can't use accessors module here, would make circular dep.

    def __str__(self):
        """
        Returns raw XML as a string
        """
        return str(self.dict_get('xml'))

    def __eq__(self, other):
        # Dynamic accessor methods mean we cannot compare class objects
        # directly
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        # Don't assume both instances have same comparables
        uncomparable = set(self.__uncompareable__)
        uncomparable |= set(other.__uncompareable__)
        dict_1 = {}
        dict_2 = {}
        slots = set(self.__slots__) | set(other.__slots__)
        for slot in slots - uncomparable:
            try:
                dict_1[slot] = getattr(self, slot)
            except xcepts.LibvirtXMLNotFoundError:
                pass  # Unset virtual values won't have keys
            try:
                dict_2[slot] = getattr(other, slot)
            except xcepts.LibvirtXMLNotFoundError:
                pass  # Unset virtual values won't have keys
        return dict_1 == dict_2

    def set_virsh(self, value):
        """Accessor method for virsh property, make sure it's right type"""
        value_type = type(value)
        # issubclass can't work for classes using __slots__ (i.e. no __bases__)
        if hasattr(value, 'VIRSH_EXEC') or hasattr(value, 'virsh_exec'):
            self.dict_set('virsh', value)
        else:
            raise xcepts.LibvirtXMLError("virsh parameter must be a module "
                                         "named virsh or subclass of virsh.VirshBase "
                                         "not a %s" % str(value_type))

    def set_xml(self, value):
        """
        Accessor method for 'xml' property to load using xml_utils.XMLTreeFile
        """
        # Always check to see if a "set" accessor is being called from __init__
        if not self.super_get('INITIALIZED'):
            self.dict_set('xml', value)
        else:
            try:
                if self.dict_get('xml') is not None:
                    del self['xml']  # clean up old temporary files
            except KeyError:
                pass  # Allow other exceptions through
            # value could be filename or a string full of XML
            self.dict_set('xml', xml_utils.XMLTreeFile(value))

    def get_xml(self):
        """
        Accessor method for 'xml' property returns xmlTreeFile backup filename
        """
        return self.xmltreefile.name  # The filename

    def get_xmltreefile(self):
        """
        Return the xmltreefile object backing this instance
        """
        try:
            # don't call get_xml() recursivly
            xml = self.dict_get('xml')
            if xml is None:
                raise KeyError
        except (KeyError, AttributeError):
            raise xcepts.LibvirtXMLError("No xml data has been loaded")
        return xml  # XMLTreeFile loaded by set_xml() method

    def set_xmltreefile(self, value):
        """
        Point instance directly at an already initialized XMLTreeFile instance
        """
        if not issubclass(type(value), xml_utils.XMLTreeFile):
            raise xcepts.LibvirtXMLError("xmltreefile value must be XMLTreefile"
                                         " type or subclass, not a %s"
                                         % type(value))
        self.dict_set('xml', value)

    def del_xmltreefile(self):
        """
        Remove all backing XML
        """
        self.dict_del('xml')

    def copy(self):
        """
        Returns a copy of instance not sharing any references or modifications
        """
        # help keep line length short, virsh is not a property
        the_copy = self.__class__(virsh_instance=self.virsh)
        try:
            # file may not be accessible, obtain XML string value
            xmlstr = str(self.dict_get('xml'))
            # Create fresh/new XMLTreeFile along with tmp files from XML
            # content
            the_copy.dict_set('xml', xml_utils.XMLTreeFile(xmlstr))
        except xcepts.LibvirtXMLError:  # Allow other exceptions through
            pass  # no XML was loaded yet
        return the_copy

    def get_validates(self):
        """
        Accessor method for 'validates' property returns virt-xml-validate T/F
        """
        # self.xml is the filename
        ret = self.virt_xml_validate(self.xml,
                                     self.super_get('__schema_name__'))
        if ret.exit_status == 0:
            return True
        else:
            return False

    def set_validates(self, value):
        """
        Raises LibvirtXMLError
        """
        del value  # not needed
        raise xcepts.LibvirtXMLError("Read only property")

    def del_validates(self):
        """
        Raises LibvirtXMLError
        """
        raise xcepts.LibvirtXMLError("Read only property")

    @staticmethod
    def virt_xml_validate(filename, schema_name=None):
        """
        Return CmdResult from running virt-xml-validate on backing XML
        """
        command = 'virt-xml-validate %s' % filename
        if schema_name:
            command += ' %s' % schema_name
        cmdresult = utils.run(command, ignore_status=True)
        return cmdresult
