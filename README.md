<div align="center">
  <img src="https://ps.w.org/daily-prayer-time-for-mosques/assets/icon-128x128.png?rev=1215663" width="128" height="128" alt="Logo">
  <h1>WordPress Daily Prayer Time</h1>


  [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
  ![Version](https://img.shields.io/badge/version-2.0.0-orange.svg?style=for-the-badge)
  ![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.3+-blue.svg?style=for-the-badge&logo=home-assistant)
  [![Maintainer](https://img.shields.io/badge/maintainer-%40modestpharaoh-blue.svg?style=for-the-badge)](https://github.com/modestpharaoh)
</div>

---

This is a custom Home Assistant integration that fetches daily prayer times (Athan and Iqamah) from any WordPress site using the [Daily Prayer Time for Mosques](https://wordpress.org/plugins/daily-prayer-time-for-mosques/) plugin.

## ✨ Features

- 🕋 **Complete Prayer Schedule**: Fetches Fajr, Sunrise, Dhuhr, Asr, Maghrib, and Isha (both Athan and Iqamah).
- 📅 **Dual Calendar Support**: Displays current **Hijri Date** directly within Home Assistant.
- 🕌 **Dynamic Jumuah Sensors**: Automatically tracks an arbitrary number of Jumuah times and labels for the upcoming Friday.
- 🕒 **Human-Readable Times**: Provides both timestamp sensors and simple `HH:MM` string sensors for all events.
- ⏱️ **Next Event Tracking**: Real-time sensors for `Next` event name, `Next In` countdown, `Next Datetime`, and `Next Time`.
- 🤫 **Quiet Period Overrides**: Automatically shows "Keep quiet, please!" and `<Prayer> Jamaha` during active Iqamah/Khutba times.
- 🔄 **Smart Refresh & Rollover**: Updates schedules automatically every day shortly after midnight. Sensors automatically rollover to show tomorrow's data after Isha Iqamah.
- 📊 **Compact Sensors**: Combined `Current` and `Next` prayer sensors with dynamic icons for clean dashboards.
- 📂 **Offline Fallback**: Downloads the full year's schedule to your config directory; if your mosque's site is offline, it falls back to the local database.
- ⚙️ **Easy Setup & Configuration**: Full UI-based configuration with native Number entities to adjust Jamaha/Jummah durations.

## 🚀 Installation

### 1. HACS (Recommended)
The easiest way to install and keep it updated.
1. Open **HACS** in Home Assistant.
2. Select **Integrations**.
3. Click the **three dots** in the top right and select **Custom repositories**.
4. Repository: `https://github.com/modestpharaoh/hass-wordpress-daily_prayer_time`
5. Category: **Integration**.
6. Click **Add**, then find **WordPress Daily Prayer Time** and click **Download**.
7. **Restart Home Assistant.**

### 2. Manual Installation
1. Download the [latest release](https://github.com/modestpharaoh/hass-wordpress-daily_prayer_time/releases).
2. Copy the `custom_components/wordpress_daily_prayer_time/` folder to your Home Assistant's `custom_components/` directory.
3. **Restart Home Assistant.**

## 🛠️ Configuration

1. Navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **WordPress Daily Prayer Time**.
4. Fill in the following:
   - **Endpoint URL**: The URL of the मस्जिद/Wordpress site (e.g., `https://masjid-wp.com`).
   - **API Path**: The path to the plugin API (default: `wp-json/dpt/v1/prayertime`).

## 📊 Sensors Created

The integration provides the following sensors:
- **Time Sensors**: `sensor.fajr_prayer` (Timestamp) & `sensor.fajr_begins_time` (HH:MM), etc.
- **Tomorrow Sensors**: `sensor.tomorrow_fajr_prayer` (Timestamp) & `sensor.tomorrow_fajr_time` (HH:MM), etc. for all prayer azan begins
- **Next Event**: `sensor.next`, `sensor.next_in`, `sensor.next_datetime`, `sensor.next_time`
- **Compact**: `sensor.current_prayer_compact`, `sensor.next_prayer_compact`
- **Jumuah**: Dynamic sensors like `sensor.jumuah_1`, `sensor.jumuah_1_label`, etc.
- **Calendar**: `sensor.hijri_date`

## 💬 Troubleshooting

- **URL format**: Ensure you use `http://` or `https://` in the endpoint.
- **API Accessibility**: Verify that your site has the plugin installed and public API enabled.
- **Logs**: Check `Configuration` > `System` > `Logs` if sensors do not appear.

## ⚠️ Disclaimer
This component is provided "as is". While we strive for accuracy, please allow for mosque-specific schedule variations. We are not responsible for missed prayers.

---
<p align="center">Made with ❤️ for the Ummah</p>