#!/usr/bin/env python3

import hashlib
import os
import subprocess
import sys
import urllib.request
import re

import shutil

from subprocess import Popen, PIPE
from codecs import decode

def get_git_history(directory, until_rev):
    git_rev_list = Popen(['git', '-C', directory, 'rev-list', 'master'], stdout=PIPE)
    git_cat_file = Popen(['git', '-C', directory, 'cat-file', '--batch'],
                         stdin=git_rev_list.stdout, stdout=PIPE)
    while True:
        line = git_cat_file.stdout.readline()
        try:
            hash_, type_, bytes_ = map(decode, line.split())
        except ValueError:
            break
        content = decode(git_cat_file.stdout.read(int(bytes_)))
        if type_ == 'commit':
            comitter = re.search('\ncommitter (.+) <(.+)> ', content)
            timestamp = re.search('author .+ ([\d]+ [+-]\d\d\d\d)\n', content).group(1)
            sha1 = re.search('ISO SHA-1 ([\w]+)', content)
            if sha1:
                print(hash_, timestamp, sha1.group(1), comitter.group(1), comitter.group(2), content)
                yield (hash_, timestamp, sha1.group(1), comitter.group(1), comitter.group(2), content)
        git_cat_file.stdout.readline()
        if hash_ == until_rev:
            break

l = list(get_git_history('.', 'f9fe277d4068ea34ebaf3c5b5f9beb7d965cafb5'))

EXTRACTED_ISO_DIR = '../TempleOS_Archive'

for hash_, timestamp, sha1, comitter_name, comitter_email, shit in reversed(l):
    for file_object in os.listdir(EXTRACTED_ISO_DIR):
        if file_object == '.git': continue
        file_object_path = os.path.join(EXTRACTED_ISO_DIR, file_object)
        if os.path.isfile(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)

    print('---- Check out rev', hash_)

    subprocess.check_call(['git', 'checkout', hash_, '--', 'TempleOSCD'])

    for file_object in os.listdir('TempleOSCD'):
        file_object_path = os.path.join('TempleOSCD', file_object)
        dst_path = os.path.join(EXTRACTED_ISO_DIR, file_object)
        if os.path.isfile(file_object_path):
            shutil.copyfile(file_object_path, dst_path)
        else:
            shutil.copytree(file_object_path, dst_path)

    dir = os.getcwd()
    os.chdir(EXTRACTED_ISO_DIR)

    print('---- Adding to git')
    subprocess.call(['git', 'add', '-A', '.'])

    print('---- Commit & push')
    subprocess.check_call(['env', 'GIT_COMMITTER_NAME=' + comitter_name, 'GIT_COMMITTER_EMAIL=' + comitter_email, 'git', 'commit', '--date', timestamp, '-m', 'TempleOS V5.03 Nightly (ISO SHA-1 %s)' % sha1])

    os.chdir(dir)
    #break
