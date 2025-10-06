
import logging
from django.utils import timezone
from .utils import haversine
from .models import Case, CaseAssignment
from users.models import LawyerProfile

logger = logging.getLogger(__name__)

MAX_IN_PROGRESS_CASES = 3
CPD_POINTS_PER_CASE = 1
MAX_ASSIGNMENT_ATTEMPTS = 3 

def get_assignment_failed_notice(case_id):
    """Returns the standardized notice for assignment failure."""
    return {
        "case_id": case_id,
        "status": 'assignment_failed',
        "notice": {
            "title": "Notice: Case Rejection",
            "message": "Our lawyers are currently handling high case volumes and we’ve been unable to assign your case after multiple attempts. \n\n Please contact the LSK Admin for further assistance and guidance.",
            "contact": {
                "phone": "+254 700 000 000",
                "email": "adminlsk@gmail.com"
            }
        }
    }


def assign_case_automatically(case_id):
    """
    Selects the best available lawyer based on specialization, case load, and proximity.
    Handles the 3-rejection limit logic.
    """
    try:
        case = Case.objects.get(case_id=case_id)
    except Case.DoesNotExist:
        logger.error(f"Case with ID {case_id} not found for assignment.")
        return None

    total_attempts = CaseAssignment.objects.filter(
        case=case
    ).exclude(status__in=['accepted', 'completed']).count()
    
    if total_attempts >= MAX_ASSIGNMENT_ATTEMPTS:
        case.status = 'assignment_failed'
        case.stage = 'handled'
        case.save()
        logger.warning(f"Case {case_id} reached max assignment attempts ({MAX_ASSIGNMENT_ATTEMPTS}).")
        return get_assignment_failed_notice(case_id)


    if not case.predicted_case_type or not case.latitude or not case.longitude:
        logger.warning(f"Case {case_id} missing type or location data, skipping assignment.")
        return None


    specialization_map = {
        'criminal': 'criminal_law',
        'family': 'family_law',
        'constitutional and human rights': 'constitutional_law',
        'corporate': 'corporate_law',
        'environment': 'environment_law',
        'employment': 'employment_law',
        'civil': 'civil_law',
        'other': 'criminal_law'
    }

    field_name = specialization_map.get(case.predicted_case_type.lower(), None)
    if not field_name:
        logger.error(f"Unknown predicted case type: {case.predicted_case_type}")
        return None

    lawyers = LawyerProfile.objects.filter(verified=True, **{field_name: True})

    assigned_lawyer_ids = CaseAssignment.objects.filter(case=case).values_list('lawyer__profile_id', flat=True)
    lawyers = lawyers.exclude(profile_id__in=assigned_lawyer_ids)

    if not lawyers.exists():
        logger.warning(f"No more available and specialized lawyers to assign for case {case_id}.")
        case.status = 'assignment_failed'
        case.stage = 'handled'
        case.save()
        return get_assignment_failed_notice(case_id)
    
    available_lawyers = []
    for lawyer in lawyers:
        in_progress_count = CaseAssignment.objects.filter(
            lawyer=lawyer,
            status='accepted',
            case__stage__in=['in_progress', 'handled', 'arraignment', 'bail', 'trial']
        ).count()
        if in_progress_count < MAX_IN_PROGRESS_CASES:
            available_lawyers.append(lawyer)

    if not available_lawyers:
        logger.info(f"All specialized lawyers remaining are at max case capacity for case {case_id}.")
        return None 

    lawyer_distances = []
    for lawyer in available_lawyers:
        distance = haversine(case.latitude, case.longitude, lawyer.latitude, lawyer.longitude)
        lawyer_distances.append((lawyer, distance))

    lawyer_distances.sort(key=lambda x: x[1])
    best_lawyer, _ = lawyer_distances[0]

    assignment = CaseAssignment.objects.create(
        lawyer=best_lawyer,
        case=case,
        is_assigned=True,
        confirmed_by_applicant=False,
        confirmed_by_lawyer=False,
        status='pending'
    )

    case.status = 'pending'
    case.save()

    logger.info(f"Case {case_id} assigned to lawyer {best_lawyer.user.email} (Profile ID: {best_lawyer.profile_id}).")

    return {
        "case_id": case.case_id,
        "lawyer_id": best_lawyer.profile_id,
        "lawyer_name": f"{best_lawyer.user.first_name} {best_lawyer.user.last_name}",
        "status": case.status,
        "assignment_id": assignment.assignment_id,
    }


def update_case_and_cpd(assignment: CaseAssignment):
    """Update case stage/status and CPD when both lawyer and applicant confirm."""
    case = assignment.case

    if assignment.status != 'accepted':
        logger.warning(f"Assignment {assignment.assignment_id} is not accepted, cannot finalize completion.")
        return

    if assignment.confirmed_by_lawyer and assignment.confirmed_by_applicant:
        case.stage = 'completed'
        case.status = 'completed'
        case.save()
        
        CaseAssignment.objects.filter(case=case).exclude(assignment_id=assignment.assignment_id).update(status='handled')

        lawyer_profile = assignment.lawyer
        lawyer_profile.cpd_points_2025 = (lawyer_profile.cpd_points_2025 or 0) + CPD_POINTS_PER_CASE
        lawyer_profile.save()
        logger.info(f"Case {case.case_id} completed. CPD awarded to {lawyer_profile.user.email}")
    else:
        logger.info(f"Case {case.case_id} awaiting full confirmation for completion.")

