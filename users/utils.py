from datetime import datetime
import random
def timestamp_conversation():
    unformatted_time = datetime.now()
    formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")
    return formatted_time