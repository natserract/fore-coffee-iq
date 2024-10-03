-include .env

setup:
	python3 -m venv .venv
	. .venv/bin/activate

clean:
	rm -rf __pycache__
	rm -rf .venv
