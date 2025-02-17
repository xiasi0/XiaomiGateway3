from homeassistant.const import STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN
from .core.converters import Converter
from .core.device import XDevice
from .core.entity import XEntity
from .core.gateway import XGateway


async def async_setup_entry(hass, config_entry, add_entities):
    def setup(gateway: XGateway, device: XDevice, conv: Converter):
        if conv.attr in device.entities:
            entity = device.entities[conv.attr]
        else:
            entity = XiaomiSwitch(gateway, device, conv)
        add_entities([entity])

    gw: XGateway = hass.data[DOMAIN][config_entry.entry_id]
    gw.add_setup(__name__, setup)


# noinspection PyAbstractClass
class XiaomiSwitch(XEntity, ToggleEntity, RestoreEntity):
    _attr_is_on: bool = None

    @callback
    def async_set_state(self, data: dict):
        """Handle state update from gateway."""
        if self.attr in data:
            self._attr_is_on = data[self.attr]

    @callback
    def async_restore_last_state(self, state: str, attrs: dict):
        self._attr_is_on = state == STATE_ON

    async def async_turn_on(self):
        await self.device_send({self.attr: True})

    async def async_turn_off(self):
        await self.device_send({self.attr: False})

    async def async_update(self):
        await self.device_read(self.subscribed_attrs)
