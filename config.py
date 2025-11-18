import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Bot Settings
OFFLINE_MESSAGE = os.getenv('OFFLINE_MESSAGE', '⏰ Currently OUT OF STOCK\n\nCheck back later!')
TERMS_AND_CONDITIONS = os.getenv('TERMS_AND_CONDITIONS', 'Please agree to our terms and conditions.')

# Grace period in minutes for late payments
GRACE_PERIOD_MINUTES = 10

# Database
DATABASE_PATH = 'data/bot.db'
