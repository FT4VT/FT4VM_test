import time
import logging
import sys
from autotest.client.shared import error
from virttest import utils_test

def run_FTboot(test, params, env):
  """
  FT4VM boot test:
  1) get vm 
  2) wait primary vm and secondary vm state become running
  3) if primary vm and secondary vm running pass else fail

  #important : Now, only can run one primary VM

  :param test: QEMU test object
  :param params: Dictionary with the test parameters
  :param env: Dictionary with test environment.
  """
  vms = env.get_all_vms()
  timeout = 90
  for vm in vms:
    #print "FTboot in \n"
    result = vm.wait_for_running(timeout)
    if not result:
      raise Exception
  return result

