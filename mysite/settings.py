#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
from private import *

gettext = lambda s: s

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

USER_DICT = 'userdict.txt'

TEMPLATE_DEBUG = DEBUG

BLOGS = os.path.join(PROJECT_DIR, '..', 'blog')

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

ALLOWED_HOSTS = ['www.obtainfo.com', 'movie.obtainfo.com', 'www.example.com', 'movie.example.com',]

TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'zh_cn'

LANGUAGES = (
    ('zh_cn', gettext('Simplified Chinese')),
)

SITE_ID = 1

# USE_I18N = True

# USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	('django.template.loaders.cached.Loader', (  
		'app_namespace.Loader',
		'django.template.loaders.filesystem.Loader',
		'django.template.loaders.app_directories.Loader',
	)),
)

MIDDLEWARE_CLASSES = (
	# 'subdomains.middleware.SubdomainURLRoutingMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	# 'django.middleware.locale.LocaleMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	#'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'zinnia.context_processors.version',
)

"""
if DEBUG == False:
	ROOT_URLCONF = 'blog.urls'
else:
	ROOT_URLCONF = 'obtainfo.urls'

SUBDOMAIN_URLCONFS = {
	'www': 'blog.urls',
	'movie': 'obtainfo.urls',
}
"""

ROOT_URLCONF = 'obtainfo.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

DEBUG_TOOLBAR_PANELS = (
	#'debug_toolbar.panels.versions.VersionsPanel',
	#'debug_toolbar.panels.timer.TimerPanel',
	#'debug_toolbar.panels.settings.SettingsPanel',
	#'debug_toolbar.panels.headers.HeadersPanel',
	#'debug_toolbar.panels.request.RequestPanel',
	'debug_toolbar.panels.sql.SQLPanel',
	#'debug_toolbar.panels.staticfiles.StaticFilesPanel',
	#'debug_toolbar.panels.templates.TemplatesPanel',
	#'debug_toolbar.panels.cache.CachePanel',
	#'debug_toolbar.panels.signals.SignalsPanel',
	#'debug_toolbar.panels.logging.LoggingPanel',
	#'debug_toolbar.panels.redirects.RedirectsPanel',
	'debug_toolbar_line_profiler.panel.ProfilingPanel',
	'debug_toolbar_mongo.panel.MongoDebugPanel',
	'template_profiler_panel.panels.template.TemplateProfilerPanel',
	#'debug_toolbar.panels.profiling.ProfilingPanel',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	#'django.contrib.comments',
	#'django.contrib.flatpages',
	#'grappelli',
	#'filebrowser',
	'django.contrib.admin',
	#'subdomains',
	#'flatblocks',
	'obtainfo',
	'putty',
	#'django_xmlrpc',
	'mptt',
	'django_mptt_admin',
	#'tinymce',
	#'flatpages_tinymce',
	#'tagging',
	#'blog',
	#'zinnia',
	#'menu',
	'sendfile',
	#'kickass',
	#'debug_toolbar_line_profiler',
	#'template_profiler_panel',
	#'debug_toolbar_mongo',
	#'debug_toolbar',
)

from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS
ZINNIA_ENTRY_BASE_MODEL = 'blog.models.AbstractEntry'

TINYMCE_DEFAULT_CONFIG = {
    'file_browser_callback': "djangoFileBrowser",
    'mode': "exact",
    'theme': "advanced",
    'skin' : "o2k7",
    'skin_variant' : "silver",
    'height': "350",
    'width': "800",
    'relative_urls': False,
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_resizing' : True,
    'plugins': "nonbreaking, contextmenu, directionality, fullscreen, paste, preview, searchreplace, spellchecker, visualchars, wordcount",
    'paste_auto_cleanup_on_paste' : True,
    'nonbreaking_force_tab': True,
    'theme_advanced_buttons1' : "formatselect,fontsizeselect,|,undo,redo,|,cut,copy,paste,pastetext,pasteword,|,search,replace,|,visualchars,visualaid,cleanup,code,preview,fullscreen",
    'theme_advanced_buttons2' : "bold,italic,underline,strikethrough,|,forecolor,backcolor,removeformat,|,justifyleft,justifycenter,justifyright,justifyfull,|,sub,sup,|,bullist,numlist,|,outdent,indent,|,link,unlink,anchor,image,blockquote,hr,charmap,",
    'theme_advanced_buttons3' : "",
}

# set file cache system
if DEBUG == False and platform.system() == 'Linux': # linux system with deploy state
	CACHES = {
		'default': {
			'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
			'LOCATION': '/opt/cache/cache',
			'TIMEOUT': 60 * 60 * 5,
			'OPTIONS': {
				'MAX_ENTRIES': 600
			}
		}
	}
	"""
	CACHES = {
		'default': {
			'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
			'LOCATION': 'obtainfo',
			'TIMEOUT': 60 * 60 * 5,
			'OPTIONS': {
				'MAX_ENTRIES': 600
			}
		}
	}
	"""
else:
	CACHES = {
		'default': {
			'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
		}
	}

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 5

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# log file need to change owner, exampel: chown www-data obtainfo
# set disable_existing_loggers = True
if DEBUG == False and platform.system() == 'Linux':
    log_file = '/var/log/obtainfo/obtainfo.log'
else:
    log_file = 'obtainfo.log'

SESSION_COOKIE_NAME = 'obtainfo'
if DEBUG == False:
	SESSION_COOKIE_DOMAIN='.obtainfo.com'
	SESSION_COOKIE_AGE = 60 * 60 * 24 * 365 * 2 # two years
else:
	SESSION_COOKIE_DOMAIN='.example.com'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'obtainfo': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'mysite': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'blog': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
