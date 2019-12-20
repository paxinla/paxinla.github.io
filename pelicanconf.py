#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from datetime import datetime


AUTHOR = "Charles"
SITENAME = "Charles's Blog"


SITEURL = "https://paxinla.github.io"
GITHUB_URL = "https://github.com/paxinla"
GITHUB_USER = "paxinla"
GITHUB_SHOW_USER_LINK = True
GITHUB_REPO = "paxinla.github.io"
INDEX_TITLE_UP = "作为思索的人而行动，"
INDEX_TITLE_DOWN = "作为行动的人而思索"
INDEX_DESCRIPTION = "这里只有我的呓语 ... ..."


DEFAULT_LANG = "zh"
TIMEZONE = "Asia/Shanghai"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %a"
COPYRIGHT_YEAR = str(datetime.now().year)


DEFAULT_CATEGORY ="杂谈"


PATH = "content"
STATIC_PATHS = ["static",
                "images",
                "images/favicon.ico"]
AVATAR = "static/user_avatar.jpeg"
THEME = "themes/pxltheme"
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{slug}.html'
PAGE_PATHS = ["pages"]
PAGE_URL = "pages/{slug}.html"
PAGE_SAVE_AS = "pages/{slug}.html"
CATEGORY_URL = 'category/{slug}.html'
CATEGORY_SAVE_AS = 'category/{slug}.html'
TAG_URL = 'tag/{slug}.html'
TAG_SAVE_AS = 'tag/{slug}.html'
AUTHOR_URL = 'author/{slug}.html'
AUTHOR_SAVE_AS = 'author/{slug}.html'


PLUGIN_PATHS = ["pelican_plugins", "plugins"]
PLUGINS = ["sitemap", "summary", "gravatar",
           "replace_content_with_custom", "replace_html_with_custom"]
SITEMAP = {
    "format": "xml",
}
DISPLAY_TAGS_INLINE = True
OUTPUT_SOURCES = False
OUTPUT_SOURCES_EXTENSION = ".md"
MARKDOWN = {
    'extensions': ['markdown.extensions.fenced_code', 'markdown.extensions.codehilite', 'markdown.extensions.extra', 'markdown.extensions.meta'],
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight',
                                           'linenums': True,
                                           'guess_lang': True,
                                           'use_pygments': True}
    },
    'output_format': 'html5',
    'lazy_ol': False
}


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
RELATIVE_URLS = False
LOAD_CONTENT_CACHE = True
CHECK_MODIFIED_METHOD = "md5"

# Blogroll
LINKS = (("Pelican", "http://getpelican.com/"),
         ("Python.org", "http://python.org/"))
# Social widget
SOCIAL = (("github", "https://github.com/paxinla"),)


DEFAULT_PAGINATION = 10
