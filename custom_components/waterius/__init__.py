"""
Пример пользовательского компонента MQTT.
Показывает, как общаться с MQTT. Отслеживает тему в MQTT и обновляет 
состояние объекта до последнего сообщения, полученного в этой теме.
Также предлагает услугу «set_state», которая будет публиковать 
сообщение по теме, которое будет передано через MQTT нашему 
слушателю полученных сообщений. Вызовите службу с примером 
полезной нагрузки {"new_state": "некоторое новое состояние"}.
Конфигурация:
Чтобы использовать компонент mqtt_example, вам нужно будет 
добавить следующее в ваш файл configuration.yaml.
configuration.yaml file.
mqtt_basic_async:
    topic: "waterius/mqtt_example/"
"""
from __future__ import annotations
import logging
import voluptuous as vol
from .const import *

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import *
from homeassistant.helpers.typing import ConfigType
from .common import *

_LOGGER = logging.getLogger(__name__)

# The domain of your component. Should be equal to the name of your component.
#DOMAIN = "waterius"


# Схема для проверки настроенной темы MQTT
# Schema to validate the configured MQTT topic
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
                vol.Required(CONF_TOPIC, default=CONF_TOPIC_DEFAULT): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
# mqtt.valid_subscribe_topic


#class WateriusConnect():
#    def __init__(self, topic):
#        self._topic = topic

#    @property
#    def topic(self):
#        return self._topic

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry)->bool:
    """Настройте интеграцию Waterius из записи конфигурации."""
    _LOGGER.info("Start init.async_setup_entry\ndomain-%s\ntitle-%s\nsource-%s\nunique_id-%s\nentry_id-%s", 
        entry.domain, entry.title, entry.source, entry.unique_id, entry.entry_id)
    if DOMAIN not in hass.data: hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data: hass.data[DOMAIN][entry.entry_id] = {}

    hass.data[DOMAIN][f"{DATA_DEVICE_INFO}_{entry.unique_id}"] = lambda: device_info(entry)
    _LOGGER.info("Save device_info %s", f"{DATA_DEVICE_INFO}_{entry.unique_id}")
    # Trigger the creation of sensors.
    #for platform in PLATFORMS:
    #    hass.async_create_task(
    #        hass.config_entries.async_forward_entry_setup(entry, platform)
    #    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    """Define services that publish data to MQTT. The published data is subscribed by waterius
    and the respective settings are changed."""
    #entry.async_on_unload(entry.add_update_listener(entry_update_listener))
#    if DOMAIN not in hass.data: hass.data[DOMAIN] = {}
#    if entry.entry_id not in hass.data: hass.data[DOMAIN][entry.entry_id] = {}
#    
#    waterius = WateriusConnect(
#        topic=entry.data[CONF_TOPIC]
#    )
#    hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION] = waterius
#    _LOGGER.info("async_setup_entry")
    return True

def device_info(self) -> DeviceInfo:
    """Return the device information."""
    return DeviceInfo(
        name=self.unique_id,
        identifiers={(DOMAIN, self.unique_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
    )

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading")
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(entry, platform)
        )
    _LOGGER.debug("Entry unloaded")
    return True
