from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORM

from .coordinator import ActualDataUpdateCoordinator

__version__ = "0.1"
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

PLATFORMS: list[str] = [PLATFORM]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    config_entry.runtime_data = coordinator = ActualDataUpdateCoordinator(hass=hass, config_entry=config_entry)

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)