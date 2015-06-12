#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from obtainfo.sync import Client, ServerDB
from bson import ObjectId
from pcnile.resource import atom_download_resource
from django.core.management.base import BaseCommand, CommandError
import datetime
import pymongo

class Command(BaseCommand):
    help = 'merge second item all info to first item id'
    
    def handle(self, *args, **options):
        timestamp = datetime.datetime.now()
        db = pymongo.Connection().server
        target = ObjectId(args[0])
        merge = ObjectId(args[1])
        try:
            local = args[2]
        except IndexError:
            local = False
        
        old = db.server.find_one(ObjectId(args[0]))
        new = db.server.find_one(ObjectId(args[1]))
        
        new['resource']['download'] += old['resource']['download']
        new['resource']['download'] = atom_download_resource( new['resource']['download'] )
        new['resource']['online'] += old['resource']['online']
        new['resource']['netdisk'] += old['resource']['netdisk']
        new['samesite'] += old['samesite']
        new['_id'] = old['_id']
        
        if local:
            server = ServerDB()
            server.delete(args[1])
            server.modtify(args[0], new)
        else:
            client = Client()
            res1 = client.delete('server', args[1])
            res2 = client.modtify('server', args[0], new)
            if res1['result'] == 'success' and res2['result'] == 'success' :
                server = ServerDB()
                server.modtify(args[0], new)
                server.delete(args[1])
            
        self.stdout.write('Successfully merge use time "%s"' % str((datetime.datetime.now() - timestamp)) )
