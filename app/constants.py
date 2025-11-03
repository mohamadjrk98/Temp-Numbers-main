# app/constants.py

# =========================
# 1) Conversation States
# =========================
USERNAME_STATE, PASSWORD_STATE, CAPTCHA_STATE = range(3)
WAITING_TRANSFER_ID = 11   # لسيرياتيل: ننتظر رقم العملية
WAITING_PHOTO = 12         # لباقي الطرق: ننتظر صورة الإشعار
WAITING_AMOUNT = 13        # في الحالتين ننتظر المبلغ لاحقاً

# =========================
# 2) Service → PID
# =========================
SERVICE_TO_PID = {
    "📧 Gmail 1": "0097",
    "📧 Gmail 2": "0098",
    "🪟 Microsoft": "0241",
    "💰 Swagbucks": "0652",
    "💌 InboxDollars": "1072",
    "📊 Ipsos": "2397",
    "🟢 ATTAPOL": "1998",
}
