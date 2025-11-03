
# app/handlers/registration.py
import bcrypt
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.services import supabase_utils as db
from app.keyboards import kb_main
from app.messages import M
from app.constants import USERNAME_STATE, PASSWORD_STATE, CAPTCHA_STATE
from app.logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if db.is_registered(user_id):
        await show_main_menu(update, context)
        return ConversationHandler.END
    await update.message.reply_text(M()['welcome'])
    await update.message.reply_text(M()['ask_username'])
    return USERNAME_STATE

async def username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    try:
        exists = db.supabase.table('users').select('username').eq('username', username).execute()
        if exists.data:
            await update.message.reply_text(M()['username_taken'])
            return USERNAME_STATE
        context.user_data['reg_username'] = username
        await update.message.reply_text(M()['username_saved'])
        return PASSWORD_STATE
    except Exception as e:
        logger.error(f"username_handler error: {e}")
        await update.message.reply_text(M()['error'].format("التحقق من الاسم"))
        return USERNAME_STATE

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    context.user_data['reg_password'] = hashed
    await update.message.reply_text(M()['password_saved'])
    context.user_data['captcha_attempts'] = 0
    return CAPTCHA_STATE

async def captcha_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "1":
        try:
            user = update.effective_user
            db.supabase.table('users').insert({
                'user_id': user.id,
                'username': context.user_data['reg_username'],
                'password_hash': context.user_data['reg_password'],
                'balance': 0.0
            }).execute()
            await update.message.reply_text(M()['captcha_success'], reply_markup=kb_main())
            context.user_data.clear()
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"captcha_check insert error: {e}")
            await update.message.reply_text(M()['error'].format("التسجيل"))
            return CAPTCHA_STATE
    else:
        context.user_data['captcha_attempts'] = context.user_data.get('captcha_attempts', 0) + 1
        if context.user_data['captcha_attempts'] >= 3:
            await update.message.reply_text(M()['too_many_attempts'], reply_markup=kb_main())
            context.user_data.clear()
            return ConversationHandler.END
        await update.message.reply_text(M()['wrong_captcha'])
        return CAPTCHA_STATE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 تم إلغاء العملية.", reply_markup=kb_main())
    context.user_data.clear()
    return ConversationHandler.END
