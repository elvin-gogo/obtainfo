#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


def md5sum(file):
    m = hashlib.md5()
    while 1:
        d = file.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()


def group_list(l, block):
    size = len(l)
    return [l[i:i + block] for i in range(0, size, block)]


# dump json peer item peer line
class DumpJson(object):
    def __init__(self, file):
        self.file = file
        self.first_item = True

    def start_exporting(self):
        self.file.write("[")

    def finish_exporting(self):
        self.file.write("]")

    def export_item(self, item):
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(', \n')

        self.file.write(json.dumps(item))

    def dump(self, items):
        self.start_exporting()
        count = 0
        for i in items:
            try:
                self.export_item(i)
            except:
                count += 1
                print count
        self.finish_exporting()
