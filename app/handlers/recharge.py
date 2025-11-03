# app/handlers/recharge.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.messages import M
from app.services import supabase_utils as db
from app.logger import logger
from app.constants import WAITING_TRANSFER_ID, WAITING_PHOTO, WAITING_AMOUNT
from app.keyboards import kb_charge
from app.config import Config

ADMIN_ID = Config.ADMIN_ID

def msg_recharge(method: str, address: str) -> str:
    return f"🏦 **طريقة الشحن:** {method}\n\nأرسل إلى:\n`{address}`\n\nثم أرسل **صورة إثبات الدفع** وبعدها **المبلغ**."

async def start_recharge_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str, is_syriatel=False):
    """بدء عملية الشحن"""
    context.user_data['recharge_type'] = method
    if is_syriatel:
        context.user_data['recharge_step'] = WAITING_TRANSFER_ID
        await update.message.reply_text(M()['ask_transfer_id'], parse_mode='Markdown')
    else:
        context.user_data['recharge_step'] = WAITING_PHOTO
        address = db.get_recharge_address(method)
        await update.message.reply_text(msg_recharge(method, address), parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال صورة الشحن"""
    if context.user_data.get('recharge_step') != WAITING_PHOTO:
        return
    photo_file_id = update.message.photo[-1].file_id
    context.user_data['temp_photo'] = photo_file_id
    context.user_data['recharge_step'] = WAITING_AMOUNT
    await update.message.reply_text(M()['photo_sent'])
    await update.message.reply_text(M()['ask_amount'], parse_mode='Markdown')

async def send_recharge_request_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float,
                                         recharge_type: str, transfer_id=None, photo_file_id=None):
    """إرسال طلب الشحن للمدير"""
    req_id = db.next_recharge_id()
    user = update.effective_user
    try:
        db.insert_recharge_request({
            'id': req_id,
            'user_id': user.id,
            'username': user.username or str(user.id),
            'payment_type': recharge_type,
            'amount': amount,
            'status': 'pending',
            'photo_file_id': photo_file_id,
            'transfer_id': transfer_id
        })
    except Exception as e:
        logger.error(f"insert recharge error: {e}")
        await update.message.reply_text(M()['error'].format("حفظ الطلب بقاعدة البيانات"))
        return

    src_info = f"رقم العملية: `{transfer_id}`" if transfer_id else ("صورة إثبات مرفقة." if photo_file_id else "—")
    admin_msg = (
        f"🚨 **طلب شحن جديد (ID: {req_id})**\n\n"
        f"• المستخدم: @{user.username or user.id} (`{user.id}`)\n"
        f"• الطريقة: **{recharge_type}**\n"
        f"• المبلغ: **{amount}**\n"
        f"• الإثبات: {src_info}\n\n"
        "راجِع الطلب ثم اختر الإجراء:"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ موافقة", callback_data=f"req_approve_{req_id}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"req_reject_{req_id}")
    ]])

    try:
        if photo_file_id:
            await context.bot.send_photo(
                ADMIN_ID, photo=photo_file_id, caption=admin_msg,
                reply_markup=keyboard, parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(ADMIN_ID, admin_msg, reply_markup=keyboard, parse_mode='Markdown')
        await update.message.reply_text(M()['request_sent'].format(req_id), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"send to admin error: {e}")
        await update.message.reply_text(M()['error'].format("تعذّر إرسال الطلب للمدير"))
