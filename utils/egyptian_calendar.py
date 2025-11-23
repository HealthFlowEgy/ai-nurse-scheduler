"""
Egyptian calendar utilities including Ramadan dates and public holidays.
"""

from datetime import datetime, timedelta
from hijri_converter import Hijri, Gregorian
from typing import List, Tuple


def get_ramadan_dates(gregorian_year: int) -> Tuple[datetime, datetime]:
    """
    Get Ramadan start and end dates for a given Gregorian year.
    
    Args:
        gregorian_year: Gregorian calendar year
    
    Returns:
        Tuple of (ramadan_start, ramadan_end) as datetime objects
    """
    # Ramadan is the 9th month of Islamic calendar
    # Approximate calculation - in production, use API or database
    
    # Ramadan 2025: approximately April 1 - April 30
    # Ramadan 2026: approximately March 22 - April 20
    
    ramadan_estimates = {
        2024: (datetime(2024, 3, 11), datetime(2024, 4, 9)),
        2025: (datetime(2025, 3, 1), datetime(2025, 3, 30)),
        2026: (datetime(2026, 2, 18), datetime(2026, 3, 19)),
        2027: (datetime(2027, 2, 8), datetime(2027, 3, 9)),
        2028: (datetime(2028, 1, 28), datetime(2028, 2, 26)),
    }
    
    return ramadan_estimates.get(gregorian_year, (None, None))


def is_ramadan(date: datetime) -> bool:
    """Check if a date falls during Ramadan"""
    ramadan_start, ramadan_end = get_ramadan_dates(date.year)
    
    if ramadan_start and ramadan_end:
        return ramadan_start <= date <= ramadan_end
    
    return False


def get_egyptian_public_holidays(year: int) -> List[datetime]:
    """
    Get Egyptian public holidays for a given year.
    
    Returns:
        List of datetime objects for public holidays
    """
    holidays = [
        # Fixed holidays
        datetime(year, 1, 7),   # Coptic Christmas
        datetime(year, 1, 25),  # January 25 Revolution
        datetime(year, 4, 25),  # Sinai Liberation Day
        datetime(year, 5, 1),   # Labor Day
        datetime(year, 6, 30),  # June 30 Revolution
        datetime(year, 7, 23),  # Revolution Day
        datetime(year, 10, 6),  # Armed Forces Day
    ]
    
    # Islamic holidays (approximate - vary by lunar calendar)
    # Eid al-Fitr (3 days after Ramadan)
    ramadan_start, ramadan_end = get_ramadan_dates(year)
    if ramadan_end:
        eid_fitr_start = ramadan_end + timedelta(days=1)
        holidays.extend([
            eid_fitr_start,
            eid_fitr_start + timedelta(days=1),
            eid_fitr_start + timedelta(days=2)
        ])
    
    # Eid al-Adha (approximate)
    # About 70 days after Eid al-Fitr
    if ramadan_end:
        eid_adha_start = ramadan_end + timedelta(days=70)
        holidays.extend([
            eid_adha_start,
            eid_adha_start + timedelta(days=1),
            eid_adha_start + timedelta(days=2),
            eid_adha_start + timedelta(days=3)
        ])
    
    # Islamic New Year (approximate)
    # Mawlid an-Nabi (Prophet's Birthday - approximate)
    
    return sorted(holidays)


def is_public_holiday(date: datetime) -> bool:
    """Check if a date is an Egyptian public holiday"""
    holidays = get_egyptian_public_holidays(date.year)
    return date.date() in [h.date() for h in holidays]


def is_friday(date: datetime) -> bool:
    """Check if a date is Friday (main prayer day in Egypt)"""
    return date.weekday() == 4  # Friday


def is_weekend(date: datetime) -> bool:
    """Check if a date is weekend in Egypt (Friday-Saturday)"""
    return date.weekday() in [4, 5]  # Friday and Saturday


def get_prayer_times(date: datetime, city: str = "Cairo") -> dict:
    """
    Get prayer times for a specific date and Egyptian city.
    
    This is a simplified version. In production, use an API like:
    - Aladhan API
    - IslamicFinder API
    - Local calculation library
    
    Args:
        date: Date to get prayer times for
        city: Egyptian city name
    
    Returns:
        Dictionary with prayer times
    """
    # Approximate prayer times for Cairo
    # In production, calculate using proper algorithms or API
    
    prayer_times = {
        "Cairo": {
            "fajr": "04:30",
            "sunrise": "06:00",
            "dhuhr": "12:00",
            "asr": "15:30",
            "maghrib": "18:00",
            "isha": "19:30"
        },
        "Alexandria": {
            "fajr": "04:35",
            "sunrise": "06:05",
            "dhuhr": "12:05",
            "asr": "15:35",
            "maghrib": "18:05",
            "isha": "19:35"
        },
        "Giza": {
            "fajr": "04:30",
            "sunrise": "06:00",
            "dhuhr": "12:00",
            "asr": "15:30",
            "maghrib": "18:00",
            "isha": "19:30"
        }
    }
    
    return prayer_times.get(city, prayer_times["Cairo"])


def get_working_days(start_date: datetime, num_days: int) -> List[datetime]:
    """
    Get working days excluding weekends and holidays.
    
    Args:
        start_date: Start date
        num_days: Number of calendar days
    
    Returns:
        List of working day dates
    """
    working_days = []
    current_date = start_date
    
    for _ in range(num_days):
        if not is_weekend(current_date) and not is_public_holiday(current_date):
            working_days.append(current_date)
        current_date += timedelta(days=1)
    
    return working_days


if __name__ == "__main__":
    # Test functions
    print("Egyptian Calendar Utilities Test")
    print("=" * 50)
    
    # Test Ramadan dates
    year = 2025
    ramadan_start, ramadan_end = get_ramadan_dates(year)
    print(f"\nRamadan {year}:")
    print(f"  Start: {ramadan_start.date()}")
    print(f"  End: {ramadan_end.date()}")
    
    # Test public holidays
    holidays = get_egyptian_public_holidays(year)
    print(f"\nEgyptian Public Holidays {year}:")
    for holiday in holidays:
        print(f"  {holiday.date()}")
    
    # Test prayer times
    prayer_times = get_prayer_times(datetime.now())
    print(f"\nPrayer Times (Cairo):")
    for prayer, time in prayer_times.items():
        print(f"  {prayer.capitalize()}: {time}")
    
    # Test working days
    working_days = get_working_days(datetime.now(), 30)
    print(f"\nWorking days in next 30 days: {len(working_days)}")
