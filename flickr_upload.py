#!/usr/bin/python

import flickrapi
import glob
import os
import sys
import functools
from time import sleep
from process_lock import ProcessLock

LowerExtensions = ['.jpg', '.png', '.mov']
Extensions = LowerExtensions + [ext.upper() for ext in LowerExtensions]

RetryLimit = 50

def upload_file(root, file):
   retry_count = 0
   while retry_count < RetryLimit:
      print 'uploading %s (%s)' % (file, retry_count)
      retry_count += 1
      try:
         result = flickr.upload(filename=os.path.join(root, file), is_public=0, is_family=1, is_friend=1, format='xmlnode')
      except Exception as e:
         print e
         continue
      status = result['stat']
      if status == 'ok':
         print 'moving %s' % file
         os.rename(os.path.join(root, file), os.path.join(backup, file))
         return

def upload_dir(directory, backup):
   root, dirs, files = os.walk(directory).next()
   for file in sorted(files):
      if os.path.splitext(file)[1] in Extensions:
         upload_file(root, file)

api_key = sys.argv[1]
api_secret = sys.argv[2]

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

directory = sys.argv[3]
backup = sys.argv[4]

if directory == '' or backup == '':
   print 'include upload and backup directories'
   exit(1)

upload_dir(directory, backup)
