import time
import datetime
from datetime import timezone, timedelta

jst_delta = timedelta(hours=9)
jst = timezone(jst_delta, 'JST')
now = None

def local_timestamp():
    return int(time.time() * 1000)

def timestamp(dt=None):
    global now
    if now:
        return now
    elif dt:
        return int(dt.timestamp() * 1000)
    else:
        return local_timestamp()

def utc_timestamp():
    return timestamp(dt=datetime.datetime.now(timezone.utc))

def to_utc_timestamp(jst_ts):
    return timestamp(to_datetime(jst_ts).astimezone(timezone.utc) - jst_delta)

def to_jst_timestamp(utc_ts):
    return timestamp(to_datetime(utc_ts).astimezone(jst) + jst_delta)


def set_time(t):
    global now
    now = t


def to_datetime(ts):
    return datetime.datetime.fromtimestamp(ts / 1000, tz=jst)

def to_timestamp(date):
    if type(date) is str:
        try:
            d = datetime.datetime.strptime(date + ' +0000', '%Y/%m/%d %H:%M:%S.%f %z')
        except:
            try:
                d = datetime.datetime.strptime(date + ' +0000', '%Y-%m-%d %H:%M:%S.%f %z')
            except:
                try:
                    d = datetime.datetime.strptime(date + ' +0000', '%Y-%m-%dT%H:%M:%S.%f %z')
                except:
                    try:
                        d = datetime.datetime.strptime(date + ' +0000', '%Y-%m-%dT%H:%M:%S %z')
                    except:
                        try:
                            d = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                        except:
                            try:
                                d = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                            except:
                                d = datetime.datetime.strptime(date, '%Y-%m-%d-%H:%M:%S')

        return to_timestamp(d)
    else:
        return int(time.mktime(date.timetuple()) * 1000)
  
def to_string(ts, hms=True, year=True, ns=False):
    tem = '%m/%d'
    if year:
        tem = '%Y/' + tem
    if hms:
        tem += ' %H:%M:%S'
    if ns:
        tem += ' .%f'

    return to_datetime(ts).strftime(tem)

def now_string():
    return to_string(timestamp())

def from_seconds(seconds):
    return 1000 * seconds

def to_seconds(ms):
    return ms / 1000

def from_minutes(minutes):
    return from_seconds(1) * 60 * minutes

def to_minutes(ms):
    return to_seconds(ms) / 60

def from_hours(hours):
    return from_minutes(1) * 60 * hours

def to_hours(ms):
    return to_minutes(ms) / 60

def from_days(days):
    return from_hours(1) * 24 * days

def to_days(ms):
    return to_hours(ms) / 24

def from_months(months):
    return to_days(1) * 30 * months

def to_months(ms):
    return to_days(ms) / 30

def from_years(years):
    return from_days(1) * 365 * years

def to_years(ms):
    return to_days(ms) / 365
