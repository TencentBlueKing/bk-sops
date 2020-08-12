web: gunicorn wsgi -w 8 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
dworker: python manage.py celery worker -Q default -n default@%h -c 6 -l info --maxtasksperchild=50
pworker: python manage.py celery worker -Q pipeline,pipeline_priority -n pipeline_worker@%h -c 6 -l info --maxtasksperchild=50
sworker: celery worker -A blueapps.core.celery -P gevent -Q service_schedule,service_schedule_priority -c 30 -l info -n schedule_worker@%h --maxtasksperchild=50
cworker: python manage.py celery worker -Q pipeline_additional_task,pipeline_additional_task_priority -n common_worker@%h -c 6 -l info --maxtasksperchild=50
api_pworker: python manage.py celery worker -Q api_task_queue_pipeline_priority -n api_task_pipeline_worker@%h -c 6 -l info --maxtasksperchild=50
api_sworker: celery worker -A blueapps.core.celery -P gevent -Q api_task_queue_service_schedule_priority -n api_task_schedule_worker@%h -c 6 -l info --maxtasksperchild=50
periodic_pworker: python manage.py celery worker -Q periodic_task_queue_pipeline_priority -n periodic_task_pipeline_worker@%h -c 6 -l info --maxtasksperchild=50
periodic_sworker: celery worker -A blueapps.core.celery -P gevent -Q periodic_task_queue_service_schedule_priority -n periodic_task_schedule_worker@%h -c 6 -l info --maxtasksperchild=50
beat: python manage.py celery beat -l info
# redis: /app/redis-server /app/redis.conf # 暂时使用 paas v2 的 redis 资源
