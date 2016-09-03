##########################################################################
# ch.mycloud.python-download - Download files from mycloud.ch using python
##########################################################################
# Copyright (C) 2016 Pascal Artho - All Rights Reserved
#
# Usage: python ./mycloud-python-download.py
#
# Preparation:
# - install python requests
# - set parameters
#
# Last revised: August 20, 2016
##########################################################################

import base64
from datetime import datetime
import ConfigParser
import json
import os
import os.path
import requests
import time

# if needed set "defaultencoding" to "utf-8" using the following commands:
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
settings = ConfigParser.ConfigParser()
settings.read('config.ini')

##########################################################################
# Parameters
##########################################################################
accessToken = settings.get('default', 'accessToken')
localFolder = settings.get('default', 'localFolder')
mycloudFolder = settings.get('default', 'mycloudFolder')
##########################################################################

print "Access Token:      %s" % (accessToken)
print "Local Folder:      %s" % (localFolder)
print "MyCloud Folder:    %s" % (mycloudFolder)

def ticks(dt):
  return (dt - datetime(1, 1, 1)).total_seconds() * 10000000

def numberRJust(number, referenceNumber):
  return str(number).rjust(len(str(referenceNumber)))

def checkFileExist(localFilePath, mycloudItem):
  if (os.path.isfile(localFilePath)):
    #print "localFilePath:      " + localFilePath.decode('utf-8')
    #print "mycloudFilePath:    " + mycloudFilePath.decode('utf-8')
    localFileSize = os.path.getsize(localFilePath.decode('utf-8'))
    #print "localFileSize:      " + str(localFileSize)
    localFileTime = os.path.getmtime(localFilePath.decode('utf-8'))
    #print "localFileTime:      " + str(localFileTime)
    localFileTimeTicks = ticks(datetime.utcfromtimestamp(localFileTime))
    #print "localFileTimeTicks: " + str(localFileTimeTicks)
    
    itemSize = long(mycloudItem.get('Length'))
    if (itemSize != localFileSize):
      return False
    return True
  return False

def fileSizeInMB(filePath, decimals):
  fileSize = os.path.getsize(filePath.decode('utf-8'))
  fileSizeInMB = float(fileSize) / (1024 * 1024)
  return round(fileSizeInMB, decimals)

def encodeString(path):
  # Standard base64 encoder
  encodedString = base64.b64encode(path)
  
  # Remove any trailing '='
  encodedString = encodedString.split('=')[0]
  
  # 62nd char of encoding
  encodedString = encodedString.replace('+', '-')
  
  # 63rd char of encoding
  encodedString = encodedString.replace('/', '_')
  return encodedString

def downloadFile(localFilePath, mycloudFilePath):
  encodedString = encodeString(mycloudFilePath)
  
  # Debug information
  print "Encoded Filename:  %s" % (encodedString)
  print "Filename:          %s" % (mycloudFilePath)
  
  # define headers for HTTP Post request
  headers = {}
  headers['User-Agent'] = 'mycloud.ch - python downloader'
  headers['Authorization'] = 'Bearer ' + accessToken
  
  getQuery = "https://storage.prod.mdl.swisscom.ch/object/?p=%s" % (encodedString)
  
  try:
    # Download file using python requests
    # if needed add "verify=False" to perform "insecure" SSL connections and transfers
    # result = requests.get(getQuery, headers=headers, strem=True, verify=False)
    result = requests.get(getQuery, headers=headers, stream=True)
    print "Successful Download: %s [HTTP Status %s]" % (str(result.status_code == requests.codes.ok), str(result.status_code))
    if (result.status_code == 200):
      currentDir = os.path.dirname(os.path.abspath(localFilePath))
      if not (os.path.isdir(currentDir)):
        os.makedirs(currentDir)
      with open(localFilePath, 'wb') as f:
        for chunk in result:
            f.write(chunk)
      return True
    return False
  except requests.ConnectionError as e:
    print "Oops! There was a connection error. Ensure connectivity to remote host and try again..."
    print e
    return False
  except requests.exceptions.Timeout as e:
    # Maybe set up for a retry, or continue in a retry loop
    print "Oops! There was a timeout error. Ensure connectivity to remote host and try again..."
    print e
    return False
  except requests.exceptions.TooManyRedirects as e:
    # Tell the user their URL was bad and try a different one
    print "Oops! There were too many redirects. Try a different URL ..."
    print e
    return False
  except requests.exceptions.RequestException as e:
    print e
    return False

# change current directory
if not (os.path.isdir(localFolder)):
  os.makedirs(localFolder)
os.chdir(localFolder)

encodedString = encodeString(mycloudFolder)

# get current list of downloaded files
headers = {}
headers['User-Agent'] = 'mycloud.ch - python downloader'
headers['Authorization'] = 'Bearer ' + accessToken

getQuery = "https://storage.prod.mdl.swisscom.ch/sync/list/?p=%s" % (encodedString)
# if needed add "verify=False" to perform "insecure" SSL connections and transfers
# resultGet = requests.get(getQuery, headers=headers, verify=False)
resultGet = requests.get(getQuery, headers=headers)
if (resultGet.status_code != 200):
  print "Oops! The accessToken is not correct. Get a new accessToken and try again..."
  quit()

array = resultGet.text
# save current list of files in array
data = json.loads(array)

# find files for upload
files = list()
for item in data:
  if ('Length' in item):
    files.append(item)

# count files for download
numberOfFiles = len(files)

# define progress counter
counter = 1
downloadedFiles = 0
downloadedFilesMB = 0
failedDownloadedFiles = 0
skippedFiles = 0

try:
  # foreach file to download
  for mycloudItem in files:
    print "Start Download %s of %s" % (numberRJust(counter, numberOfFiles), numberOfFiles)
    mycloudFP = str(mycloudItem.get('Path').encode('utf-8'))
    localFP = localFolder + mycloudFP[len(mycloudFolder):]
    localFP = localFP.replace("%20", ' ')
    if (checkFileExist(localFP, mycloudItem) == False):
      if (downloadFile(localFP, mycloudFP) == True):
        downloadedFiles += 1
        downloadedFilesMB += fileSizeInMB(localFP, 3)
      else:
        failedDownloadedFiles += 1
    else:
      skippedFiles += 1
    counter += 1
except KeyboardInterrupt, e:
  print "\n################################"
  print "Abort download to mycloud.ch ..."
  print "################################\n"

# Debug information
print "Number of Files:                            %s" % (numberRJust(numberOfFiles, numberOfFiles))
print "Number of downloaded Files:                 %s (%s MB)" % (numberRJust(downloadedFiles, numberOfFiles), str(downloadedFilesMB))
print "Number of failed downloaded Files:          %s" % (numberRJust(failedDownloadedFiles, numberOfFiles))
print "Number of skipped Files (already existing): %s" % (numberRJust(skippedFiles, numberOfFiles))
