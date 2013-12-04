#!/usr/bin/python
import optparse
import fnmatch
import os
import sys
import subprocess
sys.path.append("../virttest")
sys.path.append("/usr/local")
sys.path.append("..")
import virsh
#import ft_vm

virttest_dir = os.environ['VIRTTEST_PATH']

class Capture_file(object):
  """
  Capture message will been load in this class creates file
  """
  def __init__(self):
    self.file_name = ''
    self.FT_kvm_dir = virttest_dir+"/FT_kvm"
    self._create_tmp()

  def save(self):
    result = False
    while not result:
      self.file_name = ''
      file_name = raw_input("Input the file name (don't need .py): ")
      if file_name != '' and file_name != "tmp":
        self.file_name = file_name + ".st"
        result = self._find()
        if not result:
          print "File name exists\n"
      else:
        print "File name can be \"tmp\" or empty"

    if result == True:
      subprocess.call("mv "+self.FT_kvm_dir+"/tmp "+self.FT_kvm_dir+"/step/"+self.file_name, shell=True)


  def _create_tmp(self):
    self.tmp_file = open(self.FT_kvm_dir+"/tmp",'w')

  def _find(self):
    """
    Searching the file is existed or not

    """
    for root, dirs, files in os.walk("./step"):
      for f_name in files:
        print "root : ",root,"\n"
        print "dirs : ",dirs,"\n"
        print "files : ",f_name,"\n"
        if fnmatch.fnmatch(self.file_name,f_name):
          self.file_name == ''
          return False
    return True






class Capture(object):
  def __init__(self, vm_name, backup_ip):
    self.vm_name = vm_name
    self.backup_ip = backup_ip
    self.file = Capture_file()

  def main(self):
    #self.file.save()
    #self.file.search_file()
    print os.environ['VIRTTEST_PATH'],"\n"
    print virttest_dir+"\n"
    print virsh.domstate('test').stdout.strip()
    #virsh.qemu_monitor_command("test", "sendkey 1")
    virsh.qemu_monitor_command("test", "mouse_move 10 1000")
    virsh.qemu_monitor_command("test", "\'mouse_button 1 1000 4000 0\'")
    #virsh.qemu_monitor_command("test", "sendkey 2")

    


if __name__ == '__main__':
  app = Capture("test",'')
  app.main()
  #print virsh.domstate('test').stdout.strip()
  #vm = ft_vm.VM('test')
  #print vm.state()

  
