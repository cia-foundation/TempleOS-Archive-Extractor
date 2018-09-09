#!/usr/bin/env python

import sys
sys.path.append('isoparser')

import errno
import isoparser
import os
import subprocess
import shutil

ISO_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
VERSION = sys.argv[3]

iso = isoparser.parse(ISO_FILE)

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def extract(node, path):
    make_sure_path_exists(path)
    for entry in node.children:
        full_path = os.path.join(path, entry.name)

        if entry.is_directory:
            extract(entry, full_path)
        else:
            open(full_path, 'wb').write(entry.content)

def decompress(full_path):
    if VERSION >= '2015-02-15 21:43:28':
        decompressed_path = full_path[0:len(full_path)-2]
        subprocess.check_call(['./TOSZ', '-ascii', full_path, decompressed_path])
        os.remove(full_path)
    else:
        #shutil.copyfile(full_path, decompressed_path)
        subprocess.check_call(['./TSZ', '-ascii', full_path])
        if full_path.endswith('.Z'):
            decompressed_path = full_path[0:len(full_path)-2]
            os.rename(full_path, decompressed_path)

def decompress_all_files_in(path):
    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        compressed_extensions = 'APZ ASZ AUZ BIZ CPZ DTZ GLZ HPZ MPZ MUZ TXZ'.split()

        if os.path.isdir(full_path):
            decompress_all_files_in(full_path)
        elif full_path.endswith('.Z') or (len(full_path) >= 4 and full_path[-4] == '.' and full_path[-3:] in compressed_extensions):
            decompress(full_path)

# Extract TempleOS disk tree
extract(iso.root, OUTPUT_DIR)

#if VERSION < '2015-02-15 21:43:28':
#    subprocess.check_call(['gcc', '-o', 'TSZ', os.path.join(OUTPUT_DIR, 'Linux', 'TSZ.CPP')])

# Decompress compressed files
decompress_all_files_in(OUTPUT_DIR)
