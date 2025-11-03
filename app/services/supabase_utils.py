# app/services/supabase_utils.py

import time
from app.config import Config
from app.logger import logger

# إنشاء عميل Supabase عند الاستيراد
supabase = Config.create_supabase()

# =========================
# 🧩 المستخدمون
# =========================

def is_registered(user_id: int) -> bool:
    """تحقق ما إذا كان المستخدم مسجل مسبقًا."""
    try:
        data = supabase.table('users').select('user_id').eq('user_id', user_id).execute()
        return bool(data.data)
    except Exception as e:
        logger.error(f"is_registered error: {e}")
        return False


async def get_user_balance(user_id: int) -> float:
    """إرجاع رصيد المستخدم."""
    try:
        data = supabase.table('users').select('balance').eq('user_id', user_id).execute()
        return float(data.data[0]['balance']) if data.data else 0.0
    except Exception as e:
        logger.error(f"get_user_balance error: {e}")
        return 0.0


async def update_user_balance(user_id: int, new_balance: float):
    """تحديث رصيد المستخدم."""
    try:
        supabase.table('users').update({'balance': new_balance}).eq('user_id', user_id).execute()
    except Exception as e:
        logger.error(f"update_user_balance error: {e}")

# =========================
# ⚙️ الإعدادات العامة
# =========================

def get_setting(key: str, default=None):
    """قراءة قيمة إعداد من جدول settings."""
    try:
        data = supabase.table('settings').select('value').eq('key', key).execute()
        return data.data[0]['value'] if data.data else default
    except Exception as e:
        logger.error(f"get_setting error ({key}): {e}")
        return default


def set_setting(key: str, value: str):
    """تحديث أو إدراج إعداد في جدول settings."""
    try:
        supabase.table('settings').upsert({'key': key, 'value': str(value)}, on_conflict='key').execute()
        return True
    except Exception as e:
        logger.error(f"set_setting error ({key}): {e}")
        return False


def get_phone_price() -> float:
    """جلب سعر الرقم من settings (key=phone_price)."""
    try:
        val = get_setting('phone_price', '5.0')
        return float(val)
    except Exception as e:
        logger.error(f"get_phone_price error: {e}")
        return 5.0


def get_recharge_address(method: str) -> str:
    """جلب عنوان الشحن الخاص بطريقة معينة."""
    key = method.lower().replace(' ', '_').replace('(ل.س)', 'sp').replace('(دولار)', 'usd').replace('(bep20)', 'bep20')
    return get_setting(key, 'غير محدد')


def get_usd_rate() -> float:
    """قراءة سعر الدولار (SYP per USD)."""
    try:
        val = get_setting('usd_rate', '10000.0')
        return float(val)
    except Exception as e:
        logger.error(f"get_usd_rate error: {e}")
        return 10000.0


def set_usd_rate(v: float):
    """تحديث سعر الدولار."""
    return set_setting('usd_rate', str(v))


def next_recharge_id() -> int:
    """إنشاء رقم طلب شحن جديد (sequence)."""
    try:
        data = supabase.table('settings').select('value').eq('key', 'recharge_id_sequence').execute()
        if data.data:
            last_id = int(data.data[0]['value'])
            nxt = last_id + 1
            supabase.table('settings').update({'value': str(nxt)}).eq('key', 'recharge_id_sequence').execute()
            return nxt
        else:
            initial = 2300
            supabase.table('settings').insert({'key': 'recharge_id_sequence', 'value': str(initial + 1)}).execute()
            return initial
    except Exception as e:
        logger.error(f"next_recharge_id error: {e}")
        return 990000 + int(time.time())

# =========================
# 💵 طلبات الشحن
# =========================

def insert_recharge_request(record: dict):
    """إدراج طلب شحن جديد في قاعدة البيانات."""
    try:
        supabase.table('recharge_requests').insert(record).execute()
        return True
    except Exception as e:
        logger.error(f"insert recharge request error: {e}")
        return False


def update_recharge_status(req_id: int, status: str):
    """تحديث حالة طلب شحن."""
    try:
        supabase.table('recharge_requests').update({'status': status}).eq('id', req_id).execute()
    except Exception as e:
        logger.error(f"update_recharge_status error: {e}")


def get_pending_recharges():
    """جلب الطلبات قيد الانتظار."""
    try:
        data = supabase.table('recharge_requests').select('*').eq('status', 'pending').execute()
        return data.data or []
    except Exception as e:
        logger.error(f"get_pending_recharges error: {e}")
        return []

# =========================
# 🚫 البلاك ليست
# =========================

def add_blacklisted_number(phone: str, user_id: int):
    """إضافة رقم إلى قائمة البلاك ليست."""
    try:
        supabase.table('blacklisted_numbers').upsert({
            'phone': str(phone),
            'blocked_by': user_id,
            'blocked_at': int(time.time())
        }, on_conflict='phone').execute()
        return True
    except Exception as e:
        logger.error(f"add_blacklisted_number error: {e}")
        return False
