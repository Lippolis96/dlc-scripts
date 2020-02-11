#!/bin/python
import sys
import paramiko

rpi = {"username": sys.argv[1],
       "hostname": sys.argv[2],
       "password": sys.argv[3],
       
       }
command = " " .join(sys.argv[4:])

print(rpi)
print(command)

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(**rpi)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

#print("STD_IN  ::: ", ssh_stdin.read())
print("STD_OUT ::: ", "".join(ssh_stdout.readlines()))
#print("STD_ERR ::: ", ssh_stderr.read())
ssh.close()
