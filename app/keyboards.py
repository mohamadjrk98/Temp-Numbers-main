# app/keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from app.messages import M
from app.constants import SERVICE_TO_PID

def kb_main():
    keyboard = [
        [KeyboardButton("🔑 شراء رقم مؤقت")],
        [KeyboardButton("👤 حسابي"), KeyboardButton("💳 شحن الحساب")],
        [KeyboardButton("✉️ الحصول على الكود")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def kb_countries():
    keyboard = [
        [KeyboardButton("🇺🇸 USA")],
        [KeyboardButton("رجوع")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def kb_charge():
    keyboard = [
        [KeyboardButton("شام كاش (ل.س)"), KeyboardButton("شام كاش (دولار)")],
        [KeyboardButton("USDT (BEP20)"), KeyboardButton("سيرياتيل كاش")],
        [KeyboardButton("رجوع")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def kb_admin():
    keyboard = [
        [KeyboardButton("📊 الإحصائيات"), KeyboardButton("⚙️ تعديل سعر الرقم")],
        [KeyboardButton("📝 تعديل عناوين الشحن"), KeyboardButton("📋 طلبات الشحن")],
        [KeyboardButton("➕ إضافة رصيد يدوي"), KeyboardButton("➖ خصم رصيد يدوي")],
        [KeyboardButton("💵 سعر الدولار"), KeyboardButton("رجوع")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def kb_admin_services():
    return ReplyKeyboardMarkup([
        [KeyboardButton("تفعيل/تعطيل الخدمة"), KeyboardButton("تعديل الإعدادات")],
        [KeyboardButton("رجوع")]
    ], resize_keyboard=True)

def kb_services_page(context):
    services = list(SERVICE_TO_PID.keys())
    page = context.user_data.get('service_page', 0)
    items = 6

    if len(services) <= items:
        keyboard = [[KeyboardButton(s)] for s in services]
        keyboard.append([KeyboardButton("رجوع")])
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True), None

    start = page * items
    end = min(start + items, len(services))
    page_services = services[start:end]
    keyboard = [[KeyboardButton(s)] for s in page_services]

    nav = []
    if page > 0: nav.append(KeyboardButton(M()['prev_page']))
    if end < len(services): nav.append(KeyboardButton(M()['next_page']))
    if nav: keyboard.append(nav)

    keyboard.append([KeyboardButton("رجوع")])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    page_info = M()['service_page_info'].format(page + 1, (len(services) + items - 1) // items)
    return markup, page_info
