#!/opt/local/bin/python

import flickrapi
import glob
import os
import sys
import functools
import hashlib
from time import sleep

LowerExtensions = ['.jpg', '.png', '.mov', '.jpeg', '.mp4']
Extensions = LowerExtensions + [ext.upper() for ext in LowerExtensions]

RetryLimit = 50

hashes = {}

def file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def upload_file(name, file):
    retry_count = 0
    while retry_count < RetryLimit:
        print 'uploading %s (%s)' % (name, retry_count)
        retry_count += 1
        try:
            result = flickr.upload(filename=file, is_public=0, is_family=1, is_friend=1, format='xmlnode')
        except Exception as e:
            print e
            continue
        return result['stat'] == 'ok'
    return False

def upload_dir(directory, backup):
    root, dirs, files = os.walk(directory).next()
    for name in sorted(files):
        if os.path.splitext(name)[1] in Extensions:
            whole_file = os.path.join(root, name)
            md5 = file_hash(whole_file)
            if md5 in hashes:
                print 'skipping %s, duplicate of %s' % (name, hashes[md5])
                os.rename(whole_file, os.path.join(backup, name))
            else:
                hashes[md5] = name
                if upload_file(name, whole_file):
                    print 'moving %s' % name
                    os.rename(whole_file, os.path.join(backup, name))

def scan_backup(directory):
    root, dirs, files = os.walk(directory).next()
    for name in sorted(files):
        whole_file = os.path.join(root, name)
        md5 = file_hash(whole_file)
        hashes[md5] = name

api_key = sys.argv[1]
api_secret = sys.argv[2]

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

directory = sys.argv[3]
backup = sys.argv[4]

if directory == '' or backup == '':
    print 'include upload and backup directories'
    exit(1)

if not os.path.exists(backup):
    os.makedirs(backup)
scan_backup(backup)
upload_dir(directory, backup)
