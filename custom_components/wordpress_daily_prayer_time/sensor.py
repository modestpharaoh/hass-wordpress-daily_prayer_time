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

    def _calculate_next_event(self, key: str) -> Union[datetime, str, None]:
        """Calculate the next prayer/iqamah/sunrise event."""
        now = dt_util.now()
        today_is_friday = now.weekday() == 4
        
        # Get durations from coordinator
        jamaha_duration = self.coordinator.jamaha_duration
        jummah_duration = self.coordinator.jummah_duration
        
        events = []
        active_key = None
        active_dt = None
        
        for k, v in self.coordinator.data.items():
            if not isinstance(v, datetime):
                continue
                
            # Filter based on key and day
            if today_is_friday:
                if k in ["zuhr_begins", "zuhr_jamah"]:
                    continue
            else:
                if k.startswith("jumuah_") and not k.endswith("_label"):
                    continue
                    
            # Skip keys that are not prayer times or sunrise
            if k in [
                "fajr_begins", "fajr_jamah", "sunrise",
                "zuhr_begins", "zuhr_jamah",
                "asr_mithl_1", "asr_jamah",
                "maghrib_begins", "maghrib_jamah",
                "isha_begins", "isha_jamah"
            ] or (k.startswith("jumuah_") and not k.endswith("_label")):
                
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
                    
        # Sort by time
        events.sort(key=lambda x: x[1])
        
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
                    prayer = prayer_map.get(active_key.split("_")[0], active_key.split("_")[0].capitalize())
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
            return mapping.get(next_key, next_key)
            
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
        if self.entity_description.key == "next_prayer_compact":
            return self._get_compact_icon(is_next=True)
        elif self.entity_description.key == "current_prayer_compact":
            return self._get_compact_icon(is_next=False)
        return self.entity_description.icon

    def _get_compact_icon(self, is_next: bool) -> str | None:
        """Get icon for compact sensors."""
        now = dt_util.now()
        main_keys = ["fajr_begins", "sunrise", "zuhr_begins", "asr_mithl_1", "maghrib_begins", "isha_begins"]
        events = []
        for k in main_keys:
            v = self.coordinator.data.get(k)
            if isinstance(v, datetime):
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
                target_key = events[-1][0] # Fallback to Isha
                
        if target_key:
            for desc in SENSOR_TYPES:
                if desc.key == target_key:
                    return desc.icon
                    
        return "mdi:mosque-outline"

    def _calculate_compact_sensor(self, key: str) -> Union[str, None]:
        """Calculate compact sensor value."""
        now = dt_util.now()
        main_keys = ["fajr_begins", "sunrise", "zuhr_begins", "asr_mithl_1", "maghrib_begins", "isha_begins"]
        
        events = []
        for k in main_keys:
            v = self.coordinator.data.get(k)
            if isinstance(v, datetime):
                events.append((k, v))
                
        events.sort(key=lambda x: x[1])
        
        if not events:
            return None
            
        short_names = {
            "fajr_begins": "Fajr",
            "sunrise": "Sunr",
            "zuhr_begins": "Zuhr",
            "asr_mithl_1": "Asr",
            "maghrib_begins": "Mgrb",
            "isha_begins": "Isha"
        }
        
        if key == "next_prayer_compact":
            next_event = None
            for k, v in events:
                if v > now:
                    next_event = (k, v)
                    break
                    
            if not next_event:
                return None
                
            k, v = next_event
            short_name = short_names.get(k, k)
            local_dt = dt_util.as_local(v)
            time_str = local_dt.strftime("%H:%M")
            return f"{short_name}: {time_str}"
            
        elif key == "current_prayer_compact":
            current_event = None
            for k, v in reversed(events):
                if v <= now:
                    current_event = (k, v)
                    break
                    
            if not current_event:
                # Fallback to last event of day
                k, v = events[-1]
                short_name = short_names.get(k, k)
                local_dt = dt_util.as_local(v)
                time_str = local_dt.strftime("%H:%M")
                return f"{short_name}: {time_str}"
                
            k, v = current_event
            short_name = short_names.get(k, k)
            local_dt = dt_util.as_local(v)
            time_str = local_dt.strftime("%H:%M")
            return f"{short_name}: {time_str}"
            
        return None
