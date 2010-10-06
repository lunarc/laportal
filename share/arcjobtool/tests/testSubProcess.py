import subprocess

process = subprocess.Popen(['arcproxy', '-O'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
print process.communicate('How are you?\n')

