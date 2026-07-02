import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

REGISTER_LINK = "https://kliqa.africa/sign-up?ref=6JM8DT"

DB_FILE = "db.json"


# ---------------- DATABASE ----------------
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
            "referred_by": None,
            "withdrawals": []
        }

    return db[user_id]


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)

    get_user(db, user_id)
    save_db(db)

    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dash")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "🔥 Welcome to Kliqa Earnings Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- BUTTONS ----------------
WAITING_WITHDRAW = {}

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    db = load_db()
    user = get_user(db, q.from_user.id)

    if q.data == "balance":
        await q.edit_message_text(f"💰 Balance: {user['balance']} KC")

    elif q.data == "dash":
        usd = user["balance"] / 100
        await q.edit_message_text(
            f"📊 DASHBOARD\n\n"
            f"💰 Balance: {user['balance']} KC\n"
            f"👥 Referrals: {user['referrals']}\n"
            f"💵 ${usd}"
        )

    elif q.data == "withdraw":
        WAITING_WITHDRAW[q.from_user.id] = True
        await q.edit_message_text("💸 Send withdrawal amount (min 100 KC)")


# ---------------- MESSAGE HANDLER ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = update.effective_user.id
    user = get_user(db, user_id)

    if user_id in WAITING_WITHDRAW:
        try:
            amount = int(update.message.text)

            if amount < 100:
                await update.message.reply_text("❌ Minimum withdrawal is 100 KC")
                return

            if amount > user["balance"]:
                await update.message.reply_text("❌ Insufficient balance")
                return

            user["balance"] -= amount

            user["withdrawals"].append({
                "amount": amount,
                "status": "pending",
                "time": time.time(),
                "process_at": time.time() + 6 * 3600
            })

            save_db(db)
            WAITING_WITHDRAW.pop(user_id)

            await update.message.reply_text(
                "✅ Withdrawal request submitted\n⏳ Processing: 6 hours"
            )

        except:
            await update.message.reply_text("❌ Send valid number")


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("message", handle_message))
    app.add_handler(CommandHandler("text", handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
