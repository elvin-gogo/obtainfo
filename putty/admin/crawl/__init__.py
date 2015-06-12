#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hao123 import Hao123TV

Collections = {
    'hao123_tv' : Hao123TV(settings.MONGOPOOL),
    'quick' : MovieQuick(settings.MONGOPOOL),
    'netdisk' : MovieNetdisk(settings.MONGOPOOL),
}
