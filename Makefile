# This Makefile is primarily intended for use on a mac.

.PHONY: upload all

all:
	python setup.py sdist

upload:
	@open https://pypi.python.org/pypi
	@sleep 0.3
	@open dist
