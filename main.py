import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user(db, user_id):
    if str(user_id) not in db:
        db[str(user_id)] = {
            "balance": 0,
            "referrals": 0,
            "last_bonus": 0,
            "referred_by": None,
            "joined_channel": False
        }
    return db[str(user_id)]


# ======================
# CHECK JOIN
# ======================
async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = update.effective_user.id
    user = get_user(db, user_id)

    # referral system
    args = context.args
    if args and user["referred_by"] is None:
        ref_id = args[0]
        if ref_id != str(user_id):
            user["referred_by"] = ref_id
            if ref_id in db:
                db[ref_id]["balance"] += 10
                db[ref_id]["referrals"] += 1

    save_db(db)

    # force join
    if not await check_joined(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/KliqaUpdates")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check")]
        ]

        await update.message.reply_text(
            "⚠️ Join our channel to continue.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ]

    await update.message.reply_text(
        "👋 Welcome to Kliqa Bot",
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
# BUTTONS
# ======================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = load_db()
    user_id = str(query.from_user.id)
    user = get_user(db, user_id)

    give_daily_bonus(user)
    save_db(db)

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Your Balance: {user['balance']} KC\n"
            f"👥 Referrals: {user['referrals']}\n\n"
            "💵 100 KC = $1"
        )

    elif query.data == "check":
        if await check_joined(update, context):
            db[user_id]["joined_channel"] = True
            db[user_id]["balance"] += 10
            save_db(db)

            await query.edit_message_text("✅ You joined! +10 KC added. Send /start again.")
        else:
            await query.answer("❌ You haven't joined yet!", show_alert=True)


# ======================
# MAIN
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
