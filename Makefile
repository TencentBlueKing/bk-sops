run:
	python manage.py runserver 0.0.0.0:8000
flake8:
	flake8 --config=.flake8 .
celery:
	python manage.py celery worker --settings=settings -l info -c 4 --autoreload
beat:
	python manage.py celery beat
cache:
	python manage.py createcachetable
redis:
	redis-server
kill:
	taskkill -f -im python
	taskkill -f -im python.exe
