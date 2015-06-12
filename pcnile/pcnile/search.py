#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import pyjsonrpc
from bson.objectid import ObjectId
from paginator import get_page_part
from jieba.analyse import ChineseAnalyzer

from whoosh import index
from whoosh.index import create_in
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED, DATETIME, NGRAMWORDS

class Movie(SchemaClass):
    oid = ID(stored=True)
    title = NGRAMWORDS()
    people = NGRAMWORDS
    showtime = DATETIME(stored=True, sortable=True)
    addtime = DATETIME(stored=True, sortable=True)
    detail = TEXT(stored=True, analyzer=ChineseAnalyzer())

def get_docs_by_oid(collection, oids):
    sort_field = [("year", -1),('douban.ranking.score', -1)]
    index_dict = {'type':1, 'bigpic':1, 'title':1, 'language':1, 'year':1, 'douban':1, 'genre':1, 'resource':1, 'area':1, 'director':1, 'actor':1, 'plot':1, 'finish':1}
    query_dict = {'_id':{'$in':[ObjectId(r) for r in oids]}}
    
    return collection.find(query_dict, index_dict).sort(sort_field)
    
### import : when run in ubuntu with apache mod_wsgi, should know dir or file has Permission
class Search(object):
    def __init__(self, path, collection):
        if not os.path.exists(path):
            os.mkdir(path)
            
        if not index.exists_in(path):
            self.ix = index.create_in(path, schema=Movie)
        else:
            self.ix = index.open_dir(path)
        
        self.info = collection
    
    def add_document(self, writer, d):
        oid = unicode(str(d['_id']), 'utf-8')
        title = u",".join([d['title']] + d['aka'])
        people = u",".join(d['writer'] + d['actor'] + d['director'])
        detail = title + u',' + people
        addtime = d['addtime']
        
        writer.add_document(oid=oid, title=title, people=people, detail=detail, addtime=addtime)
    
    def initialize(self):
        writer = self.ix.writer()
        for d in self.info.find():
            self.add_document(writer, d)
        writer.commit()
    
    def insert(self, d):
        writer = self.ix.writer()
        self.add_document(writer, d)
        writer.commit()
        return True
    
    def delete(self, oid):
        if not isinstance(oid, unicode):
            oid = unicode(oid, 'utf-8')
        
        self.ix.delete_by_term('oid', oid)
        return True
    
    def modtify(self, d):
        try:
            self.delete(str(d['_id']))
        except:
            pass
        
        return self.insert(d)
    
    def build_qs(self, qs):
        qp = MultifieldParser(["title", "people", "detail"], schema=self.ix.schema)
        q = qp.parse(qs)
        return q
    
    def count(self, qs):
        q = self.build_qs(qs)
        
        with self.ix.searcher() as s:
            results = s.search(q, limit=None)
            count = results.estimated_length()
        
        return count
    
    def query(self, qs, limit=100):
        return list(get_docs_by_oid(self.info, self.query_oid(qs, limit)))
    
    def query_oid(self, qs, limit=100):
        with self.ix.searcher() as s:
            results = [r['oid'] for r in s.search(self.build_qs(qs), limit=limit)]
        
        return results

    def query_page(self, qs, page=1, limit=15): # Show 15 contacts per page
        with self.ix.searcher() as s:
            results = s.search(self.build_qs(qs), limit=100)
            contacts = get_page_part(results, page, limit)
        
        return (contacts, list(get_docs_by_oid(self.info, [r['oid'] for r in contacts])))

class FullTextSearchClient(object):
    def __init__(self, collection, ip="localhost", port=9413):
        self.info = collection
        self.rpc = pyjsonrpc.HttpClient(url="http://%s:%s" % (ip, port), timeout=5)
    
    def query_page(self, qs, page=1, limit=15):
        try:
            results = self.rpc.call("search", qs)
        except:
            results = []
        
        contacts = get_page_part(results, page, limit)
        return (contacts, get_docs_by_oid(self.info, [r for r in contacts]))

    # insert a mongodb item
    def insert(self, doc):
        self.rpc.call("insert", doc)
    
    def modtify(self, doc):
        self.rpc.call("modtify", doc)
    
    def delete(self, oid):
        self.rpc.call("delete", oid)

class FullTextSearchServer(object):
    def __init__(self, path, collection, ip="localhost", port=9413):
        self.ip = ip
        self.port = port
        self.fts = Search(path, collection)
        
    def run(self):
        class RequestHandler(pyjsonrpc.HttpRequestHandler):
            methods = {
                'search':self.fts.query_oid,
                'insert':self.fts.insert,
                'modtify':self.fts.modtify,
                'delete':self.fts.delete
            }
        
        # Threading HTTP-Server
        http_server = pyjsonrpc.ThreadingHttpServer(
            server_address = (self.ip, self.port),
            RequestHandlerClass = RequestHandler
        )
        
        print "Starting HTTP server ..."
        print "URL: http://%s:%s" % (self.ip, self.port)
        
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            http_server.shutdown()
        
        print "Stopping HTTP server ..."
