from datetime import timedelta

DOMAIN = "actual_budget"
PLATFORM = "sensor"
DOMAIN_DATA = f"{DOMAIN}_data"

DEFAULT_ICON = "mdi:bank"

CONFIG_ENDPOINT = "endpoint"
CONFIG_PASSWORD = "password"
CONFIG_FILE = "file"
CONFIG_UNIT = "unit"
CONFIG_CERT = "cert"
CONFIG_ENCRYPT_PASSWORD = "encrypt_password"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)