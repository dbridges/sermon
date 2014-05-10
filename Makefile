# This Makefile is primarily intended for use on a mac.

.PHONY: upload all clean

all:
	python setup.py sdist

clean:
	rm -f -r build/*

upload:
	twine upload dist/sermon-1.0.1.tar.gz
