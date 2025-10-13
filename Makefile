.PHONY: all lint test test-cov viz-barplot install dev clean distclean

PYTHON ?= python

all: viz-barplot barplot2-visualizer

lint:
	q2lint
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_taxa

q2_taxa/assets/barplot/dist:
	cd q2_taxa/assets/barplot && \
	npm install --no-save && \
	npm run build && \
	cp licenses/* dist/

viz-barplot: q2_taxa/assets/barplot/dist

install: all
	$(PYTHON) -m pip install -v .

dev: all
	pip install -e .

clean: distclean
	rm -rf q2_taxa/assets/barplot/node_modules
	rm -rf q2_taxa/_barplot_visualizer/node_modules

distclean:
	rm -rf q2_taxa/assets/barplot/dist
	rm -rf q2_taxa/_barplot_visualizer/dist

q2_taxa/_barplot_visualizer/dist:
	cd q2_taxa/_barplot_visualizer/ && \
	npm install && npm run build

barplot2-visualizer: q2_taxa/_barplot_visualizer/dist
