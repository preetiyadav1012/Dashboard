import os
import re
from dotenv import load_dotenv

load_dotenv()

_raw_instance = os.getenv('SERVICENOW_INSTANCE', 'your_instance.service-now.com')
SERVICENOW_INSTANCE = re.sub(r'^https?://', '', _raw_instance).rstrip('/')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME', 'your_username')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD', 'your_password')
SERVICENOW_API_BASE = f'https://{SERVICENOW_INSTANCE}/api/now'

FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))

CONFLUENCE_BASE_URL = os.getenv('CONFLUENCE_BASE_URL', '')
CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', '')
CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', '')
CONFLUENCE_SPACE_KEY = os.getenv('CONFLUENCE_SPACE_KEY', '')

TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL', '')
TURSO_AUTH_TOKEN   = os.getenv('TURSO_AUTH_TOKEN', '')
