from datetime import datetime, timedelta, timezone
import decimal

def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
    
def calc_containing_day_range(timestamp: int, start_hour: int) -> (int, int):
    offset = (start_hour - 9) * 60 * 60  # unix timestamp 0 corresponds to 09:00
    day_seconds = 24 * 60 * 60
    idx = (timestamp - offset) // day_seconds
    start_date = day_seconds * idx + offset
    end_date = start_date + day_seconds
    return (start_date, end_date)