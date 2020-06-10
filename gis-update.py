#
# Gis Automation task
# Fetch and update GIS Data from ArcGIS
# 
# Author: Alexander Nordbø

from zipfile import ZipFile
from pathlib import Path
import requests
import os
import glob
import shutil
import errno
import logging
import hashlib

# Configuration

# Credentials
username = ''
password = ''

# Use // for UNC and \\ for local
src = 'tmp'
dst = ''
log = './log.log'
url = 'https://apps.geodataonline.no/gisdata/Download/products.geodataonline.no/example.zip'
file = 'example.zip'

# Log settings

logging.basicConfig(format='Date-Time : %(asctime)s : %(message)s', level = logging.INFO, filename = log)

# Clean up files and folders
cleanSource = Path(src)
def cleanUp():
    try:
        if cleanSource.exists() and cleanSource.is_dir():
            try:
                shutil.rmtree(cleanSource)
            except Exception as e:
                logging.info(e)
                raise
    except OSError as e:
        print("Error: %s : %s" % (src, e.strerror))

    try:
        os.remove(file)
    except OSError as e:
        print("Error: %s : %s" % (file, e.strerror))



logging.info("Job Started.")

# Check if files in the destination folder are open or in use

logging.info("Check if any files in %s is open or in use...", dst)
isOpen = False
for file in glob.glob(dst + '/**/*.lock', recursive=True):
    logging.info("Locked file: " + file)
    isOpen = os.path.isfile(file)


# If files are in use, abort update.

if isOpen == True:
	logging.info("Update was aborted due to files in use!")
	logging.info("#" * 50)
	cleanUp()
	exit()


# Start Update

logging.info("Update Started")


# download the file contents in binary format

r = requests.get(url, auth=(username, password))

with open(file, "wb") as code:
    code.write(r.content)


# Get the checksum for the downloaded version

with open(file, "rb") as f:
    file_hash = hashlib.md5()
    while chunk := f.read(8192):
        file_hash.update(chunk)


# Create version file if it doesen't exists

if not os.path.exists('current.txt'):
    with open('current.txt', 'w'): pass


# Compare current version with the downloaded version.
versionFile = open("current.txt", "r")
currentVersion = versionFile.read()

if currentVersion != file_hash.hexdigest():
	logging.info("New Version detected: " + file_hash.hexdigest())
else:
	logging.info("No new version detected, aborting update")
	logging.info("#" * 50)
	cleanUp()
	exit()


# Remove destination folder if it exists

dirpath = Path(dst)
if dirpath.exists() and dirpath.is_dir():
    try:
        shutil.rmtree(dirpath)
    except Exception as e:
        logging.info(e)
        logging.info("Update failed!")
        logging.info("#" * 50)
        cleanUp()
        raise


# Extract files to tmp

with ZipFile(file, 'r') as zipObj:

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
        cleanUp()
        print('Directory not copied. Error: %s' % e)


# Write new version to versionFile current.txt

f = open("current.txt", "w")
f.write(file_hash.hexdigest())
f.close()

logging.info("Update Done!")
logging.info("#" * 50)
