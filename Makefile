.PHONY: clean build deploy install publish

# Project settings
PROJECT = webpack-loader

# Virtual environment settings
ENV ?= venv

requirements = -r requirements-dev.txt

all: install build

clean:
	@echo "Cleaning..."
	@find webpack_loader/ -name '*.pyc' -delete
	@rm -rf ./build ./*egg* ./.coverage ./dist

build: clean
	@echo "Building..."
	@python setup.py sdist bdist_wheel --universal

install:
	@echo "Installing build dependencies"
	@[ ! -d $(ENV)/ ] && virtualenv $(ENV)/ || :
	@$(ENV)/bin/pip install $(requirements)

publish: build
	@echo "Publishing to pypi..."
	@$(ENV)/bin/twine upload dist/*
