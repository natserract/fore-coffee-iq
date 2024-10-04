-include .env

install-py:
	@echo "Installing python dependencies"
	pip install --upgrade pip
	pip install -r requirements.txt -vvv
	pip install fastapi[standard]

install-js:
	@echo "Installing web dependencies"
	cd web/ && yarn install

install: install-py install-js

run-server:
	fastapi run api/main.py

run-web:
	cd web/ && yarn build && yarn start

run:
	python scripts/run.py

dev:
	python scripts/dev.py

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf __pycache__
	rm -rf .venv
	rm -rf dist/
