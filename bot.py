import os
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# اتصال به دیتابیس
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    level INT DEFAULT 1,
    chat_id BIGINT
)
""")
conn.commit()

def add_or_update_user(user_id, username, chat_id):
    cur.execute("""
    INSERT INTO users (user_id, username, chat_id)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username, chat_id = EXCLUDED.chat_id
    """, (user_id, username, chat_id))
    conn.commit()

def get_leaderboard(global_board=False, chat_id=None, limit=10):
    if global_board:
        cur.execute("SELECT username, level FROM users ORDER BY level DESC LIMIT %s", (limit,))
    else:
        cur.execute("SELECT username, level FROM users WHERE chat_id=%s ORDER BY level DESC LIMIT %s", (chat_id, limit))
    return cur.fetchall()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat.id
    text = update.message.text.strip()

    add_or_update_user(user.id, user.username or user.full_name, chat_id)

    if text == "لیدر برد جهانی":
        top = get_leaderboard(global_board=True)
        msg = "🌍 ۱۰ نفر اول جهانی:\n" + "\n".join([f"{i+1}. {u[0]} - lvl {u[1]}" for i,u in enumerate(top)])
        await update.message.reply_text(msg)
    elif text == "لیدر برد":
        top = get_leaderboard(chat_id=chat_id)
        msg = "🏠 ۱۰ نفر اول این گپ:\n" + "\n".join([f"{i+1}. {u[0]} - lvl {u[1]}" for i,u in enumerate(top)])
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("پیام شما ثبت شد ✅")

# راه‌اندازی بات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()

