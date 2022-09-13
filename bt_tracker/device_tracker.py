"""BT Tracker"""
import asyncio
import logging

from datetime import timedelta

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.components.device_tracker.const import (
    CONF_SCAN_INTERVAL,
    SCAN_INTERVAL,
    SourceType,
)

from homeassistant.components.device_tracker.legacy import (
    YAML_DEVICES,
    async_load_config,
)

DOMAIN = "bt_tracker"
_LOGGER = logging.getLogger(DOMAIN)

BEACON_UUID_PREFIX = "BEACON_"

async def async_setup_scanner(
    hass,
    config,
    async_see,
    discovery_info,
):
    interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    beacons = []

    yaml_path = hass.config.path(YAML_DEVICES)
    for device in await async_load_config(yaml_path, hass, timedelta(0)):
        if device.track and device.mac and device.mac.startswith(BEACON_UUID_PREFIX):
            uuid = device.mac[len(BEACON_UUID_PREFIX):]
            beacon = {"name": device.name, "uuid": uuid}
            beacons.append(beacon)

    def get_beacon(uuid):
        for beacon in beacons:
            beacon_uuid = beacon["uuid"]
            if beacon_uuid.lower() == uuid.lower():
                return beacon
        return None

    async def on_new_device(service_uuids):
        if len(service_uuids) != 1:
            return

        uuid = service_uuids[0]
        beacon = get_beacon(uuid)
        if beacon is None:
            return

        beacon_name = beacon["name"]
        await async_see(mac = BEACON_UUID_PREFIX + uuid,
            host_name = beacon_name,
            source_type = SourceType.BLUETOOTH_LE
        )

    def refresh_devices(now):
        for service_info in bluetooth.async_discovered_service_info(hass, False):
            hass.async_create_task(
                on_new_device(service_info.advertisement.service_uuids)
            )

    def on_device_discovered(service_info, change):
        hass.async_create_task(
            on_new_device(service_info.advertisement.service_uuids)
        )

    cancels = [
        bluetooth.async_register_callback(
            hass,
            on_device_discovered,
            BluetoothCallbackMatcher(
                connectable = False
            ),
            bluetooth.BluetoothScanningMode.ACTIVE
        ),
        async_track_time_interval(hass, refresh_devices, interval)
    ]

    def stop_scan(event):
        for cancel in cancels:
            cancel()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_scan)

    return True
