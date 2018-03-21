PELICAN=pelican
PELICANOPTS=

BASEDIR=$(PWD)
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
	@echo '|    make html                        (re)generate the web site            |'
	@echo '|    make clean                       remove the generated files           |'
	@echo '|    make regenerate                  regenerate files upon modification   |'
	@echo '|    make publish                     generate using production settings   |'
	@echo '|    make serve                       serve site at http://localhost:8000  |'
	@echo '|    make gen_issue                   generate github issue for posts      |'
	@echo '+--------------------------------------------------------------------------+'


clean:
	find $(OUTPUTDIR) -mindepth 1 -delete

gen_issue:
	python update_post_commentid.py token $(GITHUB_TOKEN)

html: clean $(OUTPUTDIR)/index.html
	@echo 'Done'

$(OUTPUTDIR)/%.html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

regenerate: clean
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve:
	cd $(OUTPUTDIR) && python -m pelican.server

publish: html
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)
