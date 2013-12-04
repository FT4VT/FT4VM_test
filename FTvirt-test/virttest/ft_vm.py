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
import threading

import sys

class VM(virt_vm.BaseVM):


  def __init__(self, name, params="", root_dir="", address_cache="", state=None):
    self.name = name
    self.connect_uri = "qemu:///system"
    self.sec_vm_ip = params["sec_vm_ip"]
    self.sec_vm_con_uri = "qemu+tcp://"+self.sec_vm_ip+"/system"
    super(VM, self).__init__(name, params)
    
  def is_alive(self, p_or_s_vm = 'p'):
    return (self.state(p_or_s_vm) == "running")

  def is_dead(self, p_or_s_vm = 'p'):
    return (self.state(p_or_s_vm) == "shut off")

  def is_paused(self, p_or_s_vm = 'p'):
    return (self.state(p_or_s_vm) == "paused")

  def state(self, p_or_s_vm = 'p'):
    """
    Return domain state
    """
    if p_or_s_vm == 'p':
      return virsh.domstate(self.name, uri=self.connect_uri).stdout.strip()
    elif p_or_s_vm == 's':
      return virsh.domstate(self.name, uri=self.sec_vm_con_uri).stdout.strip()

  def start(self):
    """
    Start VM  by virsh FTstart [vmname]

    need use thread to do
    """
    print "start vm name : ",self.name,"\n"
    t = threading.Thread(target=self.thread_start, args = ())
    t.start()
    

  def thread_start(self):
    """
    Execute FTstart
    In order to not been locked by FTstart command
    """
    sys.stdout.restore()
    print "\n\nthread in\n\n"
    #virsh.start(self.name)
    virsh.FTstart(self.name, uri=self.connect_uri)

  def wait_for_running(self, timeout):
    """
    Wait primary VM and secondary VM running
    """
    print "wait_for_running in\n"
    end_time = time.time() + timeout
    time.sleep(30)
    if self.is_alive() and self.is_paused('s'):
      print "primary state : ",self.state(),"\n"
      print "secondary state : ",self.state('s'),"\n\n"
      while time.time() < end_time:
        print "primary state : ",self.state(),"\n"
        print "secondary state : ",self.state('s'),"\n\n"
        if self.is_alive() and self.is_alive('s'):
          break
        time.sleep(2)
    if self.is_alive() and self.is_alive('s'):
      return True
    return False





