import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8673670577  # <-- لو ده ما رقمك انت، غيرو برقمك

# ===== القوائم =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("💎 شحن جواهر", callback_data="gems")],
        [InlineKeyboardButton("🪂 انزالات جوية", callback_data="airdrops")],
        [InlineKeyboardButton("📞 التواصل والدعم", url="https://t.me/TOP1MOYASAR")],
    ]
    return InlineKeyboardMarkup(keyboard)

def gems_menu():
    keyboard = [
        [InlineKeyboardButton("100 جوهرة - 12,500 جنيه", callback_data="buy_gems_100")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="home")],
    ]
    return InlineKeyboardMarkup(keyboard)

def airdrop_menu():
    keyboard = [
        [InlineKeyboardButton("انزال 1$ - 13,000 جنيه", callback_data="buy_airdrop_1")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="home")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_home():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الرئيسية", callback_data="home")]])

# ===== البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("أهلاً بيك في TOP 1 🔥\nاختار الخدمة:", reply_markup=main_menu())
    else:
        await update.callback_query.edit_message_text("أهلاً بيك في TOP 1 🔥\nاختار الخدمة:", reply_markup=main_menu())

# ===== الأزرار =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "home":
        await query.edit_message_text("أهلاً بيك في TOP 1 🔥\nاختار الخدمة:", reply_markup=main_menu())
        return
    if data == "gems":
        await query.edit_message_text("اختار الباقة:", reply_markup=gems_menu())
        return
    if data == "airdrops":
        await query.edit_message_text("اختار الانزال:", reply_markup=airdrop_menu())
        return

    if data == "buy_gems_100":
        context.user_data["order"] = {"type": "gems", "name": "100 جوهرة", "price": "12,500 جنيه"}
        context.user_data["step"] = "waiting_info"
        await query.edit_message_text(
            "السعر: 12,500 جنيه\nحول على بنكك:\n8994176\nالاسم: ميسر\n\nبعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- إيميل حسابك\n3- كلمة السر\n4- الـ ID لو موجود\n\nمثال:\nالإيميل: xxx@gmail.com\nكلمة السر: xxx\nالـ ID: xxx\n\nرسل المعلومات هسي وحنجهز ليك الطلب.",
            reply_markup=back_home())
        return

    if data == "buy_airdrop_1":
        context.user_data["order"] = {"type": "airdrop", "name": "انزال 1$", "price": "13,000 جنيه"}
        context.user_data["step"] = "waiting_info"
        await query.edit_message_text(
            "السعر: 13,000 جنيه\nحول على بنكك:\n8994176\nالاسم: ميسر\n\nبعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- إيميل حسابك\n3- كلمة السر\n4- الـ ID لو موجود\n\nمثال:\nالإيميل: xxx@gmail.com\nكلمة السر: xxx\nالـ ID: xxx\n\nرسل المعلومات هسي وحنجهز ليك الطلب.",
            reply_markup=back_home())
        return

# ===== استلام معلومات الزبون =====
async def receive_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") != "waiting_info":
        await update.message.reply_text("دوس /start عشان تبدا طلب جديد.")
        return

    order = context.user_data.get("order", {})
    user = update.message.from_user
    info = update.message.text or "صورة اشعار + نص"
    user_id = user.id
    username = user.username or user.first_name

    # رسالة للزبون
    await update.message.reply_text("تم استلام طلبك! جاري التحويل والشحن ليك.", reply_markup=back_home())
    context.user_data.clear()

    # رسالة للأدمن مع 3 أزرار
    keyboard = [
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}")],
        [InlineKeyboardButton("❌ فشل الطلب وتم إرجاع المبلغ", callback_data=f"fail_{user_id}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_text = f"طلب جديد!\nالزبون: {username}\nيوزر التليجرام: {user_id}\nالباقة: {order.get('name')}\nالسعر: {order.get('price')}\nالطريقة: ID عبر\nبيانات الزبون:\n{info}"

    await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=reply_markup)

# ===== أزرار الأدمن - تم / فشل / مكرر =====
async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "done":
        await context.bot.send_message(user_id, "تم ✅ تم شحن طلبك بنجاح، شكراً ليك ❤️")
        await query.edit_message_text(query.message.text + "\n\n✅ تم التنفيذ")
    elif action == "fail":
        await context.bot.send_message(user_id, "عذراً ❌ فشل طلبك، وتم إرجاع المبلغ لحسابك. راسلنا لو ما وصلك.")
        await query.edit_message_text(query.message.text + "\n\n❌ فشل وتم الإرجاع")
    elif action == "dup":
        await context.bot.send_message(user_id, "تنبيه ⚠️ الإشعار ده مكرر، تم تجاهل الطلب المكرر.")
        await query.edit_message_text(query.message.text + "\n\n⚠️ إشعار مكرر")

# ===== التشغيل =====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_info))
    app.run_polling()

if __name__ == "__main__":
    main()
