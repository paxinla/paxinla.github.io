#!/usr/bin/env python
#coding=utf-8

import traceback
import logging

import requests
import simplejson as json

from pelicanconf import GITHUB_USER
from pelicanconf import GITHUB_REPO


logger = logging.getLogger("issue_as_comment")
URL_CREATE_ISSUE = "https://api.github.com/repos/{}/{}/issues".format(GITHUB_USER, GITHUB_REPO)


def gen_issue_for_one_post(github_auth_mode, github_password, new_post_title):
    try:
        with requests.Session() as session:
            if github_auth_mode == "password":
                session.auth = (GITHUB_USER, github_password)
            elif github_auth_mode == "token":
                session.headers["Authorization"] = "token {!s}".format(github_password)
            else:
                raise ValueError("Unsupport auth mode {} , expect one of password|token.".format(github_auth_mode))

            new_issue_data = {"title": "《{}》的评论页".format(new_post_title),
                              "body": "请在下面留言，谢谢！",
                              "labels": ["blog_comment"]} 
            resp = session.post(URL_CREATE_ISSUE, json.dumps(new_issue_data))
            if resp.status_code == 201:
                resp_json = resp.json()
                new_issue_number = int(resp_json["number"])
                logger.info("Got issue number {!s} for post《{}》".format(new_issue_number, new_post_title))
                return new_issue_number
            else:
                return None
                raise RuntimeError("Create github issus for post《{}》 FAILED!".format(each_post_title))
    except:
        traceback.print_exc()
