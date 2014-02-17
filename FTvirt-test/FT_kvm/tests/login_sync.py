#!/usr/bin/python
import sys
import os
import time
import socket
import threading
import Queue
import subprocess
#temp
sys.path.append(os.environ['VIRTTEST_PATH']+"/FT_kvm")
import replay

msg_q = Queue.Queue()
lock_q = threading.Lock()

def create_socket(ip, port):
  """
  create socket to listen from vm
  """
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((ip, int(port)))
  sock.listen(3)
  sock.settimeout(10)
  return sock

def open_socket(sock):
  """
  open socket
  """
  try:
    thread_list = []
    while True:
      (c_sock, address) = sock.accept()
      print "accept\n"        
      client_info = (c_sock, address)
      client_info[0].settimeout(10)
      t = threading.Thread(target=receive, args = (client_info,))
      thread_list.append(t) 
      t.start()
  except socket.timeout:
    print "catch\n"  
  finally:
    while thread_list:
      print "wait\n"
      t = thread_list.pop()
      t.join() 

    

def receive(client_info):
  """
  receive message from client
  """
  try:
    msg = client_info[0].recv(1024)
    print client_info[1]," ",msg,"\n"
    lock_q.acquire()
    print "lock in\n"
    msg_q.put(msg)
    #time.sleep(5)
    lock_q.release()
  except socket.timeout:
    print "recv in catch\n"   
  #client_info[0].close()

def check_queue():
  """
  check queue has two message \"login\" from two VM
  """
  result = False
  login_times = 0
  get_times = 0
  while not msg_q.empty():
    if get_times > 2:
      break
    if msg_q.get() == "login":
      login_times+=1
    get_times+=1
  if login_times == 2:
    result = True
  return result

def run_login_sync(test, params, env):
  """
  login synchronization
  using login_sync.st to replay keyboard event
  """
  timeout = params["running_timeout"]
  vms = env.get_all_vms()
  for vm in vms:
    vm.wait_for_running(int(timeout))
    sock = create_socket("140.115.53.42","5566")
    t = threading.Thread(target=open_socket, args = (sock,))
    t.start()
    replay.Replay(vm.name, "login_sync")
    t.join()
    result = check_queue()
    if not result:
      raise Exception("login not synchronization")
  return result



if __name__ == '__main__':
  sock = create_socket("140.115.53.42","5566")
  print "test\n"
  t = threading.Thread(target=open_socket, args = (sock,))
  t.start()
  print "test1\n"
  #subprocess.call("virsh qemu-monitor-command --hmp FTtest sendkey 1", shell = True)
  #subprocess.call("virsh qemu-monitor-command --hmp FTtest sendkey 2", shell = True)
  #subprocess.call("virsh qemu-monitor-command --hmp FTtest sendkey 3", shell = True)
  #subprocess.call("virsh qemu-monitor-command --hmp FTtest sendkey kp_enter", shell = True)
  replay.Replay("FTtest","login_sync")
  print "thread :",t.is_alive(),"\n"
  t.join()
  print "thread :",t.is_alive(),"\n"
  while not msg_q.empty():
    print msg_q.get()+"\n"


