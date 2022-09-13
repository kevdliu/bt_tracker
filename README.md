# bt_tracker
Custom integration for Home Assistant which tracks BLE devices by service UUID instead of MAC

### Example configuration.xml
```
device_tracker:
  - platform: bt_tracker
    interval_seconds: 30
    consider_home: 45
    new_device_defaults:
      track_new_devices: true
```

### Example known_devices.yaml
```
my_beacon:
  name: My Beacon
  mac: BEACON_2f4fb006-30b0-4370-b412-94a31a20c014
  icon:
  picture:
  track: true
```

### Notes
Unlike the official Bluetooth LE Tracker integration, this custom integration does not populate known_devices.yaml with discovered BLE devices. 
You have to manually add an entry in known_devices.yaml for each BLE device you want to track. Make sure to replace the UUID in the `mac` field with 
the service UUID your BLE device advertises. 

This custom integration is extremely tailored to my personal use case. As such, it'll filter out any BLE devices that does not advertise **exactly** one service UUID.
I'm using the nRF Connect app on Android as a simulated BLE beacon. Feel free to modify the code as you see fit in your use case. 
