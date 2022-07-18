from os import getenv
from dotenv import load_dotenv

load_dotenv()

# bot config
BOT_TOKEN = getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, getenv('ADMIN_IDS').split()))
BOT_USERNAME = getenv('BOT_USERNAME')

# db config
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')
DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_DATABASE = getenv('DB_DATABASE')
DB_DSN = getenv('DATABASE_URL')

# deploy webhook config
NGROK_URL = getenv("NGROK_URL")
WEBHOOK_HOST = f'{NGROK_URL}'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = getenv('NGROK_PORT', 80)