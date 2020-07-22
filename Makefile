clean:
	rm -rf *.egg-info build dist .pytest_cache .tox .coverage
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete

deploy: clean
	python setup.py bdist_wheel --universal
	twine upload -r AIPlatform dist/*

dev:
	pip install pipenv
	echo ENVIRONMENT=dev >> .env
	echo DB_PASSWORD= >> .env
	pipenv install --dev

test:
	pipenv check
	pipenv run pytest --verbose --cov=oml
	pipenv run flake8 oml tests
	pipenv run bandit --recursive oml

docker-build:
	docker build -t oml .

docker-run:
	docker run -it --rm -p 127.0.0.1:8000:8000 oml
