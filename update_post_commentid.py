#!/usr/bin/env python
#coding=utf-8

import sys
import os
import re
import traceback
import logging
from datetime import datetime
from collections import namedtuple

import requests
import simplejson as json

from create_github_comment_page import gen_issue_for_one_post


logger = logging.getLogger("issue_as_comment")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] (%(pathname)s:%(lineno)d@%(funcName)s) -> %(message)s"))
logger.addHandler(handler)

POST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "content")
PTN_POST_DATE = re.compile(r"^[Dd]ate:\s+([\d: -]+)\s*$")
PTN_POST_CMTID = re.compile(r"^[Cc]omment[Ii]d:\s+([\?])\s*$")
PTN_POST_TITLE = re.compile(r"^[Tt]itle:\s+([\S ]+)\s*$")    # 用 ? 作新文章的评论id占位符

NewPostInfo = namedtuple("NewPostInfo", ["is_new", "post_date", "post_title", "filepath"])


def filter_md(filepath):
    if_accept = False
    p_date = None
    p_title = None

    with open(filepath, 'r') as f:
        t1 = False
        t2 = False
        t3 = False
        try:
            for each_line in f:
                m1 = PTN_POST_CMTID.match(each_line)
                if m1:
                    comment_id = m1.group(1)
                    logger.debug("comment_id={!s}".format(comment_id))
                    t1 = True

                m2 = PTN_POST_DATE.match(each_line)
                if m2:
                    p_date = datetime.strptime(m2.group(1), "%Y-%m-%d %H:%M:%S")
                    logger.debug("post_date={!s}".format(p_date))
                    t2 = True

                m3 = PTN_POST_TITLE.match(each_line)
                if m3:
                    p_title = m3.group(1)
                    logger.debug("post_title={!s}".format(p_title))
                    t3 = True

            if t1 and t2 and t3:
                if_accept = True
        except:
            traceback.print_exc()

    return NewPostInfo(is_new=if_accept,
                       post_date=p_date,
                       post_title=p_title,
                       filepath=filepath)


def find_all_new_posts():
    cand_mds = []
    for root, _, files in os.walk(POST_DIR):
        for each_file in files:
            if each_file.endswith(".md"):
                cand_filepath = os.path.join(root, each_file)
                logger.info("Check {}".format(cand_filepath))
                rs = filter_md(cand_filepath)
                if rs.is_new:
                    logger.info("    Accept {}".format(cand_filepath))
                    cand_mds.append(rs)

    cand_mds.sort(key=lambda x: x.post_date)

    return cand_mds


def update_comment_id(post_title, post_path, comment_id):
    new_content = None

    with open(post_path, 'r', encoding="utf8") as rf:
        old_content = rf.read()
        new_content = PTN_POST_CMTID.sub("CommentId: {!s}".format(comment_id), old_content)

    with open(post_path, 'w', encoding="utf8") as wf:
        if new_content is not None:
            wf.write(new_content)
            logger.debug("  attached comment id {!s} to post {}".format(comment_id, post_path))
        else:
            logger.error("  FAIL to replace comment id in post {} !".format(post_path))


def process(auth_mode, passwd):
    all_new_posts = find_all_new_posts()

    for each_new_post in all_new_posts:
        post_issue_id = gen_issue_for_one_post(auth_mode, passwd, each_new_post.post_title)
        if post_issue_id is not None:
            update_comment_id(each_new_post.post_title, each_new_post.filepath, post_issue_id)
        else:
            logger.error("No comment id for post {}".format(each_new_post.post_title))


if __name__ == "__main__":
    process(sys.argv[1], sys.argv[2])
