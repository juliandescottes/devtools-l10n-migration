HERE = $(shell pwd)
VENV = $(HERE)/venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install --no-deps

.PHONY: all test docs build_extras

all: build

$(PYTHON):
	virtualenv $(VENV)

build: $(PYTHON)
	$(PYTHON) setup.py develop

clean:
	rm -rf $(VENV)

test_dependencies:
	$(BIN)/pip install flake8 tox

test: build test_dependencies
	$(BIN)/flake8 migrate
	$(BIN)/tox

