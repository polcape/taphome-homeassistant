"""TapHome climate integration."""
from .taphome_sdk import *

import logging
from homeassistant.components.climate import ClimateEntity

from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.components.climate.const import SUPPORT_TARGET_TEMPERATURE

from . import TAPHOME_API_SERVICE

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, devices: list):
    tapHomeApiService = hass.data[TAPHOME_API_SERVICE]
    thermostatService = ThermostatService(tapHomeApiService)

    thermostats = []
    for device in devices:
        thermostat = await async_create_thermostat(thermostatService, device)
        thermostats.append(thermostat)

    async_add_entities(thermostats)


async def async_create_thermostat(thermostatService: ThermostatService, device: Device):
    thermostat = TapHomeThermostat(thermostatService, device)
    await thermostat.async_refresh_state()
    return thermostat


class TapHomeThermostat(ClimateEntity):
    """Representation of an Thermostat"""

    def __init__(self, thermostatService: ThermostatService, device: Device):
        self._thermostatService = thermostatService
        self._device = device
        self._supported_features = SUPPORT_TARGET_TEMPERATURE
        self._target_temperature = None
        self._current_temperature = None
        self._min_temperature = None
        self._max_temperature = None

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def name(self):
        return self._device.name

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def current_temperature(self):
        return self._current_temperature

    @property
    def min_temp(self):
        return self._min_temperature

    @property
    def max_temp(self):
        return self._max_temperature

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return None

    @property
    def hvac_modes(self):
        """Return the list of available operation/controller modes."""
        return []

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)

        result = await self._thermostatService.async_set_desired_temperature(
            self._device, temp
        )

        if result == ValueChangeResult.FAILED:
            await self.async_refresh_state()
        else:
            self._target_temperature = temp

    def async_update(self, **kwargs):
        return self.async_refresh_state()

    async def async_refresh_state(self):
        state = await self._thermostatService.async_get_thermostat_state(self._device)
        self._target_temperature = state.desired_temperature
        self._current_temperature = state.real_temperature
        self._min_temperature = state.min_temperature
        self._max_temperature = state.max_temperature
