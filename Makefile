run:
	python -i src/debug.py

init: requirements-dev.txt
	pip install -r requirements-dev.txt

build: pyproject.toml
	pip install build
	python -m build

clean:
	rm -r dist src/clappform.egg-info

black:
	black $$(git ls-files '*.py')

lint:
	pylint $$(git ls-files '*.py')
	flake8 $$(git ls-files '*.py')
	black --check $$(git ls-files '*.py')

