import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9088330525:AAGSB9gSfCXRsbxL5grMc4dshfbr4cMFrK8" 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 أسعار الجواهر", callback_data="prices")],
        [InlineKeyboardButton("🔥 شحن فري فاير", callback_data="charge")],
        [InlineKeyboardButton("📞 تواصل معنا", callback_data="contact")],
    ]
    await update.message.reply_text("أهلاً بيك في TOP 1 🔥\nاختار من تحت:", reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "prices":
        await query.edit_message_text("💎 الأسعار:\n100 جوهرة = ...")
    elif query.data == "charge":
        await query.edit_message_text("🔥 للشحن ارسل ID حقك")
    elif query.data == "contact":
        await query.edit_message_text("📞 تواصل معنا: @top1_ff_bot")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()