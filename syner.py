#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mysite import private
from putty.sync import SyncServer

def run():
    ip = private.SERVER_IP if private.DEBUG == False else 'localhost'
    ss = SyncServer(db=private.MONGODB, html_dir=private.HTML_DIR, ip=ip, port=3149)
    ss.run()

if __name__ == "__main__":
    run()
