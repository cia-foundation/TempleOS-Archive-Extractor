#!/usr/bin/env python3

from __future__ import print_function

import sys
sys.path.append('isoparser')

import hashlib
import os
import subprocess
import sys
import urllib
import isoparser
import os
import glob

import datetime
import shutil

ISO_DIR = sys.argv[1]
#isos = [os.path.join(ISO_DIR, entry) for entry in os.listdir(ISO_DIR)]

#[iI][sS][oO]
isos = glob.glob(os.path.join(ISO_DIR, '**/*.ISO'), recursive=True)

# pass 1: assign a date to each iso file

def get_latest_timestamp(node):
    if node.is_directory and len(node.children):
        #all = [get_latest_timestamp(entry) for entry in node.children]
        #print(all)
        oldest = max([get_latest_timestamp(entry) for entry in node.children])
        return oldest
    else:
        #print(node.name, '\t\t', node.datetime)
        #return datetime.datetime.strptime(node.datetime, "%Y-%m-%d %H:%M:%S")
        return node.datetime

timestamps = []

for filename in isos:
    print(filename)
    iso = isoparser.parse(filename)
    ts = get_latest_timestamp(iso.root)
    #print(iso, ts)
    #abort()
    timestamps += [ts]


sorted_pairs = sorted(zip(isos, timestamps), key=lambda pair: pair[1])
isos, ts = zip(*sorted_pairs)
print('======================')
print('\n'.join([str(p) for p in sorted_pairs]))
#print('OK?'); input()
# pass 2: extract ISOs and commit chronologically

EXTRACTED_ISO_DIR = '../TempleOS_Archive'

SKIP=1
for FILE_NAME, timestamp in sorted_pairs[SKIP:]:
    for file_object in os.listdir(EXTRACTED_ISO_DIR):
        if file_object == '.git': continue
        file_object_path = os.path.join(EXTRACTED_ISO_DIR, file_object)
        if os.path.isfile(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)

    print('---- Extracting', FILE_NAME)
    subprocess.check_call(['./extract_templeos.py', FILE_NAME, EXTRACTED_ISO_DIR, timestamp])

    dir = os.getcwd()
    os.chdir(EXTRACTED_ISO_DIR)

    print('---- Adding to git')
    subprocess.call(['git', 'add', '-A', '.'])
    subprocess.check_call(['git', 'commit', '-m', os.path.basename(FILE_NAME), '--date', timestamp])

    os.chdir(dir)
