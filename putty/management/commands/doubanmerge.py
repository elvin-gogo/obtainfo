#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from obtainfo.search import Search
from obtainfo.sync import Client, ServerDB
from bson import ObjectId
from pcnile.resource import atom_download_resource
from django.core.management.base import BaseCommand, CommandError
import datetime
import codecs
import pymongo

class Command(BaseCommand):
    help = 'merge second item all info to first item id'
    
    def handle(self, *args, **options):
        timestamp = datetime.datetime.now()
        db = pymongo.Connection().server
        server = ServerDB()
        
        df = set()
        out = dict()
        for d in db.server.find():
            did = d['douban']['id']
            if did:
                if did not in df:
                    df.add(did)
                    out[did] = [d]
                else:
                    out[did].append(d)
        
        show = list()
        for k,v in out.items():
            if len(v) > 1:
                v = sorted(v, key=lambda x : x['addtime'], reverse=False)
                show.append("manage.py merge %s" % ("  ".join([str(t['_id']) for t in v])))
                show.append("%s %s" % (k, " / ".join([t['title'] for t in v])))
                
                downloads = list()
                for d in v:
                    downloads += d['resource']['download']
                downloads = atom_download_resource( downloads )
                
                online = list()
                for d in v:
                    online += d['resource']['online']
                
                samesite = list()
                for d in v:
                    samesite += d['samesite']
                samesite = list(set( samesite ))
                
                new = v[-1]
                
            """
            new['resource']['download'] += old['resource']['download']
            new['resource']['download'] = atom_download_resource( new['resource']['download'] )
            new['resource']['online'] += old['resource']['online']
            new['samesite'] += old['samesite']
            new['_id'] = old['_id']
            
            server.delete(args[1])
            server.modtify(args[0], new)
            """
        with codecs.open('text.txt', 'wb', 'utf-8') as f:
            f.write('\n'.join(show))
        
        self.stdout.write('Successfully merge use time "%s"' % str((datetime.datetime.now() - timestamp)) )
