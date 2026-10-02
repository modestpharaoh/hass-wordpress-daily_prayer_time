"""Constants for the WordPress Daily Prayer Time integration."""

from typing import Final


DOMAIN: Final = "wordpress_daily_prayer_time"
NAME: Final = "WordPress Daily Prayer Time"

# Sensor keys for prayer times
PRAYER_TIME_KEYS: Final = [
    "fajr_begins",
    "fajr_jamah",
    "sunrise",
    "zuhr_begins",
    "zuhr_jamah",
    "asr_mithl_1",
    "asr_jamah",
    "maghrib_begins",
    "maghrib_jamah",
    "isha_begins",
    "isha_jamah",
    "fajr_begins_time",
    "fajr_jamah_time",
    "sunrise_time",
    "zuhr_begins_time",
    "zuhr_jamah_time",
    "asr_mithl_1_time",
    "asr_jamah_time",
    "maghrib_begins_time",
    "maghrib_jamah_time",
    "isha_begins_time",
    "isha_jamah_time",
    "tomorrow_fajr_begins",
    "tomorrow_zuhr_begins",
    "tomorrow_asr_mithl_1",
    "tomorrow_maghrib_begins",
    "tomorrow_isha_begins",
    "tomorrow_fajr_begins_time",
    "tomorrow_zuhr_begins_time",
    "tomorrow_asr_mithl_1_time",
    "tomorrow_maghrib_begins_time",
    "tomorrow_isha_begins_time",
    "next_event_name",
    "next_event_in",
    "next_event_datetime",
    "next_event_time",
]

CONF_ENDPOINT: Final = "endpoint"
CONF_API_PATH: Final = "api_path"
DEFAULT_API_PATH: Final = "wp-json/dpt/v1/prayertime"

# Additional sensor key for Hijri date
HIJRI_DATE_KEY: Final = "hijri_date"

# Timeout for querying the endpoint
QUERY_TIMEOUT = 10  # seconds
