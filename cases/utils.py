
import math

def haversine(lat1, lon1, lat2, lon2):

    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')  

    R = 6371.0  

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(
        delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
def normalize_urgency(ai_urgency: str) -> str:
    mapping = {
        "urgent": "urgent",
        "high": "high",
        "normal": "normal",
        "medium": "medium",
        "low": "low",
    }
    return mapping.get(ai_urgency.lower(), "medium") 