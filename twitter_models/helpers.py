import datetime

def last_dow_noon(dow, d):
  hours_ahead = d.hour - 12
  if hours_ahead < 0:
    hours_ahead += 24
  last_noon = d - datetime.timedelta(hours=hours_ahead, minutes=d.minute, seconds=d.second, microseconds=d.microsecond)
  days_ahead = last_noon.weekday() - dow
  if days_ahead < 0:
    days_ahead += 7
  return last_noon - datetime.timedelta(days=days_ahead)
