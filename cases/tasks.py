
# from celery import shared_task
# from .services import assign_case_automatically

# @shared_task(bind=True, max_retries=3)
# def async_assign_case(self, case_id):
#     try:
#         print(f"🔍 Starting auto-assignment for Case #{case_id}...")
#         assignment = assign_case_automatically(case_id)
#         if assignment:
#             print(f"Assigned Case #{case_id} to Lawyer {assignment.lawyer.user.first_name}")
#             return f"Success: Assigned to lawyer {assignment.lawyer_id}"
#         else:
#             raise Exception(f"No eligible lawyer found for case {case_id}")
#     except Exception as exc:
#         print(f"Task failed for case {case_id}: {exc}")
#         self.retry(exc=exc, countdown=60)

# cases/tasks.py

from celery import shared_task
from .services import assign_case_automatically

@shared_task
def async_assign_case(case_id):
    return assign_case_automatically(case_id)

