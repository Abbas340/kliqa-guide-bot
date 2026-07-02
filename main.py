
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

REGISTER_LINK = "https://kliqa.africa/sign-up?ref=6JM8DT"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("📱 Verify Number", callback_data="verify")],
        [InlineKeyboardButton("💰 Ways to Earn", callback_data="earn")],
    ]

    await update.message.reply_text(
        "👋 Welcome to Kliqa Guide Bot\n\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "verify":
        await query.edit_message_text(
            "📱 Verify Number\n\n"
            "1. Login to Kliqa\n"
            "2. Click Verify Number\n"
            "3. Enter your phone number\n"
            "4. Check your email for the code\n"
            "5. Enter the code to verify."
        )

    elif query.data == "earn":
        await query.edit_message_text(
            "💰 Ways to Earn\n\n"
            "• Daily Clicks\n"
            "• Read Articles\n"
            "• Complete Surveys\n"
            "• Listen to Music"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
