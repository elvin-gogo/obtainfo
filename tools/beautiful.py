#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import libtorrent as lt
import uuid
import json
import codecs
import re

re_pass = re.compile(r'^_____padding_file')

if __name__ == '__main__':
    fil = open('1.torrent', 'rb').read()
    meta = lt.bdecode(fil)
    
    for files in meta['info']['files']:
        path = files['path']
        if not re_pass.match(path[-1]):
            name = "www.obtainfo.com_" + str(uuid.uuid4()) + os.path.splitext(path[-1])[1]
            path[-1] = name
            
            if 'path.utf-8' in files:
                path = files['path.utf-8']
                path[-1] = name
    
    meta['info']['name'] = 'look.txt'
    meta['info']['name.utf-8'] = 'look.txt'
    
    processed = lt.bencode(meta)
    open('process.torrent', 'wb').write(processed)
