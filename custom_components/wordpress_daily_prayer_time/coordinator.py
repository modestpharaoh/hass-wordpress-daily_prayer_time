"""Data coordinator for WordPress Daily Prayer Time integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
import logging
import os
import random
from typing import Any, Dict
from urllib.parse import urlparse


import aiohttp
import aiofiles
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .const import CONF_ENDPOINT, CONF_API_PATH, DEFAULT_API_PATH, DOMAIN, QUERY_TIMEOUT

_LOGGER = logging.getLogger(__name__)

type WordpressPrayerTimeConfigEntry = ConfigEntry[PrayerTimeCoordinator]


class PrayerTimeCoordinator(DataUpdateCoordinator):
    """Coordinator to manage prayer time data fetching."""

    config_entry: WordpressPrayerTimeConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: WordpressPrayerTimeConfigEntry,
        endpoint: str,
        api_path: str = DEFAULT_API_PATH,
    ) -> None:
        """Initialize the coordinator."""
        # Remove trailing slashes from the endpoint
        endpoint = endpoint.rstrip("/")
        api_path = api_path.split("?")[0].strip("/")
        base_endpoint = f"{endpoint}/{api_path}"
        self.yearendpoint = f"{base_endpoint}?filter=year"
        self.todayendpoint = f"{base_endpoint}?filter=today"
        self.hass = hass
        self.jamaha_duration = 10
        self.jummah_duration = 25
        # Extract main domain from endpoint
        parsed_url = urlparse(endpoint)
        self.website = parsed_url.netloc.split(":")[0]  # Remove port if present
        
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
        )

    @property
    def endpoint(self) -> str:
        """Return the endpoint."""
        return self.config_entry.options.get(CONF_ENDPOINT)

    @property
    def website_name(self) -> str:
        """Return the website name."""
        return self.website

    async def async_request_update(self, _: datetime) -> None:
        """Request update from coordinator."""
        await self.async_request_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch prayer time data from the endpoint or fallback to saved file."""
        _LOGGER.debug(f"_async_update_data: Fetching prayer time data from endpoint: {self.yearendpoint}")
        session = async_get_clientsession(self.hass)
        timeout = aiohttp.ClientTimeout(total=QUERY_TIMEOUT)
        raw_data: list = []
        prayer_times_info: dict[str, Any] = {}
        try:
            async with session.get(self.yearendpoint, timeout=timeout) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                _LOGGER.debug(f"Fetched prayer time successfully: {response.status}")
                raw_data = await response.json()
                # Save the response to a file
                await self._save_response_to_file(raw_data)
        except Exception as err:
            _LOGGER.warning(f"Failed to fetch data from endpoint: {err}")
            # Attempt to load from saved file
            raw_data = await self._load_from_saved_file()
        try:
            # Process the data to extract today's prayer times
            prayer_times_info = self._process_data(raw_data)
            _LOGGER.debug(f"Processed prayer times info: {prayer_times_info}")
        except Exception as err:
            _LOGGER.error(f"Failed to process data: {err}")
            raise UpdateFailed(f"Failed to process data: {err}") from err
            
        try:
            async with session.get(self.todayendpoint, timeout=timeout) as response:
                if response.status == 200:
                    today_data_raw = await response.json()
                    
                    def _extract(data):
                        if isinstance(data, dict):
                            return data
                        if isinstance(data, list) and len(data) > 0:
                            return _extract(data[0])
                        return {}
                    
                    today_dict = _extract(today_data_raw)
                    if "hijri_date_convert" in today_dict:
                        prayer_times_info["hijri_date"] = today_dict["hijri_date_convert"]
                        
                    if "jumuah" in today_dict and isinstance(today_dict["jumuah"], list):
                        jumuah_list = today_dict["jumuah"]
                        jumuah_labels = today_dict.get("jumuah_label", [])
                        now = datetime.now()
                        days_ahead = (4 - now.weekday()) % 7
                        target_date = now.date() + timedelta(days=days_ahead)
                        
                        for i, jumuah_time in enumerate(jumuah_list):
                            if jumuah_time:
                                parsed_time = dt_util.parse_time(jumuah_time)
                                if parsed_time:
                                    dt = datetime.combine(target_date, parsed_time)
                                    key = f"jumuah_{i+1}"
                                    prayer_times_info[key] = dt_util.as_utc(dt)
                                    
                                    if isinstance(jumuah_labels, list) and len(jumuah_labels) > i:
                                        label_key = f"jumuah_{i+1}_label"
                                        prayer_times_info[label_key] = jumuah_labels[i]
        except Exception as err:
            _LOGGER.warning(f"Failed to fetch today's extra data: {err}")
        
        if len(prayer_times_info) > 0:
            _LOGGER.debug(f"Parsed prayer times info: {prayer_times_info}")
            # prayer_times_info["hijri_date"] = "20 Shawwal 1446"
            _LOGGER.debug(f"Parsed prayer times info: {prayer_times_info}")
            random_time = self._random_time_after_midnight()
            self.async_schedule_future_update(random_time)
            
            return prayer_times_info
        _LOGGER.error(f"No prayer times found for today")
        # schedule the next update in 30 minutes
        update_time = datetime.now() + timedelta(minutes=30)
        _LOGGER.debug(f"Scheduling next update in 30 minutes: {update_time}")
        self.async_schedule_future_update(update_time)
        return prayer_times_info

    async def _save_response_to_file(self, data: list) -> None:
        """_save_response_to_file: Save the JSON response to a file in the config directory."""
        _LOGGER.debug(f"Saving response to file")
        try:
            filename = f"{self.website}-prayer_for_year.json"
            file_path = os.path.join(self.hass.config.config_dir, filename)
            
            # Write JSON to file
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                await f.write(json_str)

            # with open(file_path, "w", encoding="utf-8") as f:
            #     json.dump(data, f, ensure_ascii=False, indent=2)
            _LOGGER.debug(f"Saved prayer time data to {file_path}")
        except Exception as err:
            _LOGGER.error(f"Failed to save prayer time data to file: {err}")

    # async def _load_from_saved_file(self) -> Dict[str, Any]:
    async def _load_from_saved_file(self) -> list:
        """_load_from_saved_file: Load prayer time data from the saved file."""
        _LOGGER.debug(f"Attempting to load saved prayer time data from file")
        try:
            # Extract main domain from endpoint
            parsed_url = urlparse(self.yearendpoint)
            main_domain = parsed_url.netloc.split(":")[0]  # Remove port if present
            filename = f"{main_domain}-prayer_for_year.json"
            file_path = os.path.join(self.hass.config.config_dir, filename)
            
            # Read JSON from file
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data = json.loads(content)
                # with open(file_path, "r", encoding="utf-8") as f:
                #     data = json.load(f)
                _LOGGER.debug(f"Loaded prayer time data from {file_path}")
                return data
            else:
                raise UpdateFailed("No saved prayer time data available")
        except Exception as err:
            raise UpdateFailed(f"Failed to load saved prayer time data: {err}") from err

    def _process_data(self, data: list) -> Dict[str, Any]:
        """Process the prayer time data to extract today's times."""
        _LOGGER.debug(f"_process_data: Processing data to extract today's prayer times")
        today = datetime.now().strftime("%Y-%m-%d")
        _LOGGER.debug(f"Looping through prayer for today: {today}")
        prayer_times_info: dict[str, Any] = {}
        # Check if data is in the expected format
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Invalid data format: Expected a non-empty list")
        # Check if the first element is a list
        if not isinstance(data[0], list):
            raise ValueError("Invalid data format: Expected a list of lists")
        # Check if the first element of the first list is a dictionary
        if not isinstance(data[0][0], dict):
            raise ValueError("Invalid data format: Expected a list of dictionaries")
        for day_data in data[0]:
            if day_data["d_date"] == today:
                _LOGGER.info(f"Parsed Prayer for today: {day_data}")
                
                # Process today's data
                for key, value in day_data.items():
                    if key in ["d_date", "tomorrow", "is_ramadan"]:
                        continue
                    elif key == "hijri_date":
                        prayer_times_info[str(key)] = day_data[key]
                        _LOGGER.debug(f"Parsed Hijri date: {day_data[key]}")
                    elif prayer_time := dt_util.parse_time(str(value)):
                        _LOGGER.debug(f"Parsed prayer time: {key} = {prayer_time}")
                        prayer_datetime = datetime.combine(datetime.now().date(), prayer_time)
                        prayer_datetime_utc = dt_util.as_utc(prayer_datetime)
                        prayer_times_info[str(key)] = prayer_datetime_utc
                        
                        # Add human readable time in HH:MM format
                        prayer_times_info[f"{key}_time"] = str(value)[:5]
                    else:
                        _LOGGER.warning(f"Skipping invalid prayer time: {key} = {day_data[key]}")
                        
                # Process tomorrow's data if available
                if "tomorrow" in day_data and isinstance(day_data["tomorrow"], dict):
                    tomorrow_data = day_data["tomorrow"]
                    _LOGGER.info(f"Parsed Prayer for tomorrow: {tomorrow_data}")
                    tomorrow_dt = datetime.now().date() + timedelta(days=1)
                    
                    for key, value in tomorrow_data.items():
                        if key in ["d_date", "is_ramadan"]:
                            continue
                        elif key == "hijri_date":
                            prayer_times_info[f"tomorrow_{key}"] = value
                        elif prayer_time := dt_util.parse_time(str(value)):
                            prayer_datetime = datetime.combine(tomorrow_dt, prayer_time)
                            prayer_datetime_utc = dt_util.as_utc(prayer_datetime)
                            prayer_times_info[f"tomorrow_{key}"] = prayer_datetime_utc
                            
                            # Add human readable time in HH:MM format
                            prayer_times_info[f"tomorrow_{key}_time"] = str(value)[:5]
                            
        return prayer_times_info

    def _random_time_after_midnight(self) -> datetime:
        """Generate a random datetime between 12:00 AM and 1:00 AM tomorrow."""
        _LOGGER.debug(f"_random_time_after_midnight: Generating random time after midnight")
        tomorrow = datetime.now() + timedelta(days=1)
        midnight = datetime.combine(tomorrow.date(), dt_util.parse_time("00:00:00"))
        one_am = datetime.combine(tomorrow.date(), dt_util.parse_time("01:00:00"))
        _LOGGER.debug(f"Midnight: {midnight}, One AM: {one_am}")
        random_seconds = random.randint(0, 3600)  # Random seconds between 0 and 3600
        random_time = midnight + timedelta(seconds=random_seconds)
        _LOGGER.debug(f"Random time after midnight: {random_time}")
        return random_time

    @callback
    def async_schedule_future_update(self, dt: datetime) -> None:
        """Schedule future update for sensors."""
        _LOGGER.debug(f"Scheduling next update for Islamic prayer times at {dt}")

        self.event_unsub = async_track_point_in_time(
            self.hass, self.async_request_update, dt
        )
