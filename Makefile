pep8:
	flake8 sequere --ignore=E501,E127,E128,E124

test:
	coverage run --branch --source=sequere manage.py test sequere
	coverage report --omit=sequere/test*

release:
	python setup.py sdist register upload -s
