
import os
from celery import Celery
from celery.schedules import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhaki.settings')

app = Celery('myhaki')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-expired-assignments-every-hour': {
        'task': 'cases.tasks.check_pending_assignments',
        'schedule': timedelta(hours=1), 
        'args': (),
    },
}
app.conf.timezone = 'UTC' 

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

__all__ = ('app',)
