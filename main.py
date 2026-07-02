import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

REGISTER_LINK = "https://example.com/register?ref=6JM8DT"
DB_FILE = "hub_data.json"


# ======================
# DATABASE
# ======================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


def user_init(db, user_id):
    user_id = str(user_id)

    if user_id not in db:
        db[user_id] = {
            "balance": 0,
            "referrals": 0,
            "last_bonus": 0,
            "referred_by": None
        }

    return db[user_id]


# ======================
# DAILY BONUS
# ======================
def daily_bonus(user):
    now = int(time.time())

    if now - user["last_bonus"] >= 86400:
        user["balance"] += 2
        user["last_bonus"] = now


# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = update.effective_user.id
    user = user_init(db, user_id)

    # referral system
    args = context.args
    if args and user["referred_by"] is None:
        ref = args[0]

        if ref != str(user_id):
            user["referred_by"] = ref
            if ref in db:
                db[ref]["balance"] += 10
                db[ref]["referrals"] += 1

    save_db(db)

    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "🚀 Welcome to Earnings Hub System\nEarn KC by tasks & referrals 💰",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ======================
# BUTTONS
# ======================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = load_db()
    user_id = str(query.from_user.id)
    user = user_init(db, user_id)

    daily_bonus(user)
    save_db(db)

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Balance: {user['balance']} KC\n"
            f"👥 Referrals: {user['referrals']}\n\n"
            "💵 Rate: 100 KC = $1"
        )

    elif query.data == "withdraw":
        await query.edit_message_text(
            "💸 Withdraw System\n\n"
            "🚧 Coming Soon...\n\n"
            "✔ Minimum: 1000 KC\n"
            "✔ Method: Crypto / Bank / Wallet\n"
        )


# ======================
# RUN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Earnings Hub Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
