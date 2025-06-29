import os
from src.cacd import CACD
 
dsn = os.getenv("DB_DSN")
cacd = CACD(dsn) 