# This Makefile is primarily intended for use on a mac.

.PHONY: upload all

all:
	python setup.py sdist

upload:
	twine upload dist/sermon-0.0.6.tar.gz
