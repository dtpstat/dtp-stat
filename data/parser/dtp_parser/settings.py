# -*- coding: utf-8 -*-

# Scrapy settings for dtp_parser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import environ
import logging
env = environ.Env(
    PROXY_LIST=(list, [])
)
environ.Env.read_env()

import sys
sys.path.insert(0, env('PROJECT_PATH'))

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dtpstat.settings'

import django
django.setup()

BOT_NAME = 'dtp_parser'

SPIDER_MODULES = ['dtp_parser.spiders']
NEWSPIDER_MODULE = 'dtp_parser.spiders'

LOG_ENABLED = False
LOG_LEVEL='ERROR'
DOWNLOADER_STATS = False
FEED_EXPORT_ENCODING = 'utf-8'
STATS_DUMP = False
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'dtp_parser (+http://dtp-stat.ru)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
logging.disable(logging.INFO)
#ROTATING_PROXY_LIST = env('PROXY_LIST')

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
    'dtp_parser.middlewares.DtpParserDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.corestats.CoreStats': None,
    'scrapy.extensions.memusage.MemoryUsage': None,
    'scrapy.extensions.closespider.CloseSpider': None,
    'scrapy.extensions.logstats.LogStats': None
    }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'dtp_parser.pipelines.DtpParserPipeline': 300,
}