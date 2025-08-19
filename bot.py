from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import sqlite3

# 🔑 توکن رباتتو اینجا بزار
TOKEN = "7981388986:AAE3xI26bTu7WJjTa9vx_svYrfVHbqBE4RU"

# 📦 دیتابیس برای ذخیره پیام‌ها
conn = sqlite3.connect("levels.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER,
    user_id INTEGER,
    username TEXT,
    messages INTEGER,
    PRIMARY KEY (chat_id, user_id)
)
""")
conn.commit()

# 🎯 شمارش پیام و لول آپ
async def level_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name

    # گرفتن تعداد پیام‌ها
    cursor.execute("SELECT messages FROM users WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    row = cursor.fetchone()

    if row:
        messages = row[0] + 1
        cursor.execute(
            "UPDATE users SET messages=?, username=? WHERE chat_id=? AND user_id=?",
            (messages, username, chat_id, user_id)
        )
    else:
        messages = 1
        cursor.execute(
            "INSERT INTO users (chat_id, user_id, username, messages) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, username, messages)
        )
    conn.commit()

    # چک کردن لول
    if messages % 10 == 0:
        level = messages // 10
        text = (
            f"🚀💥 بــــــــــوم!\n"
            f"🎉 تبرییییک بهت @{username}\n\n"
            f"🔥 تو به لول {level} رسیدی!\n"
            f"😎 برو جلو قهرمان 💪"
        )
        await update.message.reply_text(text)

# 🏆 دستور لیدربرد
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    cursor.execute(
        "SELECT username, messages FROM users WHERE chat_id=? ORDER BY messages DESC LIMIT 10",
        (chat_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("📭 هنوز کسی تو این گپ فعالیت نکرده!")
        return

    text = "👑🏆 لیدربرد تاپ 10 بازیکن گپ 🏆👑\n⚡ اینا غولای چت هستن ⚡\n\n"
    for i, (username, messages) in enumerate(rows, start=1):
        level = messages // 10
        text += f"{i}. ✨ @{username} → 🌟 لول {level}\n"

    await update.message.reply_text(text)

# 🚀 ران کردن ربات
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, level_system))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(MessageHandler(filters.Regex("(?i)لیدربرد"), leaderboard))
    print("🤖 ربات روشن شد و آماده ترکوندن گپ‌هاست!")
    app.run_polling()
