.PHONY: clean build deploy install publish

# Project settings
PROJECT = webpack-loader

# Virtual environment settings
ENV ?= venv
REPOSITORY ?= pypi

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
	@[ ! -d $(ENV)/ ] && python3 -m venv $(ENV)/ || :
	@$(ENV)/bin/pip install $(requirements)

generate-rst:
	@pandoc --from=markdown --to=rst --output=README.rst README.md

publish: generate-rst build
	@echo "Publishing to pypi..."
	@$(ENV)/bin/twine upload -r $(REPOSITORY) dist/*

register:
	@echo "Registering package on pypi..."
	@$(ENV)/bin/twine register -r $(REPOSITORY)
