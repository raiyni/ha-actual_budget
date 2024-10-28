import calendar
import datetime
from decimal import Decimal
import logging

from dataclasses import dataclass
from typing import Dict
from actual import Actual

from actual.queries import get_accounts,  get_budgets, _transactions_base_query
from actual.database import (
    Transactions
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

@dataclass
class Group:
    id: str
    name: str

@dataclass
class Budget:
    id: str
    name: str
    budgeted: float
    spent: float
    group: str
    month: str

@dataclass
class Account:
    name: str
    balance: float
    id: str

class ActualApi:
    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        self.hass = hass
        self.endpoint = config.data.get('endpoint')
        self.password = config.data.get('password')
        self.file = config.data.get('file')
        self.cert = config.data.get('cert', False)
        self.encrypt_password = config.data.get('encrypt_password')
        self.actual = None
        if not self.cert:
            self.cert = False
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.actual:
            self.actual.__exit__(exc_type, exc_val, exc_tb)

    async def create_session(self) -> Actual:
        return await self.hass.async_add_executor_job(self.create_session_sync)
    
    def create_session_sync(self) -> Actual:
        actual = Actual(
            base_url=self.endpoint,
            password=self.password,
            cert=self.cert,
            encryption_password=self.encrypt_password,
            file=self.file,
        )
        actual.__enter__()

        return actual

    async def get_accounts(self) -> Dict[str, Account]:
        return await self.hass.async_add_executor_job(self.get_accounts_sync)

    def get_accounts_sync(self) -> Dict[str, Account]:
        accounts = get_accounts(self.actual.session)
        return {a.id: Account(name=a.name, balance=a.balance, id=a.id) for a in accounts}

    async def get_budgets(self) -> Dict[str, Budget]:
        return await self.hass.async_add_executor_job(self.get_budgets_sync)

    def get_budgets_sync(self) -> Dict[str, Budget]:
        budgets_raw = get_budgets(self.actual.session, datetime.date.today())
        budgets: Dict[str, Budget] = {}
        for budget_raw in budgets_raw:
            if budget_raw.category is None:
                continue
            
            category = budget_raw.category
            id = str(category.id)
            amount = budget_raw.get_amount()
            month = str(budget_raw.month)

            spent = budget_raw.balance

            budget = Budget(name=category.name, budgeted=float(amount), id=id, group=category.group.name, month=month, spent=float(spent))
            budgets[id] = budget
        return budgets
