
from celery import shared_task
from .services import assign_case_automatically

@shared_task
def async_assign_case(case_id):
    return assign_case_automatically(case_id)

