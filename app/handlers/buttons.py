# app/handlers/buttons.py
from telegram import Update
from telegram.ext import ContextTypes
from app.messages import M
from app.keyboards import kb_main, kb_countries, kb_charge
from app.services import supabase_utils as db
from app.services.temp_numbers import buy_temp_phone, get_sms_code
from app.logger import logger
from app.constants import SERVICE_TO_PID
from app.keyboards import kb_services_page

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة الرئيسية"""
    await update.message.reply_text(M()['choose_action'], reply_markup=kb_main())
    # تصفير الحالات المؤقتة
    for k in [
        'recharge_step', 'recharge_type', 'temp_transfer', 'temp_photo',
        'waiting_country', 'selected_country', 'waiting_service',
        'selected_service', 'service_page'
    ]:
        context.user_data.pop(k, None)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد على أزرار المستخدم"""
    text = (update.message.text or "").strip()
    user_id = update.effective_user.id
    msgs = M()

    # 🏠 العودة للقائمة
    if text == "رجوع":
        await show_main_menu(update, context)
        return

    # 👤 عرض الحساب
    if text == "👤 حسابي":
        bal = await db.get_user_balance(user_id)
        await update.message.reply_text(msgs['account'].format(user_id, bal), parse_mode='Markdown')
        return

    # 💳 الشحن
    if text == "💳 شحن الحساب":
        await update.message.reply_text(msgs['choose_method'], reply_markup=kb_charge())
        return

    # 🔑 شراء رقم مؤقت
    if text == "🔑 شراء رقم مؤقت":
        await update.message.reply_text(msgs['choose_country'], reply_markup=kb_countries())
        context.user_data['waiting_country'] = True
        return

    # ✉️ جلب الكود
    if text == "✉️ الحصول على الكود":
        await get_sms_code(update, context)
        return

    # 🌍 اختيار الدولة
    if context.user_data.get('waiting_country'):
        if text == "🇺🇸 USA":
            context.user_data['selected_country'] = 'us'
            context.user_data.pop('waiting_country', None)
            markup, page_info = kb_services_page(context)
            await update.message.reply_text(
                msgs['country_selected'].format("USA") + (f"\n{page_info}" if page_info else ""),
                reply_markup=markup, parse_mode='Markdown'
            )
            context.user_data['waiting_service'] = True
            return
        if text == "رجوع":
            context.user_data.pop('waiting_country', None)
            await show_main_menu(update, context)
            return
        await update.message.reply_text(msgs['use_buttons'])
        return

    # 📱 اختيار الخدمة
    if context.user_data.get('waiting_service'):
        services = list(SERVICE_TO_PID.keys())
        if text in [msgs['next_page'], msgs['prev_page']]:
            page = context.user_data.get('service_page', 0)
            items = 6
            if text == msgs['next_page'] and (page + 1) * items < len(services):
                context.user_data['service_page'] = page + 1
            elif text == msgs['prev_page'] and page > 0:
                context.user_data['service_page'] = page - 1
            markup, page_info = kb_services_page(context)
            await update.message.reply_text(
                msgs['choose_service'] + (f"\n{page_info}" if page_info else ""),
                reply_markup=markup, parse_mode='Markdown'
            )
            return

        pid = SERVICE_TO_PID.get(text)
        if pid:
            context.user_data.pop('waiting_service', None)
            await update.message.reply_text(msgs['service_selected'].format(text), parse_mode='Markdown')
            cc = context.user_data.get('selected_country', 'us')
            await buy_temp_phone(update, context, cc, pid)
            for k in ['selected_country', 'selected_service', 'service_page']:
                context.user_data.pop(k, None)
            return

        if text == "رجوع":
            context.user_data.pop('waiting_service', None)
            await show_main_menu(update, context)
            return

    await update.message.reply_text(msgs['use_buttons'])
