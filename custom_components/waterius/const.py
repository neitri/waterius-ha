"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import *


# Домен вашего компонента. Должно совпадать с именем вашего компонента.
DOMAIN = "waterius"
FRIENDLY_NAME = "Waterius"

CONF_TOPIC = 'topic'
MQTT_ROOT_TOPIC_DEFAULT = 'waterius'
CONF_TOPIC_DEFAULT = '13024543'
MQTT_ROOT_TOPIC = 'mqttroot'
DATA_CONNECTION = "connection"
MANUFACTURER = "Waterius"
MODEL = "Waterius"
DATA_DEVICE_INFO = "device_info"

PLATFORMS = [
#    Platform.SELECT,
    Platform.SENSOR,
#    Platform.BINARY_SENSOR,
#    Platform.NUMBER,
#    Platform.SWITCH,
]

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
        vol.Required(CONF_TOPIC, default=CONF_TOPIC_DEFAULT): cv.string,
    }
)

@dataclass
class wateriusSensorEntityDescription(SensorEntityDescription):
    """Enhance the sensor entity description for Waterius"""
    mqttTopicCurrentValue: str | None = None

SENSORS_GLOBAL=[]

WATERIUS_SENSORS=[
    wateriusSensorEntityDescription(
        name= "Cold Water",
        key= "ch1",
        device_class= SensorDeviceClass.WATER,
        unit_of_measurement= "m³",
        state_class= SensorStateClass.TOTAL,
        icon= "mdi:water",
    ),
    wateriusSensorEntityDescription(
        name= "Hot Water",
        key= "ch0",
        device_class= SensorDeviceClass.WATER,
        unit_of_measurement= "m³",
        state_class= SensorStateClass.TOTAL,
        icon= "mdi:water",
    ),
    wateriusSensorEntityDescription(
        name= "Voltage",
        key= "voltage",
        device_class= SensorDeviceClass.VOLTAGE,
        unit_of_measurement= "V",
        state_class= SensorStateClass.MEASUREMENT,
        entity_category= EntityCategory.DIAGNOSTIC,
        icon= "mdi:lightning-bolt",
    ),
#    wateriusSensorEntityDescription(
#        name= "Battery",
#        key= 'voltage_diff',
#        device_class= SensorDeviceClass.BATTERY,
#        icon= "mdi:battery",
#        state_class= SensorStateClass.MEASUREMENT,
#        entity_category= EntityCategory.DIAGNOSTIC,
#        unit_of_measurement= '%',
#    ),
]