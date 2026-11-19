import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("9088330525:AAGSB9gSfCXRsbxL5grMc4dshfbr4cMFrK8")
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز"
ADMIN_ID = 7269956912

PACKAGES = {
    "id_gems": [
        ("100💎 - 12,000", "100 جوهرة", "12,000 جنيه", "id"),
        ("200💎 - 24,000", "200 جوهرة", "24,000 جنيه", "id"),
        ("500💎 - 60,000", "500 جوهرة", "60,000 جنيه", "id"),
        ("28,000 - العضوية الأسبوعية", "العضوية الأسبوعية", "28,000 جنيه", "id"),
    ],
    "id_level": [
        ("7,000 - Level Up - 6 مستوى", "Level Up - 6 مستوى", "7,000 جنيه", "id"),
        ("8,500 - Level Up - 10 مستوى", "Level Up - 10 مستوى", "8,500 جنيه", "id"),
        ("8,500 - Level Up - 15 مستوى", "Level Up - 15 مستوى", "8,500 جنيه", "id"),
        ("8,500 - Level Up - 20 مستوى", "Level Up - 20 مستوى", "8,500 جنيه", "id"),
        ("8,500 - Level Up - 25 مستوى", "Level Up - 25 مستوى", "8,500 جنيه", "id"),
        ("13,000 - Level Up - 30 مستوى", "Level Up - 30 مستوى", "13,000 جنيه", "id"),
    ],
    "acc_gems": [
        ("100💎 عبر الحساب - 11,000", "100 جوهرة عبر الحساب", "11,000 جنيه", "acc"),
        ("200💎 عبر الحساب - 22,000", "200 جوهرة عبر الحساب", "22,000 جنيه", "acc"),
        ("500💎 عبر الحساب - 55,000", "500 جوهرة عبر الحساب", "55,000 جنيه", "acc"),
    ],
    "acc_level": [
        ("6,500 - Level Up عبر الحساب - 6 مستوى", "Level Up عبر الحساب - 6 مستوى", "6,500 جنيه", "acc"),
        ("7,500 - Level Up عبر الحساب - 10 مستوى", "Level Up عبر الحساب - 10 مستوى", "7,500 جنيه", "acc"),
        ("7,500 - Level Up عبر الحساب - 15 مستوى", "Level Up عبر الحساب - 15 مستوى", "7,500 جنيه", "acc"),
        ("7,500 - Level Up عبر الحساب - 20 مستوى", "Level Up عبر الحساب - 20 مستوى", "7,500 جنيه", "acc"),
        ("7,500 - Level Up عبر الحساب - 25 مستوى", "Level Up عبر الحساب - 25 مستوى", "7,500 جنيه", "acc"),
        ("10,500 - Level Up عبر الحساب - 30 مستوى", "Level Up عبر الحساب - 30 مستوى", "10,500 جنيه", "acc"),
    ],
    "airdrop": [
        ("انزال $1 - 12,500", "انزال جوي $1", "12,500 جنيه", "id"),
        ("انزال $2 - 25,000", "انزال جوي $2", "25,000 جنيه", "id"),
    ],
}

CATEGORY_NAMES = {
    "id_gems": "شحن جواهر وعملات - ID",
    "id_level": "Level Up Pass - ID",
    "acc_gems": "شحن جواهر عبر الحساب",
    "acc_level": "Level Up Pass - عبر الحساب",
    "airdrop": "انزالات جوية - Airdrop",
}

user_state = {}

def main_menu():
    kb = [
        [InlineKeyboardButton("شحن جواهر وعملات - ID", callback_data="cat_id_gems")],
        [InlineKeyboardButton("Level Up Pass - ID", callback_data="cat_id_level")],
        [InlineKeyboardButton("شحن عبر الحساب - جواهر", callback_data="cat_acc_gems")],
        [InlineKeyboardButton("Level Up - عبر الحساب", callback_data="cat_acc_level")],
        [InlineKeyboardButton("انزالات جوية - Airdrop", callback_data="cat_airdrop")],
        [InlineKeyboardButton("📞 التواصل والدعم", url="https://t.me/TOP1MOYASAR")],
    ]
    return InlineKeyboardMarkup(kb)

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("الرئيسية", callback_data="main")]])

def admin_keyboard(user_id):
    kb = [
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}")],
        [InlineKeyboardButton("❌ فشل الطلب وتم إرجاع المبلغ", callback_data=f"fail_{user_id}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}")],
        [InlineKeyboardButton("🚫 غير متوفر", callback_data=f"unavail_{user_id}")],
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "اهلا بيك في TOP 1 👑\nاختار من القائمة:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    if data == "main":
        await start(update, context)
        return
    if data.startswith("cat_"):
        cat = data[4:]
        kb = []
        for i, item in enumerate(PACKAGES[cat]):
            kb.append([InlineKeyboardButton(item[0], callback_data="item_" + cat + "_" + str(i))])
        kb.append([InlineKeyboardButton("رجوع", callback_data="main")])
        await q.edit_message_text(CATEGORY_NAMES[cat], reply_markup=InlineKeyboardMarkup(kb))
        return
    if data.startswith("item_"):
        rest = data[5:]
        idx = int(rest.rsplit("_", 1)[-1])
        cat = rest.rsplit("_", 1)[0]
        item = PACKAGES[cat][idx]
        user_state[user_id] = {"name": item[1], "price": item[2], "method": item[3]}
        kb = [[InlineKeyboardButton("اطلب الان", callback_data="order_now")],[InlineKeyboardButton("رجوع", callback_data="cat_" + cat)]]
        await q.edit_message_text(item[1] + "\nالسعر: " + item[2] + "\nالتسليم: في غضون دقائق", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu())
            return
        method = order["method"]
        txt = "طلبك: " + order["name"] + "\nالسعر: " + order["price"] + "\n\nحول على بنكك:\nبنكك: " + BANKK_NUMBER + "\nالاسم: " + BANKK_NAME + "\n\n"
        if method == "id":
            txt += "بعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- الـ ID حقك\nمثال: ID: 123456789"
        else:
            txt += "بعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- ايميل حسابك\n3- كلمة السر\n4- ال ID لو موجود\nمثال:\nالايميل: xxx@gmail.com\nكلمة السر: xxx\nال ID: xxx"
        txt += "\n\nرسل المعلومات هسي و حنجهز ليك الطلب."
        user_state[user_id]["waiting"] = True
        await q.edit_message_text(txt, reply_markup=back_to_main())
        return

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    order = user_state.get(user_id)
    if not order or not order.get("waiting"):
        await update.message.reply_text("اهلا بيك اختار من القائمة /start")
        return
    header = "طلب جديد!\nالزبون: " + user.first_name + "\nيوزر التليجرام: " + str(user_id) + "\nالباقة: " + order["name"] + "\nالسعر: " + order["price"] + "\n"
    header += "الطريقة: عبر ID\n" if order["method"] == "id" else "الطريقة: عبر الحساب\n"
    header += "بيانات الزبون:\n"
    try:
        if update.message.photo:
            caption = update.message.caption or ""
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار + نص: " + caption, reply_markup=admin_keyboard(user_id))
            await update.message.reply_text("وصلت صورة الاشعار ✅\nهسي رسل الـ ID حقك في رسالة براهو")
            return
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=header + update.message.text, reply_markup=admin_keyboard(user_id))
            await update.message.reply_text("تم استلام طلبك! حنراجع التحويل ونشحن ليك.")
            user_state[user_id]["waiting"] = False
    except Exception as e:
        print(e)
        await update.message.reply_text("حصل خطأ، حاول تاني")

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action, user_id = q.data.rsplit("_", 1)
    user_id = int(user_id)
    if action == "done":
        msg = "تم ✅ تم شحن طلبك بنجاح، شكراً ليك ❤️"
        suffix = "\n\n✅ تم التنفيذ"
    elif action == "fail":
        msg = "عذراً ❌ فشل طلبك، وتم إرجاع المبلغ لحسابك. راسلنا لو ما وصلك."
        suffix = "\n\n❌ فشل وتم الإرجاع"
    elif action == "dup":
        msg = "تنبيه ⚠️ الإشعار ده مكرر، تم تجاهل الطلب المكرر."
        suffix = "\n\n⚠️ إشعار مكرر"
    elif action == "unavail":
        msg = "عذراً 🚫 الباقة دي غير متوفرة حالياً. حنرجع ليك المبلغ، أو اختار باقة تانية من القائمة."
        suffix = "\n\n🚫 غير متوفر"
    else:
        return
    await context.bot.send_message(user_id, msg)
    try:
        if q.message.photo:
            await q.edit_message_caption((q.message.caption or "") + suffix)
        else:
            await q.edit_message_text((q.message.text or "") + suffix)
    except Exception as e:
        print("edit error:", e)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup|unavail)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    # Fix for Python 3.14 - no current event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()


