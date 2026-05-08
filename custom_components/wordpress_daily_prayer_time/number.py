"""Number platform for WordPress Daily Prayer Time integration."""
import logging
from homeassistant.components.number import RestoreNumber
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import (
    PrayerTimeCoordinator,
    WordpressPrayerTimeConfigEntry,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: WordpressPrayerTimeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = config_entry.runtime_data
    
    entities = [
        PrayerTimeNumber(
            coordinator,
            "jamaha_duration",
            "Jamaha Duration",
            10.0,
            1.0,
            60.0,
        ),
        PrayerTimeNumber(
            coordinator,
            "jummah_duration",
            "Jummah Duration",
            25.0,
            1.0,
            60.0,
        ),
    ]
    async_add_entities(entities)

class PrayerTimeNumber(RestoreNumber):
    """Representation of a prayer time duration number."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PrayerTimeCoordinator,
        key: str,
        name: str,
        default_value: float,
        min_value: float,
        max_value: float,
    ) -> None:
        """Initialize the number."""
        self.coordinator = coordinator
        self._key = key
        self._attr_name = name
        self._attr_native_value = default_value
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = 1.0
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.website_name,
            entry_type=DeviceEntryType.SERVICE,
        )
        
        # Set initial value in coordinator
        if key == "jamaha_duration":
            coordinator.jamaha_duration = int(default_value)
        elif key == "jummah_duration":
            coordinator.jummah_duration = int(default_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value
        if self._key == "jamaha_duration":
            self.coordinator.jamaha_duration = int(value)
        elif self._key == "jummah_duration":
            self.coordinator.jummah_duration = int(value)
            
        self.async_write_ha_state()
        
        # Trigger update for sensors
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_number_data()) is not None:
            self._attr_native_value = last_data.native_value
            if self._key == "jamaha_duration" and last_data.native_value is not None:
                self.coordinator.jamaha_duration = int(last_data.native_value)
            elif self._key == "jummah_duration" and last_data.native_value is not None:
                self.coordinator.jummah_duration = int(last_data.native_value)
