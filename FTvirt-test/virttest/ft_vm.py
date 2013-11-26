import time
import os
import logging
import fcntl
import re
import shutil
import tempfile
from autotest.client.shared import error
from autotest.client import utils
import utils_misc
import virt_vm
import storage
import aexpect
import remote
import virsh
import libvirt_xml
import data_dir
import xml_utils

import sys

class VM(virt_vm.BaseVM):


  def __init__(self, name, params="", root_dir="", address_cache="", state=None):
    self.name = name
    self.connect_uri = "qemu:///system"
    
  def is_alive(self):
    return (self.state() == "Running")

  def is_dead(self):
    return (self.state() == "Shutoff")

  def is_paused(self):
    return (self.state() == "paused")

  def state(self):
    """
    Return domain state
    """
    return virsh.domstate(self.name, uri=self.connect_uri).stdout.strip()

  def start(self):
    """
    start VM  by virsh FTstart [vmname]
    """
    virsh.start(self.name)
    #virsh.FTstart(self.name)





