from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from app.services import supabase_utils as db
from app.messages import M
from app.keyboards import kb_admin, kb_charge
from app.config import ADMIN_ID, logger  # ✅ هذا هو الصحيح

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(M()['access_denied'])
        return
    await update.message.reply_text(M()['admin_welcome'], reply_markup=kb_admin(), parse_mode='Markdown')

async def admin_only_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        users = db.supabase.table('users').select('*').execute()
        user_count = len(users.data)
        requests_today = db.get_pending_recharges()
        req_count = len(requests_today)
        await update.message.reply_text(M()['admin_stats'].format(user_count, req_count), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"admin_only_stats error: {e}")
        await update.message.reply_text(M()['error'].format("جلب الإحصائيات"))
