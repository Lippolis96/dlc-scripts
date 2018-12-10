# SSH
import paramiko
import socket
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException

logPlainParam = {"type" : "plain"}
logHTMLNormalParam = {"type" : "html", "color" : "Blue"}
logHTMLErrorParam = {"type" : "html", "color" : "Red"}

# Connect to ssh and execute 1 command on the server
def sshConnectExec1(ssh_param, parent, command):
    parent.writeLog("Attempting to connect to host...", logHTMLNormalParam)
    try:
        sshClient = paramiko.SSHClient()
        #sshClient.load_system_host_keys()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(**ssh_param)
        
        parent.writeLog("Checking GPU status...", logHTMLNormalParam)
        ssh_stdin, ssh_stdout, ssh_stderr = sshClient.exec_command(command)
        parent.writeLog("".join(ssh_stdout.readlines()), logPlainParam)

        parent.writeLog("Closing connection...", logHTMLNormalParam)
        sshClient.close()
        
    except (BadHostKeyException, AuthenticationException, SSHException, socket.error, socket.gaierror) as e:
        parent.writeLog(type(e).__name__ + ": " + str(e), logHTMLErrorParam)
        
        
#def connectExecContinuous:
    # FOR CONTINUOUS OUTPUT, BELOW WILL RUN UNTIL EOF, AND WAIT IF EOF DOES NOT YET EXIST
    # for line in iter(lambda: stdout.readline(2048), ""): print(line, end="")
