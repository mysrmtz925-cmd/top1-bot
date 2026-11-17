import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز"
ADMIN_ID = 7269956912

PACKAGES = {
    "id_gems": [
        ("100 جوهرة - 12,500", "100 جوهرة", "12,500 جنيه", "id"),
        ("العضوية الأسبوعية - 30,000", "العضوية الأسبوعية", "30,000 جنيه", "id"),
    ],
    "id_level": [
        ("مستوى 6 - 7,500", "Level Up - مستوى 6", "7,500 جنيه", "id"),
        ("مستوى 10 - 9,000", "Level Up - مستوى 10", "9,000 جنيه", "id"),
        ("مستوى 15 - 9,000", "Level Up - مستوى 15", "9,000 جنيه", "id"),
        ("مستوى 20 - 9,000", "Level Up - مستوى 20", "9,000 جنيه", "id"),
        ("مستوى 25 - 9,000", "Level Up - مستوى 25", "9,000 جنيه", "id"),
        ("مستوى 30 - 13,500", "Level Up - مستوى 30", "13,500 جنيه", "id"),
    ],
    "acc_gems": [
        ("100 جوهرة - 11,500", "100 جوهرة عبر الحساب", "11,500 جنيه", "account"),
    ],
    "acc_level": [
        ("مستوى 6 - 7,000", "Level Up مستوى 6 عبر الحساب", "7,000 جنيه", "account"),
        ("مستوى 10 - 8,000", "Level Up مستوى 10 عبر الحساب", "8,000 جنيه", "account"),
        ("مستوى 15 - 8,000", "Level Up مستوى 15 عبر الحساب", "8,000 جنيه", "account"),
        ("مستوى 20 - 8,000", "Level Up مستوى 20 عبر الحساب", "8,000 جنيه", "account"),
        ("مستوى 25 - 8,000", "Level Up مستوى 25 عبر الحساب", "8,000 جنيه", "account"),
        ("مستوى 30 - 11,000", "Level Up مستوى 30 عبر الحساب", "11,000 جنيه", "account"),
    ],
    "airdrop": [
        ("انزال 1$ - 13,000", "انزال جوي 1$", "13,000 جنيه", "id"),
        ("انزال 2$ - 26,000", "انزال جوي 2$", "26,000 جنيه", "id"),
    ],
}

CATEGORY_NAMES = {
    "id_gems": "شحن جواهر وعضويات - عبر ID",
    "id_level": "Level Up Pass - عبر ID",
    "acc_gems": "شحن جواهر - عبر الحساب ارخص",
    "acc_level": "Level Up Pass - عبر الحساب ارخص",
    "airdrop": "انزالات جوية - Airdrop",
}

user_state = {}

def main_menu():
    kb = [
        [InlineKeyboardButton("شحن جواهر وعضويات - ID", callback_data="cat_id_gems")],
        [InlineKeyboardButton("Level Up Pass - ID", callback_data="cat_id_level")],
        [InlineKeyboardButton("شحن عبر الحساب - ارخص", callback_data="cat_acc_gems")],
        [InlineKeyboardButton("Level Up عبر الحساب - ارخص", callback_data="cat_acc_level")],
        [InlineKeyboardButton("انزالات جوية", callback_data="cat_airdrop")],
        [InlineKeyboardButton("تواصل معنا", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(kb)

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="main")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "متجرك المضمون لشحن فري فاير\nشحن سريع | آمن 100%\n\nاختر نوع الشحن:"
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

    if data == "contact":
        await q.edit_message_text("للتواصل والاستفسار راسلنا هنا، وحنرد عليك في اسرع وقت.", reply_markup=back_to_main())
        return

    if data.startswith("cat_"):
        cat = data[4:]
        kb = []
        for i, item in enumerate(PACKAGES[cat]):
            btn_text = item[0]
            kb.append([InlineKeyboardButton(btn_text, callback_data="item_" + cat + "_" + str(i))])
        kb.append([InlineKeyboardButton("رجوع", callback_data="main")])
        await q.edit_message_text(CATEGORY_NAMES[cat] + "\n\nاختر الباقة:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("item_"):
        parts = data.split("_")
        cat = parts[1] + "_" + parts[2]
        idx = int(parts[3])
        item = PACKAGES[cat][idx]
        name = item[1]
        price = item[2]
        method = item[3]
        user_state[user_id] = {"name": name, "price": price, "method": method}
        kb = [
            [InlineKeyboardButton("اطلب الآن", callback_data="order_now")],
            [InlineKeyboardButton("رجوع", callback_data="cat_" + cat)],
        ]
        txt = name + "\n\nالسعر: " + price + "\n\nالدفع عبر بنكك\nالتسليم في دقائق"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولا", reply_markup=back_to_main())
            return
        method = order["method"]
        txt = "طلبك: " + order["name"] + "\n"
        txt = txt + "السعر: " + order["price"] + "\n\n"
        txt = txt + "حول القروش على بنكك:\n"
        txt = txt + "رقم الحساب: " + BANKK_NUMBER + "\n"
        txt = txt + "الاسم: " + BANKK_NAME + "\n\n"
        if method == "id":
            txt = txt + "بعد التحويل، رسل لينا في رسالة واحدة:\n"
            txt = txt + "1- صورة اشعار التحويل\n"
            txt = txt + "2- الـ ID حقك في اللعبة\n\n"
            txt = txt + "مثال:\nID: 123456789"
        else:
            txt = txt + "بعد التحويل، رسل لينا في رسالة واحدة:\n"
            txt = txt + "1- صورة اشعار التحويل\n"
            txt = txt + "2- ايميل حساب فري فاير\n"
            txt = txt + "3- كلمة سر الحساب\n"
            txt = txt + "4- الـ ID حقك لو موجود\n\n"
            txt = txt + "مثال:\nالايميل: xxx@gmail.com\nكلمة السر: xxxx\nID: 123456789"
        txt = txt + "\n\nرسل المعلومات هسي، وحنأكد ليك الطلب."
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
    header = "طلب جديد!\n\n"
    header = header + "الزبون: " + user.first_name + "\n"
    header = header + "يوزر التليجرام: " + str(user_id) + "\n"
    header = header + "الباقة: " + order["name"] + "\n"
    header = header + "السعر: " + order["price"] + "\n"
    if order["method"] == "id":
        header = header + "الطريقة: عبر ID\n\n"
    else:
        header = header + "الطريقة: عبر الحساب\n\n"
    header = header + "بيانات الزبون:\n"
    user_state[user_id]["waiting"] = False
    try:
        if update.message.photo:
            caption = header + (update.message.caption or "صورة اشعار بدون نص")
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption)
        else:
            txt = header + update.message.text
            await context.bot.send_message(chat_id=ADMIN_ID, text=txt)
        await update.message.reply_text("تم استلام طلبك! حنراجع التحويل ونشحن ليك في دقائق. شكرا لثقتك فينا")
    except Exception as e:
        print(e)
        await update.message.reply_text("تم استلام طلبك! حنراجع ونشحن ليك.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
