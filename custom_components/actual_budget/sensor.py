from __future__ import annotations

import logging
import time

from typing import Dict, Union

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)


from .const import (
    DEFAULT_ICON,
    DOMAIN,
)
from .actual_api import Account, ActualApi, Budget
from .coordinator import ActualDataUpdateCoordinator

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator: ActualDataUpdateCoordinator = config_entry.runtime_data
    unit = config_entry.data.get("unit", "$")

    start_time = time.time()

    accounts = [
        AccountEntity(
            hass=hass,
            coordinator=coordinator,
            account=account,
            unit=unit
        )
        for id, account in coordinator.data.get('accounts', {}).items()
    ]
    async_add_entities(accounts)

    budgets = [
        BudgetEntity(
            hass=hass,
            coordinator=coordinator,
            budget=budget,
            unit=unit
        )
        for id, budget in coordinator.data.get('budgets', {}).items()
    ]
    async_add_entities(budgets)

    _LOGGER.debug("time to add %s", (time.time() - start_time))

class AccountEntity(CoordinatorEntity, SensorEntity):
    coordinator: ActualDataUpdateCoordinator

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        coordinator: ActualDataUpdateCoordinator,
        account: Account,
        unit: str
    ):
        super().__init__(coordinator)
        self.hass = hass
        self._account_id = account.id
        self._name = "Account: " + account.name
        self._unique_id = f"{DOMAIN}-account-{account.id}".lower()
        self._unit_of_measurement = unit
        self._device_class = SensorDeviceClass.MONETARY
        self._state_class = SensorStateClass.MEASUREMENT
        self._available = True

    @property
    def state(self) -> float:
        account = self.coordinator.data.get('accounts').get(self._account_id)
        return account.balance
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        return self._available

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def icon(self):
        return DEFAULT_ICON
    
    @property
    def should_poll(self):
        return False
    
class BudgetEntity(CoordinatorEntity, SensorEntity):
    coordinator: ActualDataUpdateCoordinator

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        coordinator: ActualDataUpdateCoordinator,
        budget: Budget,
        unit: str
    ):
        super().__init__(coordinator)
        self.hass = hass
        self._budget_id = budget.id
        self._name = "Budget: " + budget.name
        self._unique_id = f"{DOMAIN}-budget-{budget.id}".lower()
        self._unit_of_measurement = unit
        self._device_class = SensorDeviceClass.MONETARY
        self._state_class = SensorStateClass.MEASUREMENT
        self._available = True
        _LOGGER.debug("%s", budget)

    @property
    def state(self) -> float:
        budget = self.coordinator.data.get('budgets').get(self._budget_id)
        return budget.budgeted - abs(budget.spent)
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        return self._available

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def icon(self):
        return DEFAULT_ICON
    
    @property
    def extra_state_attributes(self) -> Dict[str, Union[str, float]]:
        budget = self.coordinator.data.get('budgets').get(self._budget_id)
        extra_state_attributes = {}
        extra_state_attributes['spent'] = budget.spent
        extra_state_attributes['budgeted'] = budget.budgeted
        extra_state_attributes['balance'] = budget.budgeted - abs(budget.spent)

        return extra_state_attributes
    
    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False