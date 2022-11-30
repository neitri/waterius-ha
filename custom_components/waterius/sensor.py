from __future__ import annotations
import logging
import voluptuous as vol
from .const import *

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import *
from homeassistant.helpers.typing import ConfigType

##
import copy
from datetime import timedelta
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt, slugify

from .common import WateriusBaseEntity

# Import global values.
#from .const import (
#    CHARGE_POINTS,
#    MQTT_ROOT_TOPIC,
#    SENSORS_GLOBAL,
#    SENSORS_PER_LP,
#    openwbSensorEntityDescription,
#)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for Waterius."""
    _LOGGER.info("Start sensor.async_setup_entry\ndomain-%s\ntitle-%s\nsource-%s\nunique_id-%s\nentry_id-%s", 
        config.domain, config.title, config.source, config.unique_id, config.entry_id)
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    topic = config.data[CONF_TOPIC]
    #device = config.data[DATA_DEVICE_INFO]

    sensorList = []
    # Create all global sensors.
    global_sensors = copy.deepcopy(SENSORS_GLOBAL)
    for description in global_sensors:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{topic}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        _LOGGER.info("mqttTopic: %s, \n%s", description.mqttTopicCurrentValue, integrationUniqueID)
        sensorList.append(
            wateriusSensor(
                uniqueID=f"{mqttRoot}_{topic}_{integrationUniqueID}_{description.key}",
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
                device=config.unique_id,
            )
        )

    # Create all sensors for each charge point, respectively.
    #for chargePoint in range(1, nChargePoints + 1):
    waterius_sensors = copy.deepcopy(WATERIUS_SENSORS)
    for description in waterius_sensors:
        description.mqttTopicCurrentValue = (
            f"{mqttRoot}/{topic}/{description.key}"
        )
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        sensorList.append(
            wateriusSensor(
                uniqueID=f"{integrationUniqueID}_{description.key}",
                description=description,
                device_friendly_name=description.name,
                mqtt_root=mqttRoot,
                device=config.unique_id,
            )
        )

    async_add_entities(sensorList)


class wateriusSensor(WateriusBaseEntity, SensorEntity):
    """Representation of an Waterius sensor that is updated via MQTT."""

    entity_description: wateriusSensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: wateriusSensorEntityDescription,
        device: str | None
    ) -> None:
        self.device_friendly_name=device_friendly_name
        self.mqtt_root=mqtt_root
        self.uniqueID=uniqueID
        self.entity_description = description
        self._attr_unique_id = slugify(f"{uniqueID}_{description.key}")
        self.entity_id = f"sensor.{uniqueID}"
        self._attr_name = description.name
        self.device = device

    @property
    def unique_id(self):
        return self.entity_id

    @property
    def device_info(self):
        _LOGGER.info("Get device_info \"%s\" for %s", f"{DATA_DEVICE_INFO}_{self.device}", self.entity_id)
        return self.hass.data[DOMAIN][f"{DATA_DEVICE_INFO}_{self.device}"]()

    @property
    def entity_category(self):
        if hasattr(self.entity_description, 'entity_category'):
            return self.entity_description.entity_category
        return None

    @property
    def device_class(self):
        if hasattr(self.entity_description, 'device_class'):
            return self.entity_description.device_class
        return None # Unusual class

    @property
    def state_class(self):
        if hasattr(self.entity_description, 'state_class'):
            return self.entity_description.state_class
        return None

    @property
    def native_unit_of_measurement(self):
        if hasattr(self.entity_description, 'unit_of_measurement'):
            return self.entity_description.unit_of_measurement
        return None

        
#        if nChargePoints:
#            self._attr_unique_id = slugify(
#                f"{uniqueID}-CP{currentChargePoint}-{description.name}"
#            )
#            self.entity_id = (
#                f"sensor.{uniqueID}-CP{currentChargePoint}-{description.name}"
#            )
#            self._attr_name = f"{description.name} (LP{currentChargePoint})"
#        else:
#            self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
#            self.entity_id = f"sensor.{uniqueID}-{description.name}"
#            self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_native_value = message.payload
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )