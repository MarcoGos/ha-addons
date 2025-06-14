# Home Assistant Add-on: ESPHome Proxy

⚠️ This add-on does not contain ESPHome ⚠️

This add-on acts as a proxy to an external running ESPHome instance. 
The sole purpose of this add-on is to add a ESPHome icon to the sidebar of Home Assistant which will open the frontend of an external running ESPHome instance.

## Options

- `server` (required): this should be the local URL on which the ESPHome frontend is running, e.g. `http://192.168.2.43:6052`. Make sure there is no trailing slash!
