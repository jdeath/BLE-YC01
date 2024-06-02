"""Parser for YC01 BLE devices"""

from __future__ import annotations

import asyncio
import dataclasses
import struct
from collections import namedtuple
from datetime import datetime
import logging

# from logging import Logger
from math import exp
from typing import Any, Callable, Tuple

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .const import (
    BATT_100, BATT_0
)


READ_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class YC01Device:
    """Response data with information about the YC01 device"""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )

# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
class YC01BluetoothDeviceData:
    """Data for YC01 BLE sensors."""

    _event: asyncio.Event | None
    _command_data: bytearray | None

    def __init__(
        self,
        logger: Logger,
    ):
        super().__init__()
        self.logger = logger
        self.logger.debug("In Device Data")
        
    def decode(self, byte_frame : bytes ):

        frame_array = [int(x) for x in byte_frame]
        size = len(frame_array)

        for i in range(size-1, 0 , -1):
            tmp=frame_array[i]
            hibit1=(tmp&0x55)<<1
            lobit1=(tmp&0xAA)>>1
            tmp=frame_array[i-1]
            hibit=(tmp&0x55)<<1
            lobit=(tmp&0xAA)>>1
            frame_array[i]=0xff -(hibit1|lobit)
            frame_array[i-1]= 0xff -(hibit|lobit1)

        return frame_array
    
    def reverse_bytes(self, bytes : list):
        return (bytes[0] << 8) + bytes[1]

    def decode_position(self,decodedData,idx):
        return self.reverse_bytes(decodedData[idx:idx+2])
        
    async def _get_status(self, client: BleakClient, device: YC01Device) -> YC01Device:
        
        _LOGGER.debug("Getting Status")
        data = await client.read_gatt_char(READ_UUID)
        decodedData = self.decode(data)
        
        
        # temp = ((message[13]<<8) + message[14]);
        # ph = ((message[3]<<8) + message[4]);
        # orp = ((message[9]<<8) + message[10]);
        # battery = ((message[15]<<8) + message[16]);
        # ec = ((message[5]<<8) + message[6]);
        # tds = ((message[7]<<8) + message[8]);
        # cloro = ((message[11]<<8) + message[12]);
        # id(ble_yc01_temperature_sensor).publish_state(temp/10.0);
        # id(ble_yc01_ph_sensor).publish_state(ph/100.0);
        # id(ble_yc01_orp_sensor).publish_state(orp);
        # id(ble_yc01_battery).publish_state(battery/31.9);
        # id(ble_yc01_ec_sensor).publish_state(ec);
        # id(ble_yc01_tds_sensor).publish_state(tds);
        # id(ble_yc01_cloro).publish_state(cloro/10.0)
        
        constant = decodedData[1]
        product_name_code = decodedData[2]
        hold_reading = decodedData[17] >> 4

        backlight_status = (decodedData[17] & 0x0F) >> 3

        battery = round(100 * (self.decode_position(decodedData,15) - BATT_0) / (BATT_100 - BATT_0))
        battery = min(max(0, battery), 100)
        device.sensors["battery"] = battery

        ec = self.decode_position(decodedData,5)
        device.sensors["EC"] = ec
        device.sensors["salt"] = ec * 0.55
        
        device.sensors["TDS"] = self.decode_position(decodedData,7)
        
        cloro = self.decode_position(decodedData,11) / 10
        if cloro == 6553.6: cloro = float("nan")
        device.sensors["cloro"] = cloro

        device.sensors["pH"] = self.decode_position(decodedData,3) / 100.0 
		
        device.sensors["ORP"] = self.decode_position(decodedData,9) / 1000.0
		
        device.sensors["temperature"] = self.decode_position(decodedData,13) / 10.0
        
        #fcAdjust = 0 
        #device.sensors["freeChlorine"] = round( 0.23 * (1 - fcAdjust) * (14 - ph) ** (1/(400 - orp))*(ph - 4.1) ** ( (orp - 516)/145) + 10.0 ** ( (orp + ph * 70 - 1282 ) / 40 ), 1 );  
        
        _LOGGER.debug("Got Status")
        return device

    
    async def update_device(self, ble_device: BLEDevice) -> YC01Device:
        """Connects to the device through BLE and retrieves relevant data"""
        _LOGGER.debug("Update Device")
        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        _LOGGER.debug("Got Client")
        #await client.pair()
        device = YC01Device()
        _LOGGER.debug("Made Device")
        
        device = await self._get_status(client, device)
        _LOGGER.debug("got Status")
        device.name = ble_device.address
        device.address = ble_device.address
        _LOGGER.debug("device.name: %s", device.name)
        _LOGGER.debug("device.address: %s", device.address)

        await client.disconnect()

        return device
																	 
