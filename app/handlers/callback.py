import time
from telegram import Update
from telegram.ext import ContextTypes
from app.services import supabase_utils as db
from app.services.temp_numbers import buy_temp_phone
from app.messages import M
from app.config import ADMIN_ID, logger  # ✅ تم التعديل هنا

async def admin_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """موافقة أو رفض طلب شحن"""
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID:
        await q.edit_message_text("❌ ليس لديك صلاحية.")
        return

    parts = (q.data or "").split('_')
    if len(parts) != 3:
        await q.answer("بيانات غير صالحة.")
        return

    _, action, id_str = parts
    try:
        req_id = int(id_str)
        record = db.supabase.table('recharge_requests').select('*').eq('id', req_id).execute().data
        if not record:
            await q.edit_message_text("⚠️ لم يتم العثور على الطلب.")
            return
        req = record[0]
        user_id = req['user_id']
        amount = float(req['amount'])
        payment_type = req.get('payment_type', '')

        if action == 'approve':
            if "سيرياتيل" in payment_type:
                rate = db.get_usd_rate()
                usd_amount = amount / rate if rate > 0 else 0
                current = await db.get_user_balance(user_id)
                newv = current + usd_amount
                await db.update_user_balance(user_id, newv)
                db.update_recharge_status(req_id, 'approved')
                await context.bot.send_message(user_id, M()['approval_notification'].format(usd_amount, newv))
            else:
                current = await db.get_user_balance(user_id)
                newv = current + amount
                await db.update_user_balance(user_id, newv)
                db.update_recharge_status(req_id, 'approved')
                await context.bot.send_message(user_id, M()['approval_notification'].format(amount, newv))

            await q.edit_message_text((q.message.text or "") + "\n✅ تمت الموافقة.")

        elif action == 'reject':
            db.update_recharge_status(req_id, 'rejected')
            await context.bot.send_message(user_id, M()['rejection_notification'])
            await q.edit_message_text((q.message.text or "") + "\n❌ تم الرفض.")

    except Exception as e:
        logger.error(f"admin_approval_callback error: {e}")
        await q.edit_message_text(f"خطأ: {e}")

async def phone_inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة للبلاك ليست أو إعادة شراء رقم"""
    q = update.callback_query
    await q.answer()
    data = q.data or ""
    user_id = q.from_user.id

    if data.startswith("blacklist_"):
        phone = data.split("blacklist_", 1)[1]
        ok = db.add_blacklisted_number(phone, user_id)
        if ok:
            await q.edit_message_text((q.message.text or "") + "\n🚫 تم حظر الرقم.")
        else:
            await q.edit_message_text("⚠️ خطأ أثناء إضافة الرقم للبلاك ليست.")
        return

    if data.startswith("repurchase_"):
        pid = data.split("repurchase_", 1)[1]
        await context.bot.send_message(user_id, "🔁 نحاول شراء رقم جديد لنفس الخدمة...")
        await buy_temp_phone(update, context, "us", pid)
