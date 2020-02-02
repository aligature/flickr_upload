#!/opt/local/bin/python

import flickrapi
import glob
import os
import sys
import functools
import hashlib
from time import sleep
import argparse

LowerExtensions = ['.jpg', '.png', '.mov', '.jpeg', '.mp4', '.m4v']
Extensions = LowerExtensions + [ext.upper() for ext in LowerExtensions]

RetryLimit = 50

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--api-key')
parser.add_argument('-s', '--api-secret')
parser.add_argument('-d', '--directory')
parser.add_argument('-b', '--backup-directory')
parser.add_argument('-t', '--tags')
parser.add_argument('-r', '--hash-repo')

options = parser.parse_args()
if isinstance(options, tuple):
    args = options[0]
else:
    args = options
del options

hashes = {}

def file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()

def upload_file(name, file, tags = ''):
    retry_count = 0
    while retry_count < RetryLimit:
        print 'uploading %s (%s)' % (name, retry_count)
        retry_count += 1
        try:
            result = flickr.upload(filename=file, is_public=0, is_family=1, is_friend=1, tags=tags, format='xmlnode')
        except Exception as e:
            print e
            continue
        return result['stat'] == 'ok'
    return False

def upload_dir(directory, backup, tags):
    root, dirs, files = os.walk(directory).next()
    for name in sorted(files):
        if os.path.splitext(name)[1] in Extensions:
            whole_file = os.path.join(root, name)
            this_hash = file_hash(whole_file)
            if this_hash in hashes:
                print 'skipping %s, duplicate of %s' % (name, hashes[this_hash])
                os.rename(whole_file, os.path.join(backup, name))
            else:
                hashes[this_hash] = name
                if upload_file(name, whole_file, tags):
                    print 'moving %s' % name
                    os.rename(whole_file, os.path.join(backup, name))

def scan_backup(directory):
    root, dirs, files = os.walk(directory).next()
    for name in sorted(files):
        whole_file = os.path.join(root, name)
        this_hash = file_hash(whole_file)
        hashes[this_hash] = name

def load_hash_repo(filename):
    for line in open(filename):
        line = line.strip()
        splits = line.split(' ')
        hashes[splits[0]] = splits[-1]

if not args.api_key or not args.api_secret:
    print 'must include api key and secret'
    exit(1)

flickr = flickrapi.FlickrAPI(args.api_key, args.api_secret)
flickr.authenticate_via_browser(perms='write')

directory = args.directory
backup = args.backup_directory
tags = args.tags if args.tags else ''

if directory == '' or backup == '':
    print 'include upload and backup directories'
    exit(1)

if not os.path.exists(backup):
    os.makedirs(backup)
scan_backup(backup)
if args.hash_repo:
    load_hash_repo(args.hash_repo)
upload_dir(directory, backup, tags)
