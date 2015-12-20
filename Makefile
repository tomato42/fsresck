PYTHON2 := $(shell which python2 2>/dev/null)
PYTHON3 := $(shell which python3 2>/dev/null)

clean:
	rm -rf tests/*.pyc
	rm -rf tests/__pycache__/
	rm -rf fsresck/*.pyc
	rm -rf fsresck/__pycache__/
	rm -rf fsresck/nbd/*.pyc
	rm -rf fsresck/nbd/__pycache__/
	rm -rf tests/nbd/*.pyc
	rm -rf tests/nbd/__pycache__/

test-dev: test
	coverage run --branch --source fsresck -m unittest discover
	coverage report -m

test:
ifdef PYTHON2
	python2 -m unittest discover -v
endif
ifdef PYTHON3
	python3 -m unittest discover -v
endif
ifndef PYTHON2
ifndef PYTHON3
	python -m unittest discover -v
endif
endif
	coverage run --branch --source fsresck -m unittest discover
	coverage report -m
	pep8 fsresck
	pep257 fsresck
