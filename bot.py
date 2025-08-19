from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# توکن ربات مستقیم
TOKEN = "7981388986:AAE3xI26bTu7WJjTa9vx_svYrfVHbqBE4RU"  # ← اینو با توکن خودت عوض کن

# URL ربات روی Render
WEBHOOK_URL = f"https://my-levelup-bot.onrender.com/{TOKEN}"

# پورت Render
import os
PORT = int(os.environ.get("PORT", 5000))

# دیتابیس ساده لول ها
users = {}  # ساختار: {user_id: {"name": username, "xp": 0, "level": 1}}

LEVEL_XP = 10  # هر 10 پیام، لول آپ

# تابع برای لول آپ
def add_xp(user_id, username):
    if user_id not in users:
        users[user_id] = {"name": username, "xp": 0, "level": 1}
    users[user_id]["xp"] += 1
    if users[user_id]["xp"] >= LEVEL_XP:
        users[user_id]["level"] += 1
        users[user_id]["xp"] = 0
        return users[user_id]["level"]
    return None

# دستورات ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات Level Up فعال شد 😎")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await update.message.reply_text("🏆 هنوز کسی فعالیت نداشته!")
        return
    # مرتب سازی بر اساس level
    top_users = sorted(users.items(), key=lambda x: x[1]["level"], reverse=True)[:10]
    text = "🏆 لیدربرد ۱۰ نفر برتر:\n\n"
    for i, (uid, info) in enumerate(top_users, 1):
        text += f"{i}. {info['name']} - Level {info['level']}\n"
    await update.message.reply_text(text)

# شمارش پیام برای لول آپ
async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    new_level = add_xp(user.id, user.first_name)
    if new_level:
        await update.message.reply_text(f"🎉 تبریک {user.first_name}! شما لول {new_level} شدید! 🚀")

# ساخت اپلیکیشن
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_counter))

# Webhook
if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
