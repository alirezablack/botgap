import os
import psycopg2
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DATABASE_URL")

# اتصال به دیتابیس
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# ساخت جدول اگه وجود نداشت
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id BIGINT,
    user_id BIGINT,
    username TEXT,
    level INT DEFAULT 0,
    PRIMARY KEY (chat_id, user_id)
)
""")
conn.commit()

# افزایش لول وقتی کسی پیام میده
def increase_level(update, context):
    user = update.effective_user
    chat = update.effective_chat

    cur.execute("""
        INSERT INTO users (chat_id, user_id, username, level)
        VALUES (%s, %s, %s, 1)
        ON CONFLICT (chat_id, user_id)
        DO UPDATE SET level = users.level + 1
    """, (chat.id, user.id, user.username or "بدون‌اسم"))
    conn.commit()

# لیدر برد فقط همون گروه
def leaderboard(update, context):
    chat = update.effective_chat
    cur.execute("SELECT username, level FROM users WHERE chat_id=%s ORDER BY level DESC LIMIT 10", (chat.id,))
    rows = cur.fetchall()

    text = "🏆 لیدربورد گروه:\n\n"
    for i, row in enumerate(rows, start=1):
        text += f"{i}. {row[0]} — {row[1]} لول\n"
    update.message.reply_text(text)

# لیدر برد جهانی (کل گروه‌ها)
def global_leaderboard(update, context):
    cur.execute("SELECT username, level FROM users ORDER BY level DESC LIMIT 10")
    rows = cur.fetchall()

    text = "🌍 لیدربورد جهانی:\n\n"
    for i, row in enumerate(rows, start=1):
        text += f"{i}. {row[0]} — {row[1]} لول\n"
    update.message.reply_text(text)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # افزایش لول با هر پیام
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, increase_level))

    # دستور انگلیسی
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(CommandHandler("global_leaderboard", global_leaderboard))

    # دستور فارسی
    dp.add_handler(MessageHandler(Filters.regex(r'^(لیدر برد)$'), leaderboard))
    dp.add_handler(MessageHandler(Filters.regex(r'^(لیدر برد جهانی)$'), global_leaderboard))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
