#!/usr/bin/env python
#coding=utf-8

import os
import re
import tempfile
import traceback
import shutil

from pelican import signals
from pelican.readers import MarkdownReader


PTN_PS = re.compile(r"\[ps:(.+?)\]")
RPL_PS = r'<span class="sidenote note no-word-break invisible-sm">\1</span>'

PTN_MUSIC = re.compile(r"\[music:\s*(.+?)\s+link:\s*(.+?)\]")
RPL_MUSIC = r'<div class="container-audio"><span class="music">\1</span><audio controls preload="none"><source src="\2">Your browser dose not Support the audio Tag</audio></div>'

PTN_CODE_BLOCK = re.compile(r"```\s*([\w\d\-_]+)\s*^((.|\r|\n)*?)```$", re.M)
RPL_CODE_BLOCK = r'<pre><code class="lang-\1 hljs">\n\2</code></pre>'


def repl_code_block(instr):
    return PTN_CODE_BLOCK.sub(RPL_CODE_BLOCK, instr)


def repl_side_ps(instr):
    return PTN_PS.sub(RPL_PS, instr)


def repl_music_player(instr):
    return PTN_MUSIC.sub(RPL_MUSIC, instr)


def gen_new_read(func):
    def new_read(*args, **kwargs):
        tmpdir = tempfile.mkdtemp()
        new_path = os.path.join(tmpdir, "fff")
        old_src_path = args[1]

        replacers = [repl_side_ps, repl_music_player, repl_code_block]
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
