import os
from cacd import CACD

dsn = os.getenv("DB_DSN")
cacd = CACD(dsn) 