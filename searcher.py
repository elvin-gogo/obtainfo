#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mysite import private
from pcnile.search import FullTextSearchServer

if __name__ == "__main__":
    fts = FullTextSearchServer(path=private.INDEX_PATH, collection=private.MONGOINFO, ip='localhost', port=9413)
    fts.run()