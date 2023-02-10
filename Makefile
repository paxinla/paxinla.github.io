PELICAN=pelican
PELICANOPTS=

BASEDIR=$(PWD)
BINDIR=$(BASEDIR)/ENV/bin
OUTPUTDIR=$(BASEDIR)/output
CSSDIR=$(OUTPUTDIR)/theme/css
JSDIR=$(OUTPUTDIR)/theme/js
INPUTDIR=$(BASEDIR)/content
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_TOKEN=

help:
	@echo '+--------------------------------------------------------------------------+'
	@echo '| Makefile for a pelican Web site                                          |'
	@echo '|                                                                          |'
	@echo '| Usage:                                                                   |'
	@echo '|    make init                        install pelican                      |'
	@echo '|    make build                       (re)generate the web site on local   |'
	@echo '|    make html                        (re)generate the web site            |'
	@echo '|    make clean                       remove the generated files           |'
	@echo '|    make regenerate                  regenerate files upon modification   |'
	@echo '|    make publish                     generate using production settings   |'
	@echo '|    make serve                       serve site at http://localhost:8000  |'
	@echo '|    make gen_issue                   generate github issue for posts      |'
	@echo '+--------------------------------------------------------------------------+'

init:
	test -d ENV || { virtualenv --no-site-packages ENV ;}
	$(BINDIR)/pip install -r requirements_cn.txt

clean:
	find $(OUTPUTDIR) -mindepth 1 -delete

build: clean
	$(BINDIR)/$(PELICAN) content
	$(BASEDIR)/local_gen.sh
	@echo 'Build html files.'

html: clean
	$(PELICAN) content
	@echo 'Build html files.'
	find $(CSSDIR) -type f -name '*.css' -a ! -name 'blogstyle.css' -delete
	find $(CSSDIR) -type f -name '*.map' -delete
	@echo 'Clear source CSS files.'
	find $(JSDIR) -type f -name '*.js' -a ! -name 'packed.js' -a ! -name '*_toc.js' -a ! -name 'comments.js' -a ! -name 'L2Dwidget.*' -a ! -name 'animejs.js' -a ! -name 'fireworks.min.js' -delete
	find $(JSDIR) -type f -name '*.map' -a ! -name 'L2Dwidget.*' -delete
	@echo 'Clear source JavaScript files.'

$(OUTPUTDIR)/%.html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)
	cp .well-known $(OUTPUTDIR)/

regenerate: clean
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve: build
	cd $(OUTPUTDIR) && $(BINDIR)/python -m pelican.server
	@echo 'Open URL: http://localhost:8000'

publish: html
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)
