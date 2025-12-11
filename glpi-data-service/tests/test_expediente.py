from datetime import datetime, timezone, timedelta
from src.modules.sis.carregadores.expediente import business_minutes_today, is_in_expediente

TZ = timezone(timedelta(hours=-3))

def dt(h, m, s=0):
    now = datetime.now(TZ)
    return now.replace(hour=h, minute=m, second=s, microsecond=0)

def test_business_minutes_inside_window():
    start = dt(8, 0)
    now = dt(9, 30)
    assert business_minutes_today(start, now, "08:00", "18:00", TZ) == 90

def test_business_minutes_before_window_returns_zero():
    start = dt(7, 0)
    now = dt(7, 30)
    assert business_minutes_today(start, now, "08:00", "18:00", TZ) == 0

def test_business_minutes_after_window_returns_zero():
    start = dt(17, 50)
    now = dt(18, 10)
    assert business_minutes_today(start, now, "08:00", "18:00", TZ) == 0

def test_is_in_expediente():
    assert is_in_expediente(dt(10, 0), "08:00", "18:00", TZ) is True
    assert is_in_expediente(dt(7, 59), "08:00", "18:00", TZ) is False
    assert is_in_expediente(dt(18, 1), "08:00", "18:00", TZ) is False

