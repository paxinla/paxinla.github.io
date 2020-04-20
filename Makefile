PELICAN=pelican
PELICANOPTS=

BASEDIR=$(PWD)
BINDIR=$(BASEDIR)/ENV/bin
OUTPUTDIR=$(BASEDIR)/output
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

gen_issue:
	python update_post_commentid.py token $(GITHUB_TOKEN)

build: clean
	$(BINDIR)/$(PELICAN) content
	$(BASEDIR)/local_gen.sh
	@echo 'Build html files.'

html: clean
	$(PELICAN) content
	@echo 'Build html files.'

$(OUTPUTDIR)/%.html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

regenerate: clean
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve: build
	cd $(OUTPUTDIR) && $(BINDIR)/python -m pelican.server
	@echo 'Open URL: http://localhost:8000'

publish: html
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)
