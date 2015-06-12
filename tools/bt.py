#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import argparse
import comtypes.client as cc
from bt_store import dump_torrent, dump_urn, get_server_magnet, load_torrent, stats_torrent

strURL = "http://torrent-cache.bitcomet.org:36869/get_torrent?info_hash=%s&size=226920869&key=%s"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-f", "--folder", type=str, default="")
    parser.add_argument("-r", "--rule", type=str, default='upload')
    parser.add_argument("-s", "--status", type=bool, default=False)
    parser.add_argument("-u", "--update", type=bool, default=False)
    parser.add_argument("-n", "--num", type=int, default=1000)
    args = parser.parse_args()
    
    if args.target == 'load':
        print stats_torrent(rule='full')
        load_torrent(args.folder)
        print stats_torrent(rule='full')
    elif args.target == 'dump':
        dump_torrent(where=args.folder, rule=args.rule, status=args.status, update=args.update, num=args.num)
    elif args.target == 'urn':
        dump_urn(where=args.folder)
    elif args.target == 'stats':
        print stats_torrent(rule=args.rule, status=args.status)
    elif args.target == 'old':
        magnets, urns = get_server_magnet(args.num)
        with codecs.open('magnet.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
        
        """"
        fail = 0
        magnets = list()
        for urn in urns:
            try:
                objUMU = cc.CreateObject("UMU.UrlGenerator")
                urn_key = objUMU.GenBitCometTorrentKey(urn)
                magnets.append(strURL % (urn, urn_key))
            except:
                fail += 1
        
        print 'fail count %d' % fail
        
        with codecs.open('bitcomet.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
        """
        
        magnets = list()
        for urn in urns:
            urn = urn.upper()
            s = urn[:2]
            e = urn[-2:]
            magnets.append("http://bt.box.n0808.com/%s/%s/%s.torrent" % (s,e,urn))
        with codecs.open('btbox.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
        
        """    
        magnets = list()
        for urn in urns:
            magnets.append("http://d1.torrentkittycn.com/?infohash=%s" % urn.upper())
        with codecs.open('torrentkittycn.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
            
        magnets = list()
        for urn in urns:
            magnets.append("http://dynamic.cloud.vip.xunlei.com/interface/get_torrent?userid=95847549&infoid=%s" % urn.upper())
        with codecs.open('xunlei.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
            
        magnets = list()
        for urn in urns:
            magnets.append("http://d1.lengziyuan.com/?infohash=%s" % urn.upper())
        with codecs.open('lengziyuan.txt', 'wb', 'utf-8') as f:
            f.write(os.linesep.join(magnets))
        """
