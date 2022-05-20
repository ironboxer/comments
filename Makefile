.PHONY: help reqs dev

help:
	@echo "reqs Update requirements*.txt"
	@echo "dev Install development requirements"
	@echo "test Run pytest"


PIP_COMPILE_ARGS = -i https://mirrors.cloud.tencent.com/pypi/simple/ --extra-index-url https://pypi.doubanio.com/simple -v

reqs: requirements.txt requirments-dev.txt

update-reqs: PIP_COMPILE += -U
update-reqs: reqs

requirements.txt: setup.py
	pip-compile $(PIP_COMPILE_ARGS) setup.py

requirements-dev.txt: requirements-dev.in requirements.txt
	pip-compile requirments-dev.in

dev: reqs
	pip install -r requirements.txt -r requirments-dev.txt
	pip install -e .
	pre-commit install -t pre-commit
	git rev-parse --quiet --verify HEAD && pre-commit install -t commit-msg || echo 'Run `make dev` again after first commit to install commit-msg hooks'

release:
	[ "`git status --short --untracked-files=no`" = "" ] || ( echo You have uncommitted modification; false )
	semantic-release publish


ci-test:
	pytest -rs -vvv --durations 10 --cov=comment/ tests/
	coverage xml

test:
	pytest -sx -vvv tests/

dev-server:
	unicorn comment.main.app --reload
