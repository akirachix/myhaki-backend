

from .models import Case, CaseAssignment
from users.models import LawyerProfile
from .utils import haversine

def assign_case_automatically(case_id):
    try:
        case = Case.objects.get(pk=case_id)
    except Case.DoesNotExist:
        return None

    if case.status != 'pending' or not case.predicted_case_type or not case.latitude or not case.longitude:
        return None


    specialization_map = {
        'criminal': 'criminal_law',
        'family': 'family_law',
        'constitutional and human rights': 'constitutional_law',
        'corporate': 'corporate_law',
    }

    field_name = specialization_map.get(case.predicted_case_type)
    if not field_name:
        return None

    lawyers = LawyerProfile.objects.filter(
        verified=True,  
        **{field_name: True}
    )

    if not lawyers.exists():
        return None

    lawyer_distances = []
    for lawyer in lawyers:
        distance = haversine(
            case.latitude, case.longitude,
            lawyer.latitude, lawyer.longitude
        )
        lawyer_distances.append((lawyer, distance))

    lawyer_distances.sort(key=lambda x: x[1])
    best_lawyer, _ = lawyer_distances[0]

    assignment = CaseAssignment.objects.create(
        lawyer=best_lawyer,
        case=case,
        is_assigned=True,
        confirmed_by_applicant=False,
        confirmed_by_lawyer=False
    )

    case.status = 'accepted'
    case.save()

    return assignment