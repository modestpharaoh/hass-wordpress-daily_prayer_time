# WordPress Daily Prayer Time Integration

This is a custom Home Assistant integration for fetching and displaying daily prayer times from a WordPress-based website with [Daily Prayer Time - Plugin](https://wordpress.org/plugins/daily-prayer-time-for-mosques/)

## Features

- Fetches daily prayer times from a WordPress - Daily Prayer Time - API.
- Displays prayer times in Home Assistant.
- Supports automation refresh everyday after midnight.
- Support fetching the full year by default and save it to Home Assistant config directory. In case you site wasn't reachable by the time of the update, it will fallback to the saved prayer of the year.

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant.
2. Go to **Integrations**.
3. Click the **three dots** in the top right corner and select **Custom repositories**.
4. Link the repository: `https://github.com/modestpharaoh/hass-wordpress-daily_prayer_time`
5. Select **Integration** as the category and click **Add**.
6. Search for **WordPress Daily Prayer Time** and click **Download**.
7. Restart **Home Assistant**.

### Method 2: Manual

1. Download the latest release or clone this repository.
2. Copy the `custom_components/wordpress_daily_prayer_time` folder into your Home Assistant's `custom_components` directory.
3. Ensure the directory structure is as follows:
   ```
   custom_components/
   └── wordpress_daily_prayer_time/
      ├── __init__.py
      ├── manifest.json
      ├── sensor.py
      └── ...
   ```
4. Restart **Home Assistant**.

## Configuration

1. Open `Device & Services` Dashboard.
2. ADD INTEGRATION: `WordPress Daily Prayer Time`, and fill the following parameters:

   a. `Endpoint URL`: Enter a valid http/https masjid Wordpress site. e.g. `https://masjid-wp.com`

   b. `API Path`: API path to the WordPress plugin, default `wp-json/dpt/v1/prayertime`


## Usage

Once configured, the integration will create sensors for each prayer Athan/Iqamah, as well as Hijri Date, Jumuah 1, and Jumuah 2. You can use these sensors in your automations or display them in your dashboard.

## Troubleshooting

- Ensure the API URL is correct and accessible.
- Check the Home Assistant logs for any errors.

## Disclamation
* There is no guarantee that the component will get the correct one, I always try my best to update, whenever there is a bug show up. 