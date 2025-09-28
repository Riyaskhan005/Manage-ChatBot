import datetime

def get_utc_now():
    now = datetime.datetime.utcnow()
    utc_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return utc_time_str