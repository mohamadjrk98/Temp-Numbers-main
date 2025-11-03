# app/config.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Config:
    # 🧠 Telegram & API credentials
    USERNAME = os.getenv('USERNAME')
    API_KEY = os.getenv('API_KEY')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    COUNTRY = os.getenv('COUNTRY', 'us')
    NUM_COUNT = int(os.getenv('NUM_COUNT', 1))
    SERIAL = int(os.getenv('SERIAL', 2))
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

    # 🗄️ Supabase credentials
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # 🌐 External API endpoint
    BASE_URL = "https://api.durianrcs.com/out/ext_api"

    @staticmethod
    def create_supabase() -> Client:
        """إنشاء عميل Supabase."""
        if not all([
            Config.BOT_TOKEN, Config.USERNAME, Config.API_KEY,
            Config.SUPABASE_URL, Config.SUPABASE_KEY, Config.ADMIN_ID
        ]):
            raise ValueError("❌ Missing required environment variables!")

        try:
            return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        except Exception as e:
            raise RuntimeError(f"Failed to create Supabase client: {e}")
