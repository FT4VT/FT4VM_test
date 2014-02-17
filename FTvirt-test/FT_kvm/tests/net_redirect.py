import time
import logging
import sys
import os
import subprocess
import re
"""
if you want only run this file_name

pls mark below three sentences (form ...)

unmark the sentences 
[sys.path.append("../../virttest")
import kill]
"""
from autotest.client.shared import error
from virttest import utils_test
from virttest import kill
#sys.path.append("../../virttest")
#import kill

virttest_dir = os.environ['VIRTTEST_PATH']
temp_file_n = virttest_dir+"/FT_kvm/tests/temp.txt"
temp_file1_n = virttest_dir+"/FT_kvm/tests/temp1.txt"
"""
iptables title
"""
iptb_input_t = "Chain INPUT (policy ACCEPT)\n"
iptb_forward_t = "Chain FORWARD (policy ACCEPT)\n"
iptb_prerouting_t = "Chain PREROUTING (policy ACCEPT)\n"
iptb_postrouting_t = "Chain POSTROUTING (policy ACCEPT)\n"



def find_vm_pid(name):
  """
  find vm's process id
  """
  subprocess.call("ps aux | grep \"kvm\" > "+temp_file_n, shell=True)
  subprocess.call("grep \"name "+name+"\" "+temp_file_n+" > "+temp_file1_n, shell=True)
  f = open_file(temp_file1_n)
  line = read_line(f)
  pid = get_id(line)
  delete_file(temp_file_n)
  delete_file(temp_file1_n)
  return pid

def open_file(file_name):
  """
  open file
  """
  return open(file_name, "r")

def read_line(f):
  """
  read line in file
  """
  return f.readline()

def get_id(line):
  """
  get id string
  """
  line_arr = transfer_line_to_arr(line)
  return line_arr[1]

def delete_file(file_name):
  """
  delete temp file
  """
  subprocess.call("rm "+file_name, shell=True)
  
def kill_vm(name):
  """
  kill vm's process
  """
  pid = find_vm_pid(name)
  kill.kill(pid, '9')

def check_net_redirect(ip, port):
  """
  check net is redirected
  """
  cat_iptables_info()
  check_input_reject(port)
  check_dnat(ip, port)
  check_masq()


def cat_iptables_info():
  """
  cat info from command : iptables 
  """
  print "wait for cat iptables\n"
  subprocess.call("iptables --list > "+temp_file_n, shell = True)
  subprocess.call("iptables -t nat --list > "+temp_file1_n, shell = True)

def check_input_reject(port):
  """
  check input to port is been rejected.
  """
  #print "input in\n"
  f = open_file(temp_file_n)
  if read_line(f) ==  iptb_input_t:
    line = read_line(f)
    while line:
      if line == iptb_forward_t:
        break
      line_arr = transfer_line_to_arr(line)
      if line_arr[0] == "REJECT":
        if line_arr[6] == "dpt:"+port:
          f.close()
          return True
      line = read_line(f)
  f.close()
  raise Exception("Input isn't rejected")

def check_dnat(ip, port):
  """
  check port is been redirected to ip:port
  """
  #print "dnat in\n"
  dnat_line = "DNAT       tcp  --  anywhere             anywhere             tcp dpt:"+port+" to:"+ip+":"+port+"\n"
  f = open_file(temp_file1_n)
  if read_line(f) == iptb_prerouting_t:
    line = read_line(f)
    while line:
      if line == iptb_input_t:
        break
      if line == dnat_line:
        f.close()
        return True
      line = read_line(f)
  f.close()
  raise Exception("DNAT fail")

def check_masq():
  """
  check MASQUERADE is anywhere
  """
  #print "masq in\n"
  masq_line = "MASQUERADE  all  --  anywhere             anywhere            \n"
  f = open_file(temp_file1_n)
  line = read_line(f)
  while line:
    if line == masq_line:
      f.close()
      return True
    #print "line : ",line,"\n"
    line = read_line(f)
  f.close()
  raise Exception("Haven't do MASQUERADE")




def transfer_line_to_arr(line):
  """
  transfer line to array
  """
  line = re.sub(' +',' ',line)
  line_arr = line.split(' ')
  return line_arr


def run_net_redirect(test, params, env):
  """
  FT4VM network be redirected test
  1) kill primary VM process
  2) check the info from iptable that network has been redirected

  :param test: QEMU test object
  :param params: Dictionary with the test parameters
  :param env: Dictionary with test environment. 
  """
  timeout = params["running_timeout"]
  vms = env.get_all_vms()
  for vm in vms:
    vm.wait_for_running(int(timeout))
    kill_vm(vm.name)
    #in order to wait iptables update
    time.sleep(1)

    check_net_redirect(vm.sec_vm_ip,vm.port)
    delete_file(temp_file_n)
    delete_file(temp_file1_n)
    time.sleep(2)


#test
if __name__ == '__main__':
  #kill_vm("kvm-test")
  #f = open_file(temp_file1_n)
  #line = read_line(f)
  #pid = get_id(line)
  
  #cat_iptables_info()
  print "check input :",check_input_reject("5902"),"\n"
  print "check dnat :",check_dnat("140.115.53.33","5902"),"\n"
  print "check masq :",check_masq(),"\n"


    


