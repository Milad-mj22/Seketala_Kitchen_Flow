import jdatetime
from datetime import datetime

def jalali_date_time_to_gregorian(jalali_date, time_str):
    """
    jalali_date: '1404-10-12'
    time_str: '14:32:10'
    """
    jy, jm, jd = map(int, jalali_date.split("-"))
    hour, minute = map(int, time_str.split(":"))

    j_date = jdatetime.date(jy, jm, jd)
    g_date = j_date.togregorian()

    return datetime(
        g_date.year,
        g_date.month,
        g_date.day,
        hour,
        minute,
       
    )
