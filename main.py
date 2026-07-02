import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@KliqaUpdates"
REGISTER_LINK = "https://kliqa.africa/sign-up?ref=6JM8DT"

# ======================
# CHECK JOIN
# ======================
async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except:
        return False

    return False


# ======================
# START COMMAND
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_joined(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/KliqaUpdates")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check")]
        ]

        await update.message.reply_text(
            "⚠️ You must join our channel before using this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("📱 Verify Number", callback_data="verify")],
        [InlineKeyboardButton("💰 Ways to Earn", callback_data="earn")]
    ]

    await update.message.reply_text(
        "👋 Welcome to Kliqa Guide Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ======================
# BUTTON HANDLER
# ======================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # verify
    if query.data == "verify":
        await query.edit_message_text(
            "📱 VERIFY NUMBER\n\n"
            "1. Login to Kliqa\n"
            "2. Go to Dashboard\n"
            "3. Click Verify Number\n"
            "4. Enter code sent to email"
        )

    # earn
    elif query.data == "earn":
        await query.edit_message_text(
            "💰 WAYS TO EARN\n\n"
            "• Daily Clicks\n"
            "• Read Articles\n"
            "• Complete Surveys\n"
            "• Listen to Music"
        )

    # check join
    elif query.data == "check":
        if await check_joined(update, context):
            await query.edit_message_text("✅ Verified! Now send /start again.")
        else:
            await query.answer("❌ You haven't joined yet!", show_alert=True)


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
