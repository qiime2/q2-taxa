.PHONY: all lint test test-cov viz-barplot install dev clean distclean

PYTHON ?= python

all: viz-barplot

lint:
	q2lint
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_taxa

q2_taxa/assets/barplot/dist:
	cd q2_taxa/assets/barplot && \
	npm install && \
	npm run build && \
	cp licenses/* dist/

viz-barplot: q2_taxa/assets/barplot/dist

install: all
	$(PYTHON) setup.py install

dev: all
	pip install -e .

clean: distclean
	rm -rf q2_taxa/assets/barplot/node_modules

distclean:
	rm -rf q2_taxa/assets/barplot/dist
