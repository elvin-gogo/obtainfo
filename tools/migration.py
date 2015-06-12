#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import shutil
import string
import codecs
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, default="")
    parser.add_argument("-t", "--target", type=str, default='upload')
    args = parser.parse_args()
    
    source = args.source
    target = args.target
    for f in os.listdir(source):
        if f.endswith('.torrent'):
            if not os.path.exists(os.path.join(target, f[:2])):
                os.mkdir(os.path.join(target, f[:2]))
            
            shutil.move(os.path.join(source, f), os.path.join(target, f[:2], f))
