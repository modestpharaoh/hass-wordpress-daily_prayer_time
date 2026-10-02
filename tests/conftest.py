import os
import sys
from datetime import datetime, time, timezone, timedelta
from typing import Any
from unittest.mock import MagicMock

# Add workspace root to sys.path so custom_components can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create mock homeassistant modules if not installed
if "homeassistant" not in sys.modules:
    class MockDtUtil:
        @staticmethod
        def now():
            return datetime.now(timezone.utc)

        @staticmethod
        def utcnow():
            return datetime.now(timezone.utc)

        @staticmethod
        def as_utc(d: datetime) -> datetime:
            if d.tzinfo is None:
                return d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc)

        @staticmethod
        def as_local(d: datetime) -> datetime:
            if d.tzinfo is None:
                return d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc)

        @staticmethod
        def parse_time(time_str: str) -> time | None:
            parts = str(time_str).split(":")
            if len(parts) >= 2:
                try:
                    h = int(parts[0])
                    m = int(parts[1])
                    s = int(parts[2]) if len(parts) > 2 else 0
                    return time(h, m, s)
                except ValueError:
                    return None
            return None

    class MockSensorDeviceClass:
        TIMESTAMP = "timestamp"

    class MockSensorEntityDescription:
        def __init__(self, key: str, name: str = "", device_class: Any = None, icon: str | None = None):
            self.key = key
            self.name = name
            self.device_class = device_class
            self.icon = icon

    class MockEntity:
        def __init__(self, *args, **kwargs):
            self.hass = MagicMock()

        def async_write_ha_state(self):
            pass

    class MockCoordinatorEntity(MockEntity):
        __class_getitem__ = classmethod(lambda cls, *args: cls)

        def __init__(self, coordinator, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.coordinator = coordinator

    class MockDataUpdateCoordinator:
        __class_getitem__ = classmethod(lambda cls, *args: cls)

        def __init__(self, hass, logger, config_entry=None, name=""):
            self.hass = hass
            self.logger = logger
            self.config_entry = config_entry
            self.name = name
            self.data = {}

        async def async_request_refresh(self):
            pass

    class MockUpdateFailed(Exception):
        pass

    import types
    ha = types.ModuleType("homeassistant")
    ha.__path__ = []

    ha_const = types.ModuleType("homeassistant.const")
    class MockPlatform:
        SENSOR = "sensor"
        NUMBER = "number"
    ha_const.Platform = MockPlatform
    ha.const = ha_const

    ha_util = types.ModuleType("homeassistant.util")
    ha_util.__path__ = []
    ha_util.dt = MockDtUtil
    ha.util = ha_util

    ha_components = types.ModuleType("homeassistant.components")
    ha_components.__path__ = []
    ha_sensor = types.ModuleType("homeassistant.components.sensor")
    ha_sensor.SensorDeviceClass = MockSensorDeviceClass
    ha_sensor.SensorEntity = MockEntity
    ha_sensor.SensorEntityDescription = MockSensorEntityDescription
    ha_components.sensor = ha_sensor
    ha.components = ha_components

    ha_core = types.ModuleType("homeassistant.core")
    ha_core.HomeAssistant = MagicMock
    ha_core.callback = lambda f: f
    ha.core = ha_core

    ha_helpers = types.ModuleType("homeassistant.helpers")
    ha_helpers.__path__ = []
    ha_helpers_dr = types.ModuleType("homeassistant.helpers.device_registry")
    ha_helpers_dr.DeviceEntryType = MagicMock()
    ha_helpers_dr.DeviceInfo = MagicMock
    ha_helpers_ep = types.ModuleType("homeassistant.helpers.entity_platform")
    ha_helpers_ep.AddConfigEntryEntitiesCallback = MagicMock
    ha_helpers_uc = types.ModuleType("homeassistant.helpers.update_coordinator")
    ha_helpers_uc.CoordinatorEntity = MockCoordinatorEntity
    ha_helpers_uc.DataUpdateCoordinator = MockDataUpdateCoordinator
    ha_helpers_uc.UpdateFailed = MockUpdateFailed
    ha_helpers_event = types.ModuleType("homeassistant.helpers.event")
    ha_helpers_event.async_track_point_in_time = MagicMock()
    ha_helpers_event.async_track_time_interval = MagicMock()
    ha_helpers_aiohttp = types.ModuleType("homeassistant.helpers.aiohttp_client")
    ha_helpers_aiohttp.async_get_clientsession = MagicMock()
    ha_helpers_er = types.ModuleType("homeassistant.helpers.entity_registry")

    ha_helpers.device_registry = ha_helpers_dr
    ha_helpers.entity_platform = ha_helpers_ep
    ha_helpers.update_coordinator = ha_helpers_uc
    ha_helpers.event = ha_helpers_event
    ha_helpers.aiohttp_client = ha_helpers_aiohttp
    ha_helpers.entity_registry = ha_helpers_er
    ha.helpers = ha_helpers

    ha_ce = types.ModuleType("homeassistant.config_entries")
    class MockConfigEntry:
        __class_getitem__ = classmethod(lambda cls, *args: cls)
    ha_ce.ConfigEntry = MockConfigEntry
    ha.config_entries = ha_ce

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.const"] = ha_const
    sys.modules["homeassistant.util"] = ha_util
    sys.modules["homeassistant.util.dt"] = MockDtUtil
    sys.modules["homeassistant.components"] = ha_components
    sys.modules["homeassistant.components.sensor"] = ha_sensor
    sys.modules["homeassistant.core"] = ha_core
    sys.modules["homeassistant.helpers"] = ha_helpers
    sys.modules["homeassistant.helpers.device_registry"] = ha_helpers_dr
    sys.modules["homeassistant.helpers.entity_platform"] = ha_helpers_ep
    sys.modules["homeassistant.helpers.update_coordinator"] = ha_helpers_uc
    sys.modules["homeassistant.helpers.event"] = ha_helpers_event
    sys.modules["homeassistant.helpers.aiohttp_client"] = ha_helpers_aiohttp
    sys.modules["homeassistant.helpers.entity_registry"] = ha_helpers_er
    sys.modules["homeassistant.config_entries"] = ha_ce

if "aiohttp" not in sys.modules:
    sys.modules["aiohttp"] = MagicMock()
if "aiofiles" not in sys.modules:
    sys.modules["aiofiles"] = MagicMock()
