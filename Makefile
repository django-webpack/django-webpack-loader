.PHONY: clean build deploy install publish

# Project settings
PROJECT = webpack-loader

# Virtual environment settings
ENV ?= venv

requirements = -r requirements-dev.txt

# List directories
dist_dir = dist
clean_dirs = $(PROJECT) $(ENV) $(tests_dir) $(shell [ -d $(tox_dir) ] && echo $(tox_dir) || :)

all: install build

clean:
	find webpack_loader/ -name '*.pyc' -delete
	rm -rf ./build ./*egg* ./.coverage

build: clean
	python setup.py sdist bdist_wheel --universal

install:
	[ ! -d $(ENV)/ ] && virtualenv $(ENV)/ || :
	$(ENV)/bin/pip install $(requirements)

publish: build
	$(ENV)/bin/twine upload dist/*
