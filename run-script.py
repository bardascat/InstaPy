import subprocess
import os
import json

python_path = "python"
base_path = "/home/ubuntu/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')


process = subprocess.Popen("/usr/bin/python2.7 " + base_path + "/verify_account.py", shell=True,stdout=subprocess.PIPE)
result = process.communicate()[0]
process.wait()

print(result)