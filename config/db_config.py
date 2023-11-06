
import os
from dotenv import load_dotenv

load_dotenv()

# Database configurations
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = "" if os.getenv('APP_MODE')=="dev" else os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

DEFUALT_OFFSET = 0
DEFUALT_LIMIT = 20
