"""Unit tests for WordPress Daily Prayer Time next and tomorrow sensors."""
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import pytest

from custom_components.wordpress_daily_prayer_time.const import PRAYER_TIME_KEYS
from custom_components.wordpress_daily_prayer_time.coordinator import PrayerTimeCoordinator
from custom_components.wordpress_daily_prayer_time.sensor import (
    SENSOR_TYPES,
    PrayerTimeSensor,
)

SAMPLE_API_RESPONSE = [
    {
        "d_date": "2026-10-02",
        "fajr_begins": "05:46:00",
        "fajr_jamah": "06:06:00",
        "sunrise": "07:24:00",
        "zuhr_begins": "13:17:00",
        "zuhr_jamah": "13:37:00",
        "asr_mithl_1": "16:20:00",
        "asr_mithl_2": "16:20:00",
        "asr_jamah": "16:35:00",
        "maghrib_begins": "19:06:00",
        "maghrib_jamah": "19:16:00",
        "isha_begins": "20:38:00",
        "isha_jamah": "20:48:00",
        "is_ramadan": "0",
        "hijri_date": "21 Rabi' al-Thani 1448",
        "jamah_changes": {
            "fajr_jamah": "06:07:00",
            "maghrib_jamah": "19:13:00",
            "isha_jamah": "20:45:00",
        },
        "tomorrow": {
            "d_date": "2026-10-03",
            "fajr_begins": "05:47:00",
            "fajr_jamah": "06:07:00",
            "sunrise": "07:25:00",
            "zuhr_begins": "13:16:00",
            "zuhr_jamah": "13:36:00",
            "asr_mithl_1": "16:18:00",
            "asr_mithl_2": "16:18:00",
            "asr_jamah": "16:33:00",
            "maghrib_begins": "19:03:00",
            "maghrib_jamah": "19:13:00",
            "isha_begins": "20:35:00",
            "isha_jamah": "20:45:00",
            "is_ramadan": "0",
            "hijri_date": "22 Rabi' al-Thani 1448",
        },
        "hijri_date_convert": "21 Rabi' al-Thani 1448",
        "jumuah": [
            "13:30",
            "14:30",
        ],
        "jumuah_label": [
            "Men Only",
            "Men & Women",
        ],
        "next_prayer": {
            "prayerName": "fajr",
            "timeLeft": 345,
        },
    }
]


def create_mock_coordinator(data: dict, jamaha_duration=10, jummah_duration=25):
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.jamaha_duration = jamaha_duration
    coordinator.jummah_duration = jummah_duration
    coordinator.website_name = "example.com"
    coordinator.config_entry.entry_id = "test_entry"
    return coordinator


def get_sensor(coordinator, key: str):
    desc = next((d for d in SENSOR_TYPES if d.key == key), None)
    if not desc:
        from homeassistant.components.sensor import SensorEntityDescription
        desc = SensorEntityDescription(key=key, name=key)
    sensor = PrayerTimeSensor(coordinator, desc)
    return sensor


class TestPrayerTimes:
    def test_process_data_parses_today_and_tomorrow(self):
        """Test coordinator _process_data extracts today's and tomorrow's prayer times."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.options = {"endpoint": "https://example.com"}
        coordinator = PrayerTimeCoordinator(hass, config_entry, "https://example.com")

        # Mock current date to match 2026-10-02 (Friday)
        fixed_now = datetime(2026, 10, 2, 10, 0, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=fixed_now):
            parsed = coordinator._process_data(SAMPLE_API_RESPONSE)

        # Verify today's sensors
        assert "fajr_begins" in parsed
        assert parsed["fajr_begins_time"] == "05:46"
        assert parsed["zuhr_begins_time"] == "13:17"
        assert parsed["asr_mithl_1_time"] == "16:20"
        assert parsed["maghrib_begins_time"] == "19:06"
        assert parsed["isha_begins_time"] == "20:38"
        assert parsed["hijri_date"] == "21 Rabi' al-Thani 1448"

        # Verify tomorrow's sensors
        assert "tomorrow_fajr_begins" in parsed
        assert parsed["tomorrow_fajr_begins_time"] == "05:47"
        assert parsed["tomorrow_zuhr_begins_time"] == "13:16"
        assert parsed["tomorrow_asr_mithl_1_time"] == "16:18"
        assert parsed["tomorrow_maghrib_begins_time"] == "19:03"
        assert parsed["tomorrow_isha_begins_time"] == "20:35"
        assert parsed["tomorrow_asr_begins_time"] == "16:18"

        # Verify Jumuah parsed from day_data
        assert "jumuah_1" in parsed
        assert parsed["jumuah_1_label"] == "Men Only"
        assert "jumuah_2" in parsed
        assert parsed["jumuah_2_label"] == "Men & Women"

    def test_sensor_types_definitions(self):
        """Verify tomorrow azan sensors are in SENSOR_TYPES with matching naming."""
        keys = [desc.key for desc in SENSOR_TYPES]
        expected_keys = [
            "tomorrow_fajr_begins",
            "tomorrow_fajr_begins_time",
            "tomorrow_zuhr_begins",
            "tomorrow_zuhr_begins_time",
            "tomorrow_asr_mithl_1",
            "tomorrow_asr_mithl_1_time",
            "tomorrow_maghrib_begins",
            "tomorrow_maghrib_begins_time",
            "tomorrow_isha_begins",
            "tomorrow_isha_begins_time",
        ]
        for key in expected_keys:
            assert key in keys
            assert key in PRAYER_TIME_KEYS

    def test_tomorrow_sensors_native_value(self):
        """Verify tomorrow sensors return tomorrow values directly without rollover."""
        data = {
            "tomorrow_fajr_begins": datetime(2026, 10, 3, 5, 47, tzinfo=timezone.utc),
            "tomorrow_fajr_begins_time": "05:47",
            "tomorrow_zuhr_begins_time": "13:16",
            "tomorrow_asr_mithl_1_time": "16:18",
            "tomorrow_maghrib_begins_time": "19:03",
            "tomorrow_isha_begins_time": "20:35",
            "isha_jamah": datetime(2026, 10, 2, 20, 48, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # After Isha
        with patch("homeassistant.util.dt.now", return_value=datetime(2026, 10, 2, 21, 0, tzinfo=timezone.utc)):
            sensor_fajr = get_sensor(coordinator, "tomorrow_fajr_begins")
            assert sensor_fajr.native_value == datetime(2026, 10, 3, 5, 47, tzinfo=timezone.utc)

            sensor_fajr_time = get_sensor(coordinator, "tomorrow_fajr_begins_time")
            assert sensor_fajr_time.native_value == "05:47"

    def test_next_sensors_during_day_thursday(self):
        """Test Next sensor on Thursday daytime shows Thursday prayers, not Jummah."""
        # 2026-10-01 was a Thursday
        data = {
            "fajr_begins": datetime(2026, 10, 1, 5, 45, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 1, 7, 23, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 10, 1, 13, 17, tzinfo=timezone.utc),
            "zuhr_jamah": datetime(2026, 10, 1, 13, 37, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 1, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 1, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 1, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 1, 20, 48, tzinfo=timezone.utc),
            "tomorrow_fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "tomorrow_sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Thursday 10:00 AM (before Dhuhr)
        thursday_10am = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=thursday_10am):
            next_sensor = get_sensor(coordinator, "next_event_name")
            assert next_sensor.native_value == "Dhuhr"

            next_time = get_sensor(coordinator, "next_event_time")
            assert next_time.native_value == "13:17"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Zuhr: 13:17"

            curr_compact = get_sensor(coordinator, "current_prayer_compact")
            assert curr_compact.native_value == "Sunr: 07:23"

    def test_next_sensors_after_isha_not_unknown(self):
        """Fix bug: after Isha sensors should NOT show unknown/None, but tomorrow's Fajr."""
        data = {
            "fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 10, 2, 13, 17, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 2, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 2, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 2, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 2, 20, 48, tzinfo=timezone.utc),
            "tomorrow_fajr_begins": datetime(2026, 10, 3, 5, 47, tzinfo=timezone.utc),
            "tomorrow_sunrise": datetime(2026, 10, 3, 7, 25, tzinfo=timezone.utc),
            "tomorrow_zuhr_begins": datetime(2026, 10, 3, 13, 16, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Friday 21:00 (after Isha Jamah 20:48)
        friday_2100 = datetime(2026, 10, 2, 21, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=friday_2100):
            next_sensor = get_sensor(coordinator, "next_event_name")
            assert next_sensor.native_value == "Fajr"

            next_dt_sensor = get_sensor(coordinator, "next_event_datetime")
            assert next_dt_sensor.native_value == datetime(2026, 10, 3, 5, 47, tzinfo=timezone.utc)

            next_time_sensor = get_sensor(coordinator, "next_event_time")
            assert next_time_sensor.native_value == "05:47"

            next_in_sensor = get_sensor(coordinator, "next_event_in")
            assert next_in_sensor.native_value == "In 8 hours"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Fajr: 05:47"

            curr_compact = get_sensor(coordinator, "current_prayer_compact")
            assert curr_compact.native_value == "Isha: 20:38"

            # Check dynamic icons
            next_icon = get_sensor(coordinator, "next_prayer_compact")
            assert next_icon.icon == "mdi:theme-light-dark"

    def test_thursday_after_isha_does_not_show_jummah(self):
        """Fix bug: On Thursday after Isha, Next must show Friday Fajr, NOT Jummah 1."""
        # 2026-10-01 was Thursday
        data = {
            "fajr_begins": datetime(2026, 10, 1, 5, 45, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 1, 7, 23, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 10, 1, 13, 17, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 1, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 1, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 1, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 1, 20, 48, tzinfo=timezone.utc),
            "tomorrow_fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "tomorrow_sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
            "jumuah_2": datetime(2026, 10, 2, 14, 30, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Thursday 21:00 (after Isha)
        thursday_2100 = datetime(2026, 10, 1, 21, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=thursday_2100):
            next_sensor = get_sensor(coordinator, "next_event_name")
            assert next_sensor.native_value == "Fajr"
            assert next_sensor.native_value != "Jumuah 1"

            next_time = get_sensor(coordinator, "next_event_time")
            assert next_time.native_value == "05:46"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Fajr: 05:46"

    def test_friday_schedule_transitions_to_jumuah(self):
        """Test on Friday after Sunrise, Next event is Jumuah 1, not Dhuhr."""
        # 2026-10-02 is Friday
        data = {
            "fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "fajr_jamah": datetime(2026, 10, 2, 6, 6, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 10, 2, 13, 17, tzinfo=timezone.utc),
            "zuhr_jamah": datetime(2026, 10, 2, 13, 37, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
            "jumuah_2": datetime(2026, 10, 2, 14, 30, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 2, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 2, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 2, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 2, 20, 48, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Friday 08:00 AM (after sunrise)
        friday_0800 = datetime(2026, 10, 2, 8, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=friday_0800):
            next_sensor = get_sensor(coordinator, "next_event_name")
            assert next_sensor.native_value == "Jumuah 1"

            next_time = get_sensor(coordinator, "next_event_time")
            assert next_time.native_value == "13:30"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Jumh: 13:30"

            next_icon = get_sensor(coordinator, "next_event_name")
            assert next_icon.icon == "mdi:mosque"

    def test_active_quiet_period(self):
        """Test during Jamah / Khutba quiet period active event overrides are applied."""
        data = {
            "fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "fajr_jamah": datetime(2026, 10, 2, 6, 6, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data, jamaha_duration=10, jummah_duration=25)

        # During Fajr Jamah (06:08)
        fajr_active = datetime(2026, 10, 2, 6, 8, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=fajr_active):
            next_name = get_sensor(coordinator, "next_event_name")
            assert next_name.native_value == "Fajr Jamaha"

            next_in = get_sensor(coordinator, "next_event_in")
            assert next_in.native_value == "Keep quiet, please!"

        # During Jumuah Khutba (13:40)
        jumuah_active = datetime(2026, 10, 2, 13, 40, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=jumuah_active):
            next_name = get_sensor(coordinator, "next_event_name")
            assert next_name.native_value == "Jummah Khutba 1"

            next_in = get_sensor(coordinator, "next_event_in")
            assert next_in.native_value == "Keep quiet, please!"

    def test_friday_early_morning_before_refresh_shows_fajr(self):
        """Test on Friday at 00:05 AM before coordinator refresh, Next is Friday Fajr, NOT Jumuah 1."""
        # Coordinator data has Thursday as primary and Friday as tomorrow
        data = {
            "fajr_begins": datetime(2026, 10, 1, 5, 45, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 10, 1, 7, 23, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 10, 1, 13, 17, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 1, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 1, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 1, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 1, 20, 48, tzinfo=timezone.utc),
            # Tomorrow keys represent Friday (today at 00:05 AM)
            "tomorrow_fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "tomorrow_sunrise": datetime(2026, 10, 2, 7, 24, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Friday 00:05 AM
        friday_0005 = datetime(2026, 10, 2, 0, 5, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=friday_0005):
            next_name = get_sensor(coordinator, "next_event_name")
            assert next_name.native_value == "Fajr"
            assert next_name.native_value != "Jumuah 1"

            next_time = get_sensor(coordinator, "next_event_time")
            assert next_time.native_value == "05:46"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Fajr: 05:46"

    def test_friday_after_isha_tomorrow_is_saturday(self):
        """Test on Friday after Isha, tomorrow is Saturday, so Zuhr is used, not Jumuah."""
        data = {
            "fajr_begins": datetime(2026, 10, 2, 5, 46, tzinfo=timezone.utc),
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
            "asr_mithl_1": datetime(2026, 10, 2, 16, 20, tzinfo=timezone.utc),
            "maghrib_begins": datetime(2026, 10, 2, 19, 6, tzinfo=timezone.utc),
            "isha_begins": datetime(2026, 10, 2, 20, 38, tzinfo=timezone.utc),
            "isha_jamah": datetime(2026, 10, 2, 20, 48, tzinfo=timezone.utc),
            # Tomorrow is Saturday
            "tomorrow_fajr_begins": datetime(2026, 10, 3, 5, 47, tzinfo=timezone.utc),
            "tomorrow_sunrise": datetime(2026, 10, 3, 7, 25, tzinfo=timezone.utc),
            "tomorrow_zuhr_begins": datetime(2026, 10, 3, 13, 16, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Friday 21:30 (after Isha)
        friday_2130 = datetime(2026, 10, 2, 21, 30, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=friday_2130):
            next_name = get_sensor(coordinator, "next_event_name")
            assert next_name.native_value == "Fajr"

            next_compact = get_sensor(coordinator, "next_prayer_compact")
            assert next_compact.native_value == "Fajr: 05:47"

    def test_wednesday_does_not_include_friday_jumuah(self):
        """Test on Wednesday, upcoming events only consider today & tomorrow (not Friday's Jumuah)."""
        # 2026-09-30 was Wednesday
        data = {
            "fajr_begins": datetime(2026, 9, 30, 5, 44, tzinfo=timezone.utc),
            "sunrise": datetime(2026, 9, 30, 7, 22, tzinfo=timezone.utc),
            "zuhr_begins": datetime(2026, 9, 30, 13, 17, tzinfo=timezone.utc),
            "tomorrow_fajr_begins": datetime(2026, 10, 1, 5, 45, tzinfo=timezone.utc),
            "tomorrow_zuhr_begins": datetime(2026, 10, 1, 13, 17, tzinfo=timezone.utc),
            # Jumuah is for Friday 2026-10-02 (2 days away)
            "jumuah_1": datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc),
        }
        coordinator = create_mock_coordinator(data)

        # Wednesday 10:00 AM
        wednesday_10am = datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=wednesday_10am):
            events, _, _ = get_sensor(coordinator, "next_event_name")._get_upcoming_events()
            event_keys = [k for k, _ in events]
            assert "zuhr_begins" in event_keys
            assert "jumuah_1" not in event_keys

    def test_process_data_from_year_schedule_without_nested_tomorrow(self):
        """Test coordinator _process_data extracts tomorrow's times when data is a flat list of days."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.options = {"endpoint": "https://example.com"}
        coordinator = PrayerTimeCoordinator(hass, config_entry, "https://example.com")

        year_data = [
            {
                "d_date": "2026-10-02",
                "fajr_begins": "05:46:00",
                "zuhr_begins": "13:17:00",
                "asr_mithl_1": "16:20:00",
                "maghrib_begins": "19:06:00",
                "isha_begins": "20:38:00",
            },
            {
                "d_date": "2026-10-03",
                "fajr_begins": "05:47:00",
                "zuhr_begins": "13:16:00",
                "asr_mithl_1": "16:18:00",
                "maghrib_begins": "19:03:00",
                "isha_begins": "20:35:00",
            },
        ]

        fixed_now = datetime(2026, 10, 2, 10, 0, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=fixed_now):
            parsed = coordinator._process_data(year_data)

            # Check today's times
            assert parsed["fajr_begins_time"] == "05:46"
            # Check tomorrow's times extracted from the second row
            assert parsed["tomorrow_fajr_begins_time"] == "05:47"
            assert parsed["tomorrow_zuhr_begins_time"] == "13:16"
            assert parsed["tomorrow_asr_begins_time"] == "16:18"
            assert parsed["tomorrow_maghrib_begins_time"] == "19:03"
            assert parsed["tomorrow_isha_begins_time"] == "20:35"

    def test_tomorrow_asr_alias_fallback_in_sensor(self):
        """Test tomorrow_asr_begins and tomorrow_asr_mithl_1 fallback gracefully."""
        data = {
            "tomorrow_asr_mithl_1": datetime(2026, 10, 3, 16, 18, tzinfo=timezone.utc),
            "tomorrow_asr_mithl_1_time": "16:18",
        }
        coordinator = create_mock_coordinator(data)

        sensor_alias = get_sensor(coordinator, "tomorrow_asr_begins")
        sensor_alias_time = get_sensor(coordinator, "tomorrow_asr_begins_time")

        assert sensor_alias.native_value == datetime(2026, 10, 3, 16, 18, tzinfo=timezone.utc)
        assert sensor_alias_time.native_value == "16:18"

    def test_process_data_nested_list_of_lists_year_schedule(self):
        """Test coordinator _process_data handles [[ {...}, {...} ]] format from legacy year endpoint."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.options = {"endpoint": "https://example.com"}
        coordinator = PrayerTimeCoordinator(hass, config_entry, "https://example.com")

        # Nested list of lists as returned by the year endpoint
        nested_year_data = [
            [
                {
                    "d_date": "2026-10-02",
                    "fajr_begins": "05:46:00",
                    "zuhr_begins": "13:17:00",
                    "asr_mithl_1": "16:20:00",
                    "maghrib_begins": "19:06:00",
                    "isha_begins": "20:38:00",
                },
                {
                    "d_date": "2026-10-03",
                    "fajr_begins": "05:47:00",
                    "zuhr_begins": "13:16:00",
                    "asr_mithl_1": "16:18:00",
                    "maghrib_begins": "19:03:00",
                    "isha_begins": "20:35:00",
                },
            ]
        ]

        fixed_now = datetime(2026, 10, 2, 10, 0, 0, tzinfo=timezone.utc)
        with patch("homeassistant.util.dt.now", return_value=fixed_now):
            parsed = coordinator._process_data(nested_year_data)

            # Check today's times
            assert parsed["fajr_begins_time"] == "05:46"
            # Check tomorrow's times extracted from preferred year schedule
            assert parsed["tomorrow_fajr_begins_time"] == "05:47"
            assert parsed["tomorrow_zuhr_begins_time"] == "13:16"
            assert parsed["tomorrow_asr_begins_time"] == "16:18"
            assert parsed["tomorrow_maghrib_begins_time"] == "19:03"
            assert parsed["tomorrow_isha_begins_time"] == "20:35"


