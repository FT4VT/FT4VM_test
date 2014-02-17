import time
import logging
import sys
from autotest.client.shared import error
from virttest import utils_test
#sys.path.append("../../virttest")
#import ft_vm

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
  #time.sleep(20000)
  vms = env.get_all_vms()
  timeout = params["running_timeout"]
  for vm in vms:
    result = vm.wait_for_running(int(timeout))
    time.sleep(2)
  return result


