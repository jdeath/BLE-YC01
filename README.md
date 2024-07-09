# BLE-YC01
Home Assistant BLE Integration for BLE-YC01 Pool Monitor

[![Stargazers repo roster for @jdeath/BLE-YC01](https://git-lister.onrender.com/api/stars/jdeath/BLE-YC01?limit=30)](https://github.com/jdeath/BLE-YC01/stargazers)

Please ask support questions in homeassistant forums: https://community.home-assistant.io/t/pool-monitor-device-yieryi-ble-yc01

I no longer have this device (it died!). I will accept PRs but will not actively develop anymore.

I just made a native integration. This supports built-in bluetooth adapters and ESPHome configured as Bluetooth Proxies. Much more effecient than running/decoding directly in ESPHome.

I did not figure out any of the decoding myself. This leverages all the great work by: @anasm2010, 
@RubenKona, and many others in the above homeassistant thread. 

Please post a PR if can add any capability.

## Installation
Install this repo in HACS, then add the BLE_YC01 integration. Restart Home Assistant. The device should be found automatically in a few minutes.

## Configuration
The default update interval can be set in: custom_components/BLE_YC01/const.py
Currently set to 1800 seconds (30 minutes). Change the value and restart homeassistant if want more or less often.


[![Star History Chart](https://api.star-history.com/svg?repos=jdeath/BLE-YC01&type=Date)](https://star-history.com/#jdeath/BLE-YC01&Date)
