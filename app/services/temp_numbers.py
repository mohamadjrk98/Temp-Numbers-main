# app/services/temp_numbers.py
import time
import requests
from urllib.parse import quote_plus
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from app.config import BASE_URL, USERNAME, API_KEY, NUM_COUNT, SERIAL, logger  # ✅ التعديل هنا
from app.services import supabase_utils as db
from app.messages import M
from app.logger import logger

# إعدادات أساسية
BASE_URL = Config.BASE_URL
USERNAME = Config.USERNAME
API_KEY = Config.API_KEY
NUM_COUNT = Config.NUM_COUNT
SERIAL = Config.SERIAL


async def buy_temp_phone(update: Update, context: ContextTypes.DEFAULT_TYPE, country_code: str, service_pid: str):
    """شراء رقم مؤقت لخدمة معينة من API الخارجي."""
    user_id = update.effective_user.id
    price = db.get_phone_price()
    balance = await db.get_user_balance(user_id)

    if balance < price:
        await update.message.reply_text(M()['low_balance'])
        return

    await update.message.reply_text(M()['buy_phone_prompt'])
    try:
        url = f"{BASE_URL}/getMobile"
        params = {
            'name': USERNAME,
            'ApiKey': API_KEY,
            'cuy': country_code,
            'pid': service_pid,
            'num': NUM_COUNT,
            'noblack': 0,
            'serial': SERIAL,
            'secret_key': 'null',
            'vip': 'null'
        }

        logger.info(f"getMobile params: {params}")
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"getMobile response: {data}")

        if data.get("code") != 200:
            raise ValueError(f"API Error {data.get('code')}: {data.get('msg')}")

        phone = data.get("data")
        if not phone:
            raise ValueError("لم يتم استلام رقم من الـ API")

        # خصم الرصيد
        new_balance = balance - price
        await db.update_user_balance(user_id, new_balance)

        # حفظ الهاتف والـ PID في ذاكرة المستخدم
        context.user_data['temp_phone'] = phone
        context.user_data['temp_pid'] = service_pid

        # أزرار النسخ والبلاك ليست
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 انسخ الرقم", switch_inline_query_current_chat=str(phone)),
                InlineKeyboardButton("🚫 إضافة للبلاك-ليست", callback_data=f"blacklist_{quote_plus(str(phone))}")
            ],
            [
                InlineKeyboardButton("🔄 أعد شراء رقم", callback_data=f"repurchase_{service_pid}")
            ]
        ])

        await update.message.reply_text(
            f"📲 **رقمك المؤقت:** `{phone}`\n\n{M()['get_code_tip']}",
            reply_markup=keyboard, parse_mode='Markdown'
        )
        await update.message.reply_text(M()['deducted'].format(price, new_balance))

    except Exception as e:
        logger.error(f"buy_temp_phone error: {e}")
        await update.message.reply_text(M()['error'].format(f"شراء الرقم: {str(e)}"))


async def get_sms_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جلب رسالة التحقق (SMS code) من الـ API."""
    phone = context.user_data.get('temp_phone')
    service_pid = context.user_data.get('temp_pid')

    if not phone:
        await update.message.reply_text(M()['no_phone'])
        return

    await update.message.reply_text(M()['searching'])
    try:
        url = f"{BASE_URL}/getMsg"
        params = {
            'name': USERNAME,
            'ApiKey': API_KEY,
            'pid': service_pid,
            'pn': phone,
            'serial': SERIAL
        }

        start = time.time()
        while time.time() - start < 60:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"getMsg response: {data}")

            if data.get("code") == 200:
                code = data.get("data")
                await update.message.reply_text(f"✅ الكود المستلم: `{code}`", parse_mode='Markdown')
                context.user_data.pop('temp_phone', None)
                context.user_data.pop('temp_pid', None)
                return
            elif data.get("code") in [908, 203]:
                time.sleep(5)
                continue
            else:
                raise ValueError(f"API Error {data.get('code')}: {data.get('msg')}")

        await update.message.reply_text(M()['no_sms'])

    except Exception as e:
        logger.error(f"get_sms_code error: {e}")
        await update.message.reply_text(M()['error'].format(str(e)))
