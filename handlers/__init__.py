
# app/handlers/__init__.py

from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from app.handlers.registration import (
    start, username_handler, password_handler, captcha_check, cancel
)
from app.handlers.buttons import button_handler, show_main_menu
from app.handlers.admin import admin_panel, admin_only_stats
from app.handlers.recharge import handle_photo
from app.handlers.callbacks import admin_approval_callback, phone_inline_callback
from app.constants import USERNAME_STATE, PASSWORD_STATE, CAPTCHA_STATE

def register_handlers(app):
    """تسجيل جميع الـ handlers في التطبيق."""
    # 1️⃣ محادثة التسجيل
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, username_handler)],
            PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
            CAPTCHA_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, captcha_check)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(reg_handler)

    # 2️⃣ أوامر عامة ومدير
    app.add_handler(CommandHandler("admin", admin_panel))

    # 3️⃣ الصور
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # 4️⃣ الردود النصية (أزرار)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    # 5️⃣ ردود الـ inline
    app.add_handler(CallbackQueryHandler(admin_approval_callback, pattern=r"^req_(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(phone_inline_callback, pattern=r"^(blacklist_|repurchase_)"))
