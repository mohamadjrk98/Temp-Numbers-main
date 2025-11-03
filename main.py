import os
import sys
import logging
import telegram
print(f"📦 telegram version: {telegram.__version__}")
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

# ✅ التأكد من إمكانية استيراد مجلد app حتى لو شُغل من مكان مختلف
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ استيراد الإعدادات والمكونات
from app.config import BOT_TOKEN, ADMIN_ID, logger
from app.handlers import registration, recharge, callback, buttons, admin

# =====================================================
# تسجيل جميع الـ Handlers في التطبيق
# =====================================================
def register_handlers(app: Application):
    # محادثة التسجيل
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("start", registration.start)],
        states={
            registration.USERNAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration.username_handler)],
            registration.PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration.password_handler)],
            registration.CAPTCHA_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration.captcha_check)],
        },
        fallbacks=[CommandHandler("cancel", registration.cancel)],
    )
    app.add_handler(reg_handler)

    # أوامر الأدمن
    app.add_handler(CommandHandler("admin", admin.admin_panel))

    # الكولباك (الموافقات والرفض)
    app.add_handler(CallbackQueryHandler(callback.admin_approval_callback, pattern="^req_(approve|reject)_"))

    # استقبال الصور أثناء عملية الشحن
    app.add_handler(MessageHandler(filters.PHOTO, recharge.handle_photo))

    # الأزرار والنصوص العامة
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons.button_handler))

    # معالجة الأخطاء
    app.add_error_handler(callback.error_handler)

# =====================================================
# تشغيل البوت
# =====================================================
def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود في ملف البيئة (.env)")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # تسجيل جميع الهاندلرز
    register_handlers(app)

    # إعداد الـ webhook أو التشغيل العادي
    PORT = int(os.getenv("PORT", 10000))
    HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

    if HOSTNAME:
        WEBHOOK_URL = f"https://{HOSTNAME}/{BOT_TOKEN}"
        app.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"🌐 Webhook set: {WEBHOOK_URL}")

        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=WEBHOOK_URL
        )
    else:
        logger.info("🚀 Running bot in polling mode (local).")
        app.run_polling()

# =====================================================
# نقطة الدخول الرئيسية
# =====================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
