# # import os
# # from celery import Celery

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhaki.settings')

# # app = Celery('myhaki')

# # app.config_from_object('django.conf:settings', namespace='CELERY')

# # app.autodiscover_tasks()
# # @app.task(bind=True)
# # def debug_task(self):
# #     print(f'Request: {self.request!r}')


# import os
# from celery import Celery
# from celery.schedules import timedelta

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhaki.settings')

# app = Celery('myhaki')

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()

# # Celery Beat settings
# app.conf.beat_schedule = {
#     'check-and-reassign-overdue-cases-every-hour': {
#         'task': 'cases.tasks.check_and_reassign_overdue_cases',
#         'schedule': timedelta(hours=1), # Runs every hour
#         'args': (),
#     },
# }
# app.conf.timezone = 'UTC' # Or your local timezone like 'Africa/Nairobi'

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')



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
