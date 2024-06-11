#!/usr/bin/env python
#coding=utf-8

import os
import re
import tempfile
import traceback
import random
import shutil

from pelican import signals
from pelican.readers import MarkdownReader


PTN_PS = re.compile(r"\[ps:(.+?)\]")
RPL_PS = r'<span class="sidenote note no-word-break invisible-sm">\1</span>'

PTN_LIST = re.compile(r"\[list:(.+?)\]")
RPL_LIST = r'<p class="list-title">\1</p>'

PTN_MUSIC = re.compile(r"\[music:\s*(.+?)\s+link:\s*(.+?)\]")
RPL_MUSIC = r'<div class="container-audio"><span class="music">\1</span><audio controls preload="none"><source src="\2">Your browser dose not Support the audio Tag</audio></div>'

PTN_CODE_BLOCK = re.compile(r"```\s*([\w\d\-_]+)\s*^((.|\r|\n)*?)```$", re.M)
RPL_CODE_BLOCK = r'<pre><code class="lang-\1 hljs">\n\2</code></pre>'

PTN_FLINK = re.compile(r"\[flink:\s*(.+?)\s+name:\s*(.+?)\s+desc:\s*(.+?)\s+logo:\s*(.+?)\]")
RPL_FLINK = r'''
<div class="flink-item" style="background-color: THECOLOR !important;">
  <div class="flink-title">
    <a href="\1" target="_blank" rel="external noopener noreferrer">\2</a>
  </div>
  <div class="flink-link">
    <div class="flink-link-ico" style="background: url(\4); background-size: 42px auto;"></div>
    <div class="flink-link-text">\3</div>
  </div>
</div>'''

PTN_FDLINK = re.compile(r"\[fdlink:\s*(.+?)\s+name:\s*(.+?)\s+desc:\s*(.+?)\s+logo:\s*(.+?)\]")
RPL_FDLINK = r'''
<div class="flink-item" style="background-color: black !important;">
  <div class="flink-title" style="color: white !important;">
    <a href="\1" target="_blank" rel="external noopener noreferrer" style="color: white !important; text-decoration: line-through 5px; text-decoration-color: red;">\2</a>
  </div>
  <div class="flink-link">
    <div class="flink-link-ico" style="background: url(\4); background-size: 42px auto;"></div>
    <div class="flink-link-text" style="color: white !important; text-decoration: line-through 2px; text-decoration-color: red;">\3</div>
  </div>
</div>'''

BG_COLORS = [['#d3869b'],  #红组
             ['#A0DAD0', '#c8cfbc', '#c2d94c'],  #绿组
             ['#f1f8ff', '#4899c0', '#9a76d7'],  #蓝/紫组
             ['#f68e5f', '#f9bb3c', '#fff0d6', '#fd8b4a'],  #黄/橙组
             ['#b29499', '#e0eaf0']  #灰组
            ]
BG_COLORS_GROUPS = len(BG_COLORS)-1
last_color_groupno = set()

def repl_code_block(instr):
    return PTN_CODE_BLOCK.sub(RPL_CODE_BLOCK, instr)


def repl_side_ps(instr):
    return PTN_PS.sub(RPL_PS, instr)


def repl_list_title(instr):
    return PTN_LIST.sub(RPL_LIST, instr)


def repl_music_player(instr):
    return PTN_MUSIC.sub(RPL_MUSIC, instr)


def repl_friend_link(instr):
    new_content = PTN_FLINK.sub(RPL_FLINK, instr)

    if 'THECOLOR' in new_content:
        global last_color_groupno
        if len(last_color_groupno) == 3:
            last_color_groupno.clear()

        color_groupno = random.randint(0, BG_COLORS_GROUPS-1)
        while color_groupno in last_color_groupno:
            color_groupno = random.randint(0, BG_COLORS_GROUPS-1)
        last_color_groupno.add(color_groupno)

        new_content = new_content.replace('THECOLOR', random.choice(BG_COLORS[color_groupno]), 1)

    return new_content

def repl_friend_dead_link(instr):
    return PTN_FDLINK.sub(RPL_FDLINK, instr)


def gen_new_read(func):
    def new_read(*args, **kwargs):
        tmpdir = tempfile.mkdtemp()
        new_path = os.path.join(tmpdir, "fff")
        old_src_path = args[1]

        replacers = [repl_code_block, repl_side_ps, repl_list_title, repl_music_player, repl_friend_link, repl_friend_dead_link]
        try:
            with open(old_src_path, "r", encoding="utf8") as rf, open(new_path, 'w', encoding="utf8") as wf:
                content = rf.read()
                for replacer in replacers:
                    content = replacer(content)
                wf.write(content)
            return func(args[0], new_path)
        except:
            traceback.print_exc()
        else:
            os.remove(new_path)
        finally:
            shutil.rmtree(tmpdir)

    return new_read


def run_plugin(readers):
    print("Replace string in source markdown files.")
    for clss in readers.reader_classes.values():
        if clss is MarkdownReader:
            old_read_func = clss.read
            clss.read = gen_new_read(old_read_func)


def register():
    signals.readers_init.connect(run_plugin)
