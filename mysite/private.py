#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os.path
import pymongo
import platform

"""
Postgresql 连接信息
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'obtainfo',
        'USER': 'postgres',
        'PASSWORD': '1991223',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# MongoDB 连接池
MONGOPOOL = pymongo.Connection()
# MongoDB 主要数据库，服务器数据库
MONGODB = MONGOPOOL.server
# 电影、电视剧信息简介存放的集合
MONGOINFO = MONGODB.info
# 在线、网盘、下载资源存储的集合
MONGORESOURCE = MONGODB.resource

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x#0zw6o_z8x_w3wqbd=4u^r600lc+7p17sm-6yfx2pu=8u*ok+'

# 服务器 IP
SERVER_IP = '106.186.122.161'

"""
基于服务器IP设置写目录信息
"""
if socket.gethostbyname(socket.gethostname()) == SERVER_IP:
    DEBUG = False
    LOCATION = 'SERVER'
    INDEX_PATH = '/opt/index'
    TORRENT_DIR = '/opt/torrent'
    IMAGE_DIR = '/opt/images'
    HTML_DIR = '/opt/html'
    SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
else:
    DEBUG = True
    LOCATION = 'LOCAL'
    LEVEL = 7
    SENDFILE_BACKEND = 'sendfile.backends.development'

    # set all kinds of filter
    if platform.system() == 'Linux':
        BASE_PATH = "/home/zhy/workspace/obtainfostatic/store"
        INDEX_PATH = os.path.join(BASE_PATH, 'index')
        TORRENT_DIR = os.path.join(BASE_PATH, 'torrent')
        IMAGE_DIR = os.path.join(BASE_PATH, 'image')
        QINIU_IMAGE_DIR = os.path.join(BASE_PATH, 'image')
        HTML_DIR = os.path.join(BASE_PATH, 'html')
        DBDIR = os.path.join(BASE_PATH, 'wolf')
    else:
        INDEX_PATH = 'D:\\obtainfo\\Store\\index'
        TORRENT_DIR = 'D:\\obtainfo\\Store\\torrent'
        IMAGE_DIR = 'D:\\obtainfo\\Store\\image'
        QINIU_IMAGE_DIR = 'D:\\obtainfo\\Store\\image'
        HTML_DIR = "D:\\obtainfo\\Store\\html"
        DBDIR = 'D:\\obtainfo\\Store\\db'
