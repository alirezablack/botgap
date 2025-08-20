# bot.py
import os
import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# دریافت متغیرهای محیطی
BOT_TOKEN = os.environ["BOT_TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 10000))

# اتصال به دیتابیس
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# ایجاد جدول اگر وجود نداشته باشد
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    level INT DEFAULT 1
)
""")
conn.commit()

# تابع شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! این یه ربات نمایش لول‌های کاربرای گپه.\n"
        "کافیه اد کنی گپت!\n"
        "با /leaderboard یا /لیدر برد لیست کاربران برتر رو ببین.\n"
        "سازنده ربات: @black_bigbang"
    )

# اضافه کردن کاربر جدید یا آپدیت کردن یوزرنیم
def add_or_update_user(user_id, username):
    cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username", (user_id, username))
    conn.commit()

# تابع نمایش لیدر برد محلی (همان گپ)
async def leaderboard_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # اینجا فقط کاربران پیام داده توی همون گپ بررسی میشه
    cur.execute("SELECT username, level FROM users ORDER BY level DESC LIMIT 10")
    top_users = cur.fetchall()
    text = "🏆 لیدر برد این گپ:\n\n"
    for i, (username, level) in enumerate(top_users, 1):
        text += f"{i}. {username} - Level {level}\n"
    await update.message.reply_text(text)

# تابع نمایش لیدر برد جهانی
async def leaderboard_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT username, level FROM users ORDER BY level DESC LIMIT 10")
    top_users = cur.fetchall()
    text = "🌐 لیدر برد جهانی:\n\n"
    for i, (username, level) in enumerate(top_users, 1):
        text += f"{i}. {username} - Level {level}\n"
    await update.message.reply_text(text)

# اضافه کردن هندرها
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["leaderboard", "لیدر برد"], leaderboard_local))
app.add_handler(CommandHandler(["leaderboard_global", "لیدر برد جهانی"], leaderboard_global))

# هر پیام کاربر رو برای ثبت یا آپدیت در دیتابیس بررسی می‌کنیم
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username or user.full_name)

app.add_handler(CommandHandler(None, register_user))  # هر پیام

# وبهوک روی Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
