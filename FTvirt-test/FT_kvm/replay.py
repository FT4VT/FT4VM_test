#!/usr/bin/python
import sys
import os
import subprocess
import re
import time
sys.path.append(os.environ['VIRTTEST_PATH']+"/virttest")
sys.path.append(os.environ['VIRTTEST_PATH'])
sys.path.append("/usr/local")
sys.path.append("..")
import virsh


step_dir = os.environ['VIRTTEST_PATH']+"/FT_kvm/step/"

class Replay(object):
  def __init__(self, vm_name, file_name):
    self.vm_name = vm_name
    self.file_path = step_dir+file_name+".st"
    self.f = self.open_file(self.file_path)
    self.line = self.read_line(self.f)
    while self.line:
      self.execute_command(self.line)
      self.line = self.read_line(self.f)
  
  def open_file(self, file_name):
    """
    open file
    """
    return open(file_name, "r")

  def read_line(self, f):
    """
    read line in file
    """
    return f.readline()

  def analyze_command(self, line):
    """
    Analyze which command
    sendkey
    mouse_move
    mouse_button
    wait
    """
    line = line.rstrip('\n')
    line_arr = self.transfer_line_to_arr(line)
    command = ''
    if line_arr[0] == "wait":
      #temp
      time.sleep(int(line_arr[1]))
    elif line_arr[0] == "key":
      command = "sendkey " + line_arr[1]
    elif line_arr[0] == "button":
      command = "mouse_button " + line_arr[1]
      command = command + " "+line_arr[2]
      command = command + " "+line_arr[3]
      command = command + " "+line_arr[4]
    elif line_arr[0] == "move":
      command = "mouse_move " + line_arr[1]+" "+line_arr[2]
    return command

  def execute_command(self, line):
    """
    execute command
    """
    command = self.analyze_command(line)
    print "command: "+command+'\n'
    if command != '':
      virsh.qemu_monitor_command(self.vm_name, command)

  def transfer_line_to_arr(self, line):
    """
    transfer line to array
    """
    line = re.sub(' +',' ',line)
    line_arr = line.split(' ')
    return line_arr



#test
if __name__ == '__main__':
  Replay("FTtest","login_sync")




