import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "@KliqaUpdates"
REGISTER_LINK = "https://kliqa.africa/sign-up?ref=6JM8DT"

DB_FILE = "data.json"


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


def get_user(db, user_id):
    user_id = str(user_id)

    if user_id not in db:
        db[user_id] = {
            "balance": 0,
            "referrals": 0,
            "last_bonus": 0,
            "referred_by": None,
            "joined": False
        }

    return db[user_id]


# ======================
# CHECK CHANNEL JOIN
# ======================
async def check_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ======================
# START COMMAND
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = update.effective_user.id
    user = get_user(db, user_id)

    # ======================
    # REFERRAL SYSTEM
    # ======================
    args = context.args
    if args and user["referred_by"] is None:
        ref_id = args[0]

        if ref_id != str(user_id):
            user["referred_by"] = ref_id

            if ref_id in db:
                db[ref_id]["balance"] += 10
                db[ref_id]["referrals"] += 1

    save_db(db)

    # ======================
    # JOIN CHECK
    # ======================
    joined = await check_joined(context, user_id)

    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "⚠️ You must join our channel to continue:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ======================
    # MAIN MENU
    # ======================
    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "👋 Welcome to Kliqa Bot\nEarn KC by inviting friends & daily bonuses 💰",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ======================
# DAILY BONUS
# ======================
def give_daily_bonus(user):
    now = int(time.time())

    if now - user["last_bonus"] >= 86400:
        user["balance"] += 2
        user["last_bonus"] = now


# ======================
# BUTTON HANDLER
# ======================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = load_db()
    user_id = str(query.from_user.id)
    user = get_user(db, user_id)

    give_daily_bonus(user)
    save_db(db)

    # ======================
    # BALANCE
    # ======================
    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Your Balance: {user['balance']} KC\n"
            f"👥 Referrals: {user['referrals']}\n\n"
            "💵 100 KC = $1"
        )

    # ======================
    # JOIN CHECK
    # ======================
    elif query.data == "check_join":
        joined = await check_joined(context, query.from_user.id)

        if joined:
            db[user_id]["joined"] = True
            db[user_id]["balance"] += 10
            save_db(db)

            await query.edit_message_text(
                "✅ Successfully joined!\n🎉 You received +10 KC\n\nSend /start again."
            )
        else:
            await query.answer("❌ You have not joined yet!", show_alert=True)

    # ======================
    # WITHDRAW (COMING SOON)
    # ======================
    elif query.data == "withdraw":
        await query.edit_message_text(
            "💸 Withdrawal System\n\n"
            "🚧 Status: COMING SOON\n\n"
            "We are building a secure withdrawal system.\n"
            "Please keep earning KC 💰"
        )


# ======================
# MAIN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
