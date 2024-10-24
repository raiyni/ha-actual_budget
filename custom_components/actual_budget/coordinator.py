from __future__ import annotations

from logging import getLogger
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MIN_TIME_BETWEEN_UPDATES

from .actual_api import ActualApi

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class ActualDataUpdateCoordinator(DataUpdateCoordinator):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=MIN_TIME_BETWEEN_UPDATES
        )

    async def _async_update_data(self) -> dict[str, Any]:
        return await self._get_data()
    
    
    async def _get_data(self) -> dict[str, Any]:
        try:
            with ActualApi(self.hass, self.config_entry) as api:
                api.actual = await api.create_session()

                accounts = await api.get_accounts()
                budgets = await api.get_budgets()

                data = {
                    'accounts': accounts,
                    'budgets': budgets
                }
                
                return data
            
        except Exception as error:
            raise UpdateFailed(error) from error
            