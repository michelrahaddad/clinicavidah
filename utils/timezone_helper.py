"""
Timezone Helper for Sistema Médico VIDAH
Handles all timezone conversions for Brasília (America/Sao_Paulo)
"""
import datetime
import pytz
from typing import Optional

def get_brasilia_timezone():
    """Get Brasília timezone object"""
    return pytz.timezone('America/Sao_Paulo')

def now_brasilia():
    """Get current datetime in Brasília timezone"""
    return datetime.datetime.now(get_brasilia_timezone())

def format_brasilia_datetime(dt: Optional[datetime.datetime] = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime in Brasília timezone"""
    if dt is None:
        dt = now_brasilia()
    elif dt.tzinfo is None:
        # If naive datetime, assume it's UTC and convert
        dt = pytz.UTC.localize(dt).astimezone(get_brasilia_timezone())
    elif dt.tzinfo != get_brasilia_timezone():
        # Convert to Brasília timezone
        dt = dt.astimezone(get_brasilia_timezone())
    
    return dt.strftime(format_str)

def format_brasilia_date(dt: Optional[datetime.datetime] = None) -> str:
    """Format date in Brasília timezone (DD/MM/YYYY)"""
    return format_brasilia_datetime(dt, '%d/%m/%Y')

def format_brasilia_time(dt: Optional[datetime.datetime] = None) -> str:
    """Format time in Brasília timezone (HH:MM)"""
    return format_brasilia_datetime(dt, '%H:%M')

def format_brasilia_full(dt: Optional[datetime.datetime] = None) -> str:
    """Format full datetime in Brasília timezone (DD/MM/YYYY HH:MM:SS)"""
    return format_brasilia_datetime(dt, '%d/%m/%Y %H:%M:%S')

def utc_to_brasilia(utc_dt: datetime.datetime) -> datetime.datetime:
    """Convert UTC datetime to Brasília timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    return utc_dt.astimezone(get_brasilia_timezone())

def brasilia_to_utc(brasilia_dt: datetime.datetime) -> datetime.datetime:
    """Convert Brasília datetime to UTC"""
    if brasilia_dt.tzinfo is None:
        brasilia_dt = get_brasilia_timezone().localize(brasilia_dt)
    return brasilia_dt.astimezone(pytz.UTC)