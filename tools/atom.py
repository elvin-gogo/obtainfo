#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import urlparse
import pymongo
import re
from pcnile.resource import atom_download_resource
from bson import ObjectId

if __name__ == '__main__':
    db = pymongo.Connection().server
    
    for item in db.server.find():
        item['resource']['download'] = atom_download_resource(item['resource']['download'])
        db.server.save(item)
