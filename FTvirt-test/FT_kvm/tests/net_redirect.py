import time
import logging
import sys
import subprocess
from autotest.client.shared import error
from virttest import utils_test
from virttest import kill

temp_file_n = "temp.txt"
temp_file1_n = "temp1.txt"
def run_net_redirect(test, params, env):
  """
  FT4VM network be redirected test
  1) kill primary VM process
  2) check the info from iptable that network has been redirected

  :param test: QEMU test object
  :param params: Dictionary with the test parameters
  :param env: Dictionary with test environment. 
  """
  vms = env.get_all_vms()
  for vm in vms:
    subprocess.call("ps aux | grep \"kvm\" > "+temp_file_n, shell=True)
    subprocess.call("grep \"name "+vm.name+"\" "+temp_file_n+" > "+temp_file1_n, shell=True)
    


