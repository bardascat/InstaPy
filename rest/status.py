import os
import subprocess
import json
from flask import abort
from rest_logger import getLogger
import os.path

python_path = "python"
base_path = "/home/projects/InstaPy"
DEVNULL = open(os.devnull, 'wb')

def getStatus():
    status={"status":"up"}
    return status
