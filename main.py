import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")
        def log_message(self, *args):
            pass
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()
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
