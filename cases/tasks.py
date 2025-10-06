from celery import shared_task
from django.utils import timezone
from .services import assign_case_automatically
from .models import CaseAssignment
import logging

logger = logging.getLogger(__name__)

@shared_task
def async_assign_case(case_id):
    """Asynchronously calls the automatic case assignment logic (used for initial creation and rejection)."""
    logger.info(f"Attempting async assignment for case ID: {case_id}")
    return assign_case_automatically(case_id)

@shared_task
def check_pending_assignments():
    """
    Scheduled task to check for pending assignments older than 24 hours 
    and reassign them automatically, respecting the MAX_ASSIGNMENT_ATTEMPTS.
    """
    
    twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
    expired_assignments = CaseAssignment.objects.filter(
        status='pending',
        assign_date__lte=twenty_four_hours_ago
    )
    
    if not expired_assignments.exists():
        logger.info("No expired pending assignments found.")
        return "No expired pending assignments found."
    
    reassigned_count = 0
    
    for assignment in expired_assignments:
        case_id = assignment.case.case_id
        
        logger.warning(f"Assignment {assignment.assignment_id} for case {case_id} expired. Attempting reassignment...")

        assignment.status = 'reassigned'
        assignment.reassigned_automatically = True
        assignment.reject_reason = "Expired (Not accepted within 24 hours)"
        assignment.save()

        try:
            result = assign_case_automatically(case_id)
            if result and result.get('status') == 'assignment_failed':
                logger.error(f"Case {case_id} failed reassignment after expiry: Max attempts reached.")
            reassigned_count += 1
        except Exception as e:
            logger.error(f"Failed to reassign case {case_id} after expiry: {e}")

    logger.info(f"Triggered reassignment for {reassigned_count} expired cases.")
    return f"Triggered reassignment for {reassigned_count} cases."
