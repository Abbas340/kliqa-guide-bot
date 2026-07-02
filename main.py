import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

REGISTER_LINK = "https://kliqa.africa/sign-up?ref=6JM8DT"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Register", url=REGISTER_LINK)],
        [InlineKeyboardButton("📱 Verify Number", callback_data="verify")],
        [InlineKeyboardButton("💰 Ways to Earn", callback_data="earn")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to Kliqa Guide Bot 👇 Choose option:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "verify":
        await query.edit_message_text("Go to dashboard and verify your number.")

    elif query.data == "earn":
        await query.edit_message_text("Daily clicks, surveys, reading articles, music tasks.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()

# Railway redeploy
