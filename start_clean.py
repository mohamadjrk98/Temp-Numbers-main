import os
import shutil
import telegram

print(f"📦 Detected telegram version: {telegram.__version__}")
print(f"📂 Telegram path: {telegram.__file__}")

# حذف بقايا الإصدارات القديمة إن وُجدت
venv_path = "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram"
if os.path.exists(venv_path):
    print("🧹 Removing old telegram directory...")
    try:
        shutil.rmtree(venv_path)
        print("✅ Old telegram directory removed successfully.")
    except Exception as e:
        print("⚠️ Could not remove old telegram directory:", e)

# إعادة التثبيت السريع
print("🔄 Reinstalling python-telegram-bot...")
os.system("pip install --force-reinstall --no-cache-dir python-telegram-bot==20.7")

# تشغيل البوت
print("🚀 Starting main bot...")
os.system("python main.py")
