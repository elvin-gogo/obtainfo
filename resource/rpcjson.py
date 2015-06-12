#!/usr/bin/env python
# coding: utf-8

"""
try:
    import jsonlib2 as json
    JsonParseError = json.ReadError
except ImportError:
    try:
        import simplejson as json
        JsonParseError = json.JSONDecodeError
    except ImportError:
        import json
        JsonParseError = ValueError
"""

from bson import json_util as json
JsonParseError = ValueError

