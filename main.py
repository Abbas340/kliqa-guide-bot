import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working 🚀")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()

import json
import os
DB_FILE = "db.json"
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)
        def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)
        def get_user(db, user_id):
    user_id = str(user_id)

    if user_id not in db:
        db[user_id] = {
            "balance": 0,
            "referrals": 0,
            "referred_by": None
        }

    return db[user_id]
    
