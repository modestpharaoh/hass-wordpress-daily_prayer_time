"""Sensor platform for WordPress Daily Prayer Time integration."""
import logging
from datetime import datetime, timedelta
from typing import Union
from homeassistant.util import dt as dt_util

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HIJRI_DATE_KEY
from .coordinator import (
    PrayerTimeCoordinator,
    WordpressPrayerTimeConfigEntry,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="fajr_begins",
        name="Fajr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="fajr_jamah",
        name="Fajr Iqamah",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="sunrise",
        name="Sunrise",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-up",
    ),
    SensorEntityDescription(
        key="zuhr_begins",
        name="Dhuhr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="zuhr_jamah",
        name="Dhuhr Iqamah",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="asr_mithl_1",
        name="Asr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="asr_jamah",
        name="Asr Iqamah",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="maghrib_begins",
        name="Maghrib Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="maghrib_jamah",
        name="Maghrib Iqamah",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="isha_begins",
        name="Isha Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key="isha_jamah",
        name="Isha Iqamah",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key="fajr_begins_time",
        name="Fajr Time",
        device_class=None,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="fajr_jamah_time",
        name="Fajr Iqamah Time",
        device_class=None,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="sunrise_time",
        name="Sunrise Time",
        device_class=None,
        icon="mdi:weather-sunset-up",
    ),
    SensorEntityDescription(
        key="zuhr_begins_time",
        name="Dhuhr Time",
        device_class=None,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="zuhr_jamah_time",
        name="Dhuhr Iqamah Time",
        device_class=None,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="asr_mithl_1_time",
        name="Asr Time",
        device_class=None,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="asr_jamah_time",
        name="Asr Iqamah Time",
        device_class=None,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="maghrib_begins_time",
        name="Maghrib Time",
        device_class=None,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="maghrib_jamah_time",
        name="Maghrib Iqamah Time",
        device_class=None,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="isha_begins_time",
        name="Isha Time",
        device_class=None,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key="isha_jamah_time",
        name="Isha Iqamah Time",
        device_class=None,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key="tomorrow_fajr_begins",
        name="Tomorrow Fajr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="tomorrow_fajr_begins_time",
        name="Tomorrow Fajr Time",
        device_class=None,
        icon="mdi:theme-light-dark",
    ),
    SensorEntityDescription(
        key="tomorrow_zuhr_begins",
        name="Tomorrow Dhuhr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="tomorrow_zuhr_begins_time",
        name="Tomorrow Dhuhr Time",
        device_class=None,
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="tomorrow_asr_mithl_1",
        name="Tomorrow Asr Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="tomorrow_asr_mithl_1_time",
        name="Tomorrow Asr Time",
        device_class=None,
        icon="mdi:weather-sunny",
    ),
    SensorEntityDescription(
        key="tomorrow_maghrib_begins",
        name="Tomorrow Maghrib Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="tomorrow_maghrib_begins_time",
        name="Tomorrow Maghrib Time",
        device_class=None,
        icon="mdi:weather-sunset-down",
    ),
    SensorEntityDescription(
        key="tomorrow_isha_begins",
        name="Tomorrow Isha Prayer",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key="tomorrow_isha_begins_time",
        name="Tomorrow Isha Time",
        device_class=None,
        icon="mdi:weather-night",
    ),
    SensorEntityDescription(
        key=HIJRI_DATE_KEY,
        name="Hijri Date",
        device_class=None,
        icon="mdi:calendar",
    ),
    SensorEntityDescription(
        key="next_event_name",
        name="Next",
        device_class=None,
        icon="mdi:mosque-outline",
    ),
    SensorEntityDescription(
        key="next_event_in",
        name="Next In",
        device_class=None,
        icon="mdi:mosque-outline",
    ),
    SensorEntityDescription(
        key="next_event_datetime",
        name="Next Datetime",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:mosque-outline",
    ),
    SensorEntityDescription(
        key="next_event_time",
        name="Next Time",
        device_class=None,
        icon="mdi:mosque-outline",
    ),
    SensorEntityDescription(
        key="next_prayer_compact",
        name="Next Prayer Compact",
        device_class=None,
    ),
    SensorEntityDescription(
        key="current_prayer_compact",
        name="Current Prayer Compact",
        device_class=None,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: WordpressPrayerTimeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    coordinator = config_entry.runtime_data
    _LOGGER.debug("Setting up sensor with coordinator: %s", coordinator)
    
    entities = []
    
    # Add static sensors
    for description in SENSOR_TYPES:
        entities.append(PrayerTimeSensor(coordinator, description))
        
    # Add dynamic Jumuah sensors
    for key in coordinator.data:
        if key.startswith("jumuah_"):
            parts = key.split("_")
            if len(parts) >= 2:
                num = parts[1]
                if key.endswith("_label"):
                    entities.append(
                        PrayerTimeSensor(
                            coordinator,
                            SensorEntityDescription(
                                key=key,
                                name=f"Jumuah {num} Label",
                                device_class=None,
                                icon="mdi:mosque-outline",
                            ),
                        )
                    )
                else:
                    entities.append(
                        PrayerTimeSensor(
                            coordinator,
                            SensorEntityDescription(
                                key=key,
                                name=f"Jumuah {num}",
                                device_class=SensorDeviceClass.TIMESTAMP,
                                icon="mdi:mosque",
                            ),
                        )
                    )
            
    async_add_entities(entities)


class PrayerTimeSensor(
    CoordinatorEntity[PrayerTimeCoordinator], SensorEntity
):
    """Representation of an Islamic prayer time sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PrayerTimeCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the Wordpress Daily Prayer Time sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.website_name,
            entry_type=DeviceEntryType.SERVICE,
        )
        if description.key.startswith("next_event_") or description.key.endswith("_compact"):
            self._attr_should_poll = True
    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        
        if self.entity_description.key.startswith("next_event_") or self.entity_description.key.endswith("_compact"):
            from homeassistant.helpers.event import async_track_time_interval
            self._timer_unsub = async_track_time_interval(
                self.hass,
                self._async_update_state,
                timedelta(minutes=1),
            )
            
    async def _async_update_state(self, now: datetime) -> None:
        """Update state."""
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        if hasattr(self, "_timer_unsub"):
            self._timer_unsub()

    @property
    def native_value(self) -> Union[datetime, str, None]:
        """Return the state of the sensor."""
        key = self.entity_description.key
        
        if key.startswith("next_event_"):
            return self._calculate_next_event(key)
            
        if key.endswith("_compact"):
            return self._calculate_compact_sensor(key)
            
        if key.startswith("tomorrow_"):
            val = self.coordinator.data.get(key)
            if val is None:
                if key == "tomorrow_asr_begins":
                    val = self.coordinator.data.get("tomorrow_asr_mithl_1")
                elif key == "tomorrow_asr_begins_time":
                    val = self.coordinator.data.get("tomorrow_asr_mithl_1_time")
                elif key == "tomorrow_asr_mithl_1":
                    val = self.coordinator.data.get("tomorrow_asr_begins")
                elif key == "tomorrow_asr_mithl_1_time":
                    val = self.coordinator.data.get("tomorrow_asr_begins_time")
            return val
            
        # Standard sensors rollover logic
        now = dt_util.now()
        isha_jamah = self.coordinator.data.get("isha_jamah")
        
        if isha_jamah and isinstance(isha_jamah, datetime):
            if now > isha_jamah:
                # After Isha Iqamah
                # Exception: Isha sensors still show current date until midnight
                if key not in ["isha_begins", "isha_jamah", "isha_begins_time", "isha_jamah_time"] or now.date() > isha_jamah.date():
                    tomorrow_key = f"tomorrow_{key}"
                    if tomorrow_key in self.coordinator.data:
                        return self.coordinator.data.get(tomorrow_key)
                        
        return self.coordinator.data.get(key)

    def _get_upcoming_events(self) -> tuple[list[tuple[str, datetime]], str | None, datetime | None]:
        """Get upcoming events and active event."""
        now = dt_util.now()
        today_date = now.date()
        tomorrow_date = today_date + timedelta(days=1)
        today_is_friday = now.weekday() == 4
        tomorrow_is_friday = (now.weekday() + 1) % 7 == 4
        
        jamaha_duration = self.coordinator.jamaha_duration
        jummah_duration = self.coordinator.jummah_duration
        
        has_jumuah = any(
            k.startswith("jumuah_") and not k.endswith("_label") and isinstance(v, datetime)
            for k, v in self.coordinator.data.items()
        )
        
        events = []
        active_key = None
        active_dt = None
        
        for k, v in self.coordinator.data.items():
            if not isinstance(v, datetime):
                continue
                
            local_v = dt_util.as_local(v)
            v_date = local_v.date()
            
            # Only consider events for today or tomorrow
            if v_date < today_date or v_date > tomorrow_date:
                continue
                
            is_event_for_today = (v_date == today_date)
            is_event_for_tomorrow = (v_date == tomorrow_date)
            
            # Handle Jumuah vs Zuhr:
            if k.startswith("jumuah_") and not k.endswith("_label"):
                # Jumuah can ONLY be valid on a Friday
                if local_v.weekday() != 4:
                    continue
                # If event is on Friday, it is only relevant if today is Friday or tomorrow is Friday
                if not ((today_is_friday and is_event_for_today) or (tomorrow_is_friday and is_event_for_tomorrow)):
                    continue
            elif k in ["zuhr_begins", "zuhr_jamah"]:
                # If today is Friday and Jumuah is present, skip today's Zuhr
                if today_is_friday and has_jumuah:
                    continue
            elif k in ["tomorrow_zuhr_begins", "tomorrow_zuhr_jamah"]:
                # If tomorrow is Friday and Jumuah is present, skip tomorrow's Zuhr
                if tomorrow_is_friday and has_jumuah:
                    continue
                    
            # Skip keys that are not prayer times or sunrise
            valid_today_keys = [
                "fajr_begins", "fajr_jamah", "sunrise",
                "zuhr_begins", "zuhr_jamah",
                "asr_mithl_1", "asr_jamah",
                "maghrib_begins", "maghrib_jamah",
                "isha_begins", "isha_jamah"
            ]
            valid_tomorrow_keys = [
                "tomorrow_fajr_begins", "tomorrow_fajr_jamah", "tomorrow_sunrise",
                "tomorrow_zuhr_begins", "tomorrow_zuhr_jamah",
                "tomorrow_asr_mithl_1", "tomorrow_asr_jamah",
                "tomorrow_maghrib_begins", "tomorrow_maghrib_jamah",
                "tomorrow_isha_begins", "tomorrow_isha_jamah"
            ]
            
            is_valid_event = (
                k in valid_today_keys
                or k in valid_tomorrow_keys
                or (k.startswith("jumuah_") and not k.endswith("_label"))
            )
            
            if not is_valid_event:
                continue
                
            # Check for active event (quiet period)
            duration = None
            if k.endswith("_jamah"):
                duration = timedelta(minutes=jamaha_duration)
            elif k.startswith("jumuah_") and not k.endswith("_label"):
                duration = timedelta(minutes=jummah_duration)
                
            if duration and v <= now < v + duration:
                active_key = k
                active_dt = v
                
            if v > now:
                events.append((k, v))
                
        events.sort(key=lambda x: x[1])
        return events, active_key, active_dt

    def _calculate_next_event(self, key: str) -> Union[datetime, str, None]:
        """Calculate the next prayer/iqamah/sunrise event."""
        events, active_key, active_dt = self._get_upcoming_events()
        now = dt_util.now()
        
        # Handle active event overrides
        if active_key and key in ["next_event_name", "next_event_in"]:
            if key == "next_event_name":
                if active_key.endswith("_jamah"):
                    prayer_map = {
                        "fajr": "Fajr",
                        "zuhr": "Dhuhr",
                        "asr": "Asr",
                        "maghrib": "Maghrib",
                        "isha": "Isha"
                    }
                    clean_k = active_key.removeprefix("tomorrow_")
                    prayer = prayer_map.get(clean_k.split("_")[0], clean_k.split("_")[0].capitalize())
                    return f"{prayer} Jamaha"
                elif active_key.startswith("jumuah_"):
                    parts = active_key.split("_")
                    num = parts[1]
                    return f"Jummah Khutba {num}"
            elif key == "next_event_in":
                return "Keep quiet, please!"
                
        # Fallback to standard logic if no active event or for other keys
        if not events:
            return None
            
        next_key, next_dt = events[0]
        
        if key == "next_event_name":
            mapping = {
                "fajr_begins": "Fajr",
                "fajr_jamah": "Fajr Iqamah",
                "sunrise": "Sunrise",
                "zuhr_begins": "Dhuhr",
                "zuhr_jamah": "Dhuhr Iqamah",
                "asr_mithl_1": "Asr",
                "asr_jamah": "Asr Iqamah",
                "maghrib_begins": "Maghrib",
                "maghrib_jamah": "Maghrib Iqamah",
                "isha_begins": "Isha",
                "isha_jamah": "Isha Iqamah",
            }
            if next_key.startswith("jumuah_"):
                parts = next_key.split("_")
                num = parts[1]
                return f"Jumuah {num}"
            clean_key = next_key.removeprefix("tomorrow_")
            return mapping.get(clean_key, clean_key)
            
        elif key == "next_event_in":
            diff = next_dt - now
            seconds = diff.total_seconds()
            minutes = int(seconds / 60)
            hours = int(seconds / 3600)
            
            if hours >= 2:
                return f"In {hours} hours"
            elif hours == 1:
                return "In 1 hour"
            elif minutes >= 1:
                return f"in {minutes} minutes"
            else:
                return "In less than a minute"
                
        elif key == "next_event_datetime":
            return next_dt
            
        elif key == "next_event_time":
            local_dt = dt_util.as_local(next_dt)
            return local_dt.strftime("%H:%M")
            
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        key = self.entity_description.key
        
        if key == "next_prayer_compact":
            return self._get_compact_icon(is_next=True)
        elif key == "current_prayer_compact":
            return self._get_compact_icon(is_next=False)
            
        if key.startswith("next_event_"):
            return self._get_next_event_icon()
            
        return self.entity_description.icon

    def _get_compact_icon(self, is_next: bool) -> str | None:
        """Get icon for compact sensors."""
        now = dt_util.now()
        today_date = now.date()
        tomorrow_date = today_date + timedelta(days=1)
        today_is_friday = now.weekday() == 4
        tomorrow_is_friday = (now.weekday() + 1) % 7 == 4
        
        has_jumuah = any(
            k.startswith("jumuah_") and not k.endswith("_label") and isinstance(v, datetime)
            for k, v in self.coordinator.data.items()
        )
        
        compact_keys = [
            "fajr_begins", "sunrise", "zuhr_begins", "asr_mithl_1", "maghrib_begins", "isha_begins",
            "tomorrow_fajr_begins", "tomorrow_sunrise", "tomorrow_zuhr_begins",
            "tomorrow_asr_mithl_1", "tomorrow_maghrib_begins", "tomorrow_isha_begins",
            "jumuah_1"
        ]
        
        events = []
        for k in compact_keys:
            v = self.coordinator.data.get(k)
            if not isinstance(v, datetime):
                continue
            local_v = dt_util.as_local(v)
            v_date = local_v.date()
            if v_date < today_date or v_date > tomorrow_date:
                continue
            # Jumuah vs Zuhr rules
            if k == "jumuah_1":
                if local_v.weekday() != 4:
                    continue
                if not ((today_is_friday and v_date == today_date) or (tomorrow_is_friday and v_date == tomorrow_date)):
                    continue
            elif k in ["zuhr_begins", "tomorrow_zuhr_begins"]:
                if v_date.weekday() == 4 and has_jumuah:
                    continue
            events.append((k, v))
                    
        events.sort(key=lambda x: x[1])
        
        if not events:
            return "mdi:mosque-outline"
            
        target_key = None
        if is_next:
            for k, v in events:
                if v > now:
                    target_key = k
                    break
        else:
            for k, v in reversed(events):
                if v <= now:
                    target_key = k
                    break
            if not target_key:
                target_key = "isha_begins"
                
        if target_key:
            if target_key.startswith("jumuah_"):
                return "mdi:mosque"
            clean_key = target_key.removeprefix("tomorrow_")
            for desc in SENSOR_TYPES:
                if desc.key == clean_key:
                    return desc.icon
                    
        return "mdi:mosque-outline"

    def _get_next_event_icon(self) -> str | None:
        """Get icon for next event sensors."""
        events, active_key, _ = self._get_upcoming_events()
        
        target_key = None
        if active_key:
            target_key = active_key
        elif events:
            target_key = events[0][0]
            
        if target_key:
            if target_key.startswith("jumuah_"):
                return "mdi:mosque"
            clean_key = target_key.removeprefix("tomorrow_")
            for desc in SENSOR_TYPES:
                if desc.key == clean_key:
                    return desc.icon
                    
        return "mdi:mosque-outline"


    def _calculate_compact_sensor(self, key: str) -> Union[str, None]:
        """Calculate compact sensor value."""
        now = dt_util.now()
        today_date = now.date()
        tomorrow_date = today_date + timedelta(days=1)
        today_is_friday = now.weekday() == 4
        tomorrow_is_friday = (now.weekday() + 1) % 7 == 4
        
        has_jumuah = any(
            k.startswith("jumuah_") and not k.endswith("_label") and isinstance(v, datetime)
            for k, v in self.coordinator.data.items()
        )
        
        short_names = {
            "fajr_begins": "Fajr",
            "sunrise": "Sunr",
            "zuhr_begins": "Zuhr",
            "asr_mithl_1": "Asr",
            "maghrib_begins": "Mgrb",
            "isha_begins": "Isha",
        }
        
        compact_keys = [
            "fajr_begins", "sunrise", "zuhr_begins", "asr_mithl_1", "maghrib_begins", "isha_begins",
            "tomorrow_fajr_begins", "tomorrow_sunrise", "tomorrow_zuhr_begins",
            "tomorrow_asr_mithl_1", "tomorrow_maghrib_begins", "tomorrow_isha_begins",
            "jumuah_1"
        ]
        
        events = []
        for k in compact_keys:
            v = self.coordinator.data.get(k)
            if not isinstance(v, datetime):
                continue
            local_v = dt_util.as_local(v)
            v_date = local_v.date()
            if v_date < today_date or v_date > tomorrow_date:
                continue
            # Jumuah vs Zuhr rules
            if k == "jumuah_1":
                if local_v.weekday() != 4:
                    continue
                if not ((today_is_friday and v_date == today_date) or (tomorrow_is_friday and v_date == tomorrow_date)):
                    continue
            elif k in ["zuhr_begins", "tomorrow_zuhr_begins"]:
                if v_date.weekday() == 4 and has_jumuah:
                    continue
            events.append((k, v))
                    
        events.sort(key=lambda x: x[1])
        
        if not events:
            return None
            
        def _get_short_name(k: str) -> str:
            if k.startswith("jumuah_"):
                return "Jumh"
            clean_k = k.removeprefix("tomorrow_")
            return short_names.get(clean_k, clean_k[:4].capitalize())
            
        if key == "next_prayer_compact":
            next_event = None
            for k, v in events:
                if v > now:
                    next_event = (k, v)
                    break
                    
            if not next_event:
                return None
                
            k, v = next_event
            name = _get_short_name(k)
            local_dt = dt_util.as_local(v)
            time_str = local_dt.strftime("%H:%M")
            return f"{name}: {time_str}"
            
        elif key == "current_prayer_compact":
            current_event = None
            for k, v in reversed(events):
                if v <= now:
                    current_event = (k, v)
                    break
                    
            if not current_event:
                # Fallback to Isha (previous prayer before Fajr)
                isha = self.coordinator.data.get("isha_begins")
                if isinstance(isha, datetime):
                    local_dt = dt_util.as_local(isha)
                    return f"Isha: {local_dt.strftime('%H:%M')}"
                k, v = events[-1]
                name = _get_short_name(k)
                local_dt = dt_util.as_local(v)
                return f"{name}: {local_dt.strftime('%H:%M')}"
                
            k, v = current_event
            name = _get_short_name(k)
            local_dt = dt_util.as_local(v)
            time_str = local_dt.strftime("%H:%M")
            return f"{name}: {time_str}"
            
        return None
