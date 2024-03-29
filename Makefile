.PHONY: clean build deploy install publish

# Project settings
PROJECT = webpack-loader

# Virtual environment settings
ENV ?= venv
REPOSITORY ?= pypi

requirements = -r requirements-dev.txt

all: install build

@activate_venv = . $(ENV)/bin/activate
@check_if_venv_active = $(shell python -c 'import sys; print ("1" if sys.prefix != sys.base_prefix else "0")')
@activate_venv_if_not_active = $(if $(filter 1,$(check_if_venv_active)),$(activate_venv),)

clean:
	@echo "Cleaning..."
	@find webpack_loader/ -name '*.pyc' -delete
	@rm -rf ./build ./*egg* ./.coverage ./dist

build: clean
	@$(activate_venv_if_not_active)
	@echo "Building..."
	@pip install -r requirements-dev.txt
	@python setup.py sdist bdist_wheel --universal

install:
	@echo "Installing build dependencies"
	@[ ! -d $(ENV)/ ] && python3 -m venv $(ENV)/ || :
	@$(ENV)/bin/pip install $(requirements)
	@cd tests; npm i

test:
	@$(activate_venv_if_not_active)
	@echo "Running tests..."
	@cd tests; coverage run --source=webpack_loader manage.py test
	@cd tests_webpack5; coverage run --source=webpack_loader manage.py test

publish: build
	@echo "Publishing to $(REPOSITORY)..."
	@$(ENV)/bin/twine upload -r $(REPOSITORY) dist/*

register:
	@echo "Registering package on $(REPOSITORY)..."
	@$(ENV)/bin/twine register -r $(REPOSITORY)
