from celery import Celery, shared_task
from config import config
from celery.schedules import crontab

celery = Celery('LMS')
celery.config_from_object(config['celery'])

@shared_task
def test():
    return "Hi mom"

# run task every 10 sec
@celery.on_after_configure.connect
def hello(sender, **kwargs):
    sender.add_periodic_task(10, test.s(), name='test')

