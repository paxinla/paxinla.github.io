#!/usr/bin/env python
#coding=utf-8

import sys
import os
import re
import traceback
from datetime import datetime

import requests
import simplejson as json

from pelicanconf import GITHUB_USER
from pelicanconf import GITHUB_REPO


POST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "content")
PTN_POST_DATE = re.compile(r"^[Dd]ate:\s+([\d: -]+)\s*$")
PTN_POST_CMTID = re.compile(r"^[Cc]omment[Ii]d:\s+([\?])\s*$")
PTN_POST_TITLE = re.compile(r"^[Tt]itle:\s+([\w ]+)\s*$")
URL_CREATE_ISSUE = "https://api.github.com/repos/{}/{}/issues".format(GITHUB_USER, GITHUB_REPO)


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
                    t1 = True

                m2 = PTN_POST_DATE.match(each_line)
                if m2:
                    p_date = datetime.strptime(m2.group(1), "%Y-%m-%d %H:%M:%S")
                    t2 = True

                m3 = PTN_POST_TITLE.match(each_line)
                if m3:
                    p_title = m3.group(1)
                    t3 = True

            if t1 and t2 and t3:
                if_accept = True
        except:
            traceback.print_exc()

    return (if_accept, p_date, p_title, filepath)


def find_all_new_posts():
    cand_mds = []
    for root, _, files in os.walk(POST_DIR):
        for each_file in files:
            if each_file.endswith(".md"):
                cand_filepath = os.path.join(root, each_file)
                print("Check {}".format(cand_filepath))
                rs = filter_md(cand_filepath)
                if rs[0]:
                    print("    Accept {}".format(cand_filepath))
                    cand_mds.append(rs)

    cand_mds.sort(key=lambda x: x[1])

    return cand_mds


def gen_issue_for_posts(github_auth_mode, github_password, new_posts):
    handled_posts = []

    try:
        with requests.Session() as session:
            if github_auth_mode == "password":
                session.auth = (GITHUB_USER, github_password)
            elif github_auth_mode == "token":
                session.headers["Authorization"] = "token {!s}".format(github_password)
            else:
                raise ValueError("Unsupport auth mode {} , expect one of password|token.".format(github_auth_mode))

            for each_post in new_posts:
                each_post_title = each_post[2]
                each_post_path = each_post[3]
                new_issue = {"title": "《{}》的评论页".format(each_post_title),
                             "body": "请在下面留言，谢谢！",
                             "labels": ["blog_comment"]} 
                resp = session.post(URL_CREATE_ISSUE, json.dumps(new_issue))
                if resp.status_code == 201:
                    resp_json = resp.json()
                    new_issue_number = int(resp_json["number"])
                    print("Got issue number {!s} for post《{}》".format(new_issue_number, each_post_title))
                    handled_posts.append((each_post_path, new_issue_number))
                else:
                    raise RuntimeError("Create github issus for post《{}》 FAILED!".format(each_post_title))
    except:
        traceback.print_exc()

    return handled_posts


def update_comment_id(target_posts):
    for each_post in target_posts:
        post_path = each_post[0]
        post_comment_id = each_post[1]
        new_content = None
        with open(post_path, "r") as rf:
            old_content = rf.read()
            new_content = PTN_POST_CMTID.sub("CommentId: {!s}".format(post_comment_id), old_content)

        with open(post_path, "w") as wf:
            wf.write(new_content)


if __name__ == "__main__":
    auth_mode = sys.argv[1]
    passwd = sys.argv[2]
    all_new_posts = find_all_new_posts()
    posts_with_issue_id = gen_issue_for_posts(auth_mode, password, all_new_posts)
    update_comment_id(posts_with_issue_id)
