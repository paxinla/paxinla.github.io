#!/usr/bin/env python
#coding=utf-8

import itertools

from bs4 import BeautifulSoup
from pelican import signals


def run_plugin(article_gen):
    print("Wrap div blocks around sections and give each section an ID.")
    new_articles = []

    for article in article_gen.articles:
        soup = BeautifulSoup(article._content, 'html.parser')
        tag_no = 1

        h2s = soup.find_all("h2")
        for idx, el in enumerate(h2s):
            els = [i for i in itertools.takewhile(lambda x: x.name not in [el.name, 'div'], el.next_siblings)]
            new_div = soup.new_tag('div', **{"id": "section{!s}".format(idx+1)})
            el.wrap(new_div)
            for tag in els:
                new_div.append(tag)
        article._content = soup.decode()
        new_articles.append(article)

    article_gen.articles = new_articles


def register():
    signals.article_generator_pretaxonomy.connect(run_plugin)
