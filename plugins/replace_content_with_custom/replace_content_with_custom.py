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

PTN_CODE_BLOCK = re.compile(r"```\s*([\w\d\-_]+)\s*^((.|\r|\n)*?)```$", re.M)
RPL_CODE_BLOCK = r'<pre><code class="lang-\1 hljs">\n\2</code></pre>'


def repl_code_block(instr):
    return PTN_CODE_BLOCK.sub(RPL_CODE_BLOCK, instr)


def repl_side_ps(instr):
    return PTN_PS.sub(RPL_PS, instr)


def gen_new_read(func):
    def new_read(*args, **kwargs):
        tmpdir = tempfile.mkdtemp()
        new_path = os.path.join(tmpdir, "fff")
        old_src_path = args[1]
        try:
            with open(old_src_path, "r", encoding="utf8") as rf, open(new_path, 'w', encoding="utf8") as wf:
                wf.write(repl_side_ps(repl_code_block(rf.read())))
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
