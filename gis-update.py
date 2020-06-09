#
# Gis Automation task
# Fetch and update GIS Data from ArcGIS
# 
# Author: Alexander Nordbø

from zipfile import ZipFile
from pathlib import Path
import requests
import os
import shutil
import errno
import logging
import hashlib

# Credentials
username = 'USERNAME'
password = 'PASSWORD'

# Use // for UNC and \\ for local
src = 'tmp'
dst = '//UNC-PATH-TO-DESTINATION'
log = '//UNC-PATH-TO-DESTINATION'
url = 'Direct-Download-Link-From-ArcGIS'
file = 'ZIP-FILE-NAME'

logging.basicConfig(format='Date-Time : %(asctime)s : %(message)s', level = logging.INFO, filename = log)

logging.info("Update Started")
# download the file contents in binary format
r = requests.get(url, auth=(username, password))

with open(file, "wb") as code:
    code.write(r.content)

# Get the checksum for the new file
with open(file, "rb") as f:
    file_hash = hashlib.md5()
    while chunk := f.read(8192):
        file_hash.update(chunk)

logging.info("New checksum: " + file_hash.hexdigest())

# Remove destination folder if exists
dirpath = Path(dst)
if dirpath.exists() and dirpath.is_dir():
    try:
        shutil.rmtree(dirpath)
    except Exception as e:
        logging.info(e)
        logging.info("Update failed!")
        logging.info("#" * 50)
        os.remove(file)
        raise

# Extract files to tmp
with ZipFile(file, 'r') as zipObj:

   # Extract all the contents to tmp
   zipObj.extractall(src)

# Update files and folders in dst folder.
try:
    shutil.copytree(src, dst)
except OSError as e:
    # If the error was caused because the source wasn't a directory
    if e.errno == errno.ENOTDIR:
        shutil.copy(src, dst)
    else:
        logging.info("Update failed!")
        logging.info("#" * 50)
        print('Directory not copied. Error: %s' % e)

# Clean up files and folders
try:
    shutil.rmtree(src)
except OSError as e:
    print("Error: %s : %s" % (src, e.strerror))

try:
    os.remove(file)
except OSError as e:
    print("Error: %s : %s" % (file, e.strerror))

logging.info("Update Done!")
logging.info("#" * 50)
