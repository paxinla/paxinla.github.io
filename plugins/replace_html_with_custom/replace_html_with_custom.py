#!/usr/bin/env python
#coding=utf-8

import itertools

from bs4 import BeautifulSoup
from pelican import signals


def run_plugin(article_gen):
    new_articles = []

    for article in article_gen.articles:
        soup = BeautifulSoup(article._content, 'html.parser')
        tag_no = 1

        print("Wrap div blocks around sections and give each section an ID.")
        h2s = soup.find_all("h2")
        for idx, el in enumerate(h2s):
            els = [i for i in itertools.takewhile(lambda x: x.name not in [el.name, 'div'], el.next_siblings)]
            new_div = soup.new_tag('div', **{"id": "section{!s}".format(idx+1)})
            el.wrap(new_div)
            for tag in els:
                new_div.append(tag)
        content_with_section_id = soup.decode()

        print("Fix controls attribute in audio tag.")
        new_content = content_with_section_id.replace('controls=""', 'controls')

        article._content = new_content
        new_articles.append(article)

    article_gen.articles = new_articles


def register():
    signals.article_generator_pretaxonomy.connect(run_plugin)
