#!/usr/bin/env python
# coding: utf-8

from bson import json_util as json
from django.http import HttpResponse

JsonResponse = lambda js : HttpResponse(json.dumps(js), content_type="application/json")
