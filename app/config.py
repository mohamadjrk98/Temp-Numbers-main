import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# تحميل متغيرات البيئة
load_dotenv()

# ----------------------------
# متغيرات البيئة الأساسية
# ----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
USERNAME = os.getenv("USERNAME")
PIDS = [pid.strip() for pid in os.getenv("PID", "").split(",") if pid.strip()]
COUNTRY = os.getenv("COUNTRY", "us")
NUM_COUNT = int(os.getenv("NUM_COUNT", 1))
SERIAL = int(os.getenv("SERIAL", 2))
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BASE_URL = "https://api.durianrcs.com/out/ext_api"

# ----------------------------
# إعداد الـ Logger
# ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------
# إنشاء عميل Supabase بأمان
# ----------------------------
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        supabase = None
else:
    logger.warning("⚠️ Supabase credentials missing — database features disabled.")
