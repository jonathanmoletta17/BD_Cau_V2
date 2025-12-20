from datetime import datetime, time, timedelta, timezone
from typing import Tuple

DEFAULT_TZ = timezone(timedelta(hours=-3))

def _parse_hhmm(value: str) -> Tuple[int, int]:
    if not value:
        return (8, 0)
    try:
        parts = value.split(":")
        return (int(parts[0]), int(parts[1]))
    except Exception:
        return (8, 0)

def _to_tz(dt: datetime, tz: timezone) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)

def get_today_window(now: datetime, start_hhmm: str = "08:00", end_hhmm: str = "18:00", tz: timezone = DEFAULT_TZ) -> Tuple[datetime, datetime]:
    tz_now = _to_tz(now, tz)
    sh, sm = _parse_hhmm(start_hhmm)
    eh, em = _parse_hhmm(end_hhmm)
    start_dt = tz_now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end_dt = tz_now.replace(hour=eh, minute=em, second=0, microsecond=0)
    if end_dt <= start_dt:
        end_dt = start_dt + timedelta(hours=10)
    return (start_dt, end_dt)

def is_in_expediente(now: datetime, start_hhmm: str = "08:00", end_hhmm: str = "18:00", tz: timezone = DEFAULT_TZ) -> bool:
    start_dt, end_dt = get_today_window(now, start_hhmm, end_hhmm, tz)
    tz_now = _to_tz(now, start_dt.tzinfo)  # type: ignore[arg-type]
    return start_dt <= tz_now <= end_dt

def business_minutes_today(start_ts: datetime | None, now: datetime, start_hhmm: str = "08:00", end_hhmm: str = "18:00", tz: timezone = DEFAULT_TZ) -> int:
    start_dt, end_dt = get_today_window(now, start_hhmm, end_hhmm, tz)
    tz_now = _to_tz(now, start_dt.tzinfo)  # type: ignore[arg-type]
    if tz_now < start_dt or tz_now > end_dt:
        return 0
    if not start_ts:
        effective_start = start_dt
    else:
        st = _to_tz(start_ts, start_dt.tzinfo) if start_ts else start_dt  # type: ignore[arg-type]
        effective_start = max(st, start_dt)
    if effective_start >= tz_now:
        return 0
    delta = tz_now - effective_start
    return max(0, int(delta.total_seconds() // 60))
