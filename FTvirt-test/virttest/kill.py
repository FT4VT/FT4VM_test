import subprocess

def kill(pid, sig_no = '9'):
  """
  execute linux kill command
  """
  cmd = "kill -"+sig_no+" "+pid
  subprocess.call(cmd, shell=True)
