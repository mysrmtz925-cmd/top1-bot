import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر"
ADMIN_ID = 7269956912

PACKAGES = {
    "id_gems": [
        ("100 جوهرة - 12,500", "100 جوهرة", "12,500 جنيه", "id"),
        ("30,000 - العضوية الأسبوعية", "العضوية الأسبوعية", "30,000 جنيه", "id"),
    ],
    "id_level": [
        ("7,500 - Level Up - 6 مستوى", "Level Up - 6 مستوى", "7,500 جنيه", "id"),
        ("9,000 - Level Up - 10 مستوى", "Level Up - 10 مستوى", "9,000 جنيه", "id"),
        ("9,000 - Level Up - 15 مستوى", "Level Up - 15 مستوى", "9,000 جنيه", "id"),
        ("9,000 - Level Up - 20 مستوى", "Level Up - 20 مستوى", "9,000 جنيه", "id"),
        ("9,000 - Level Up - 25 مستوى", "Level Up - 25 مستوى", "9,000 جنيه", "id"),
        ("13,500 - Level Up - 30 مستوى", "Level Up - 30 مستوى", "13,500 جنيه", "id"),
    ],
    "acc_gems": [
        ("100 جوهرة عبر الحساب - 11,500", "100 جوهرة عبر الحساب", "11,500 جنيه", "acc"),
    ],
    "acc_level": [
        ("7,000 - Level Up عبر الحساب - 6 مستوى", "Level Up عبر الحساب - 6 مستوى", "7,000 جنيه", "acc"),
        ("8,000 - Level Up عبر الحساب - 10 مستوى", "Level Up عبر الحساب - 10 مستوى", "8,000 جنيه", "acc"),
        ("8,000 - Level Up عبر الحساب - 15 مستوى", "Level Up عبر الحساب - 15 مستوى", "8,000 جنيه", "acc"),
        ("8,000 - Level Up عبر الحساب - 20 مستوى", "Level Up عبر الحساب - 20 مستوى", "8,000 جنيه", "acc"),
        ("8,000 - Level Up عبر الحساب - 25 مستوى", "Level Up عبر الحساب - 25 مستوى", "8,000 جنيه", "acc"),
        ("11,000 - Level Up عبر الحساب - 30 مستوى", "Level Up عبر الحساب - 30 مستوى", "11,000 جنيه", "acc"),
    ],
    "airdrop": [
        ("انزال $1 - 13,000", "انزال جوي $1", "13,000 جنيه", "id"),
        ("انزال $2 - 26,000", "انزال جوي $2", "26,000 جنيه", "id"),
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
        [InlineKeyboardButton("تواصل معنا", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(kb)

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("الرئيسية", callback_data="main")]])

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

    if data == "contact":
        await q.edit_message_text("راسلنا هنا وسنرد عليك في أسرع وقت", reply_markup=back_to_main())
        return

    if data.startswith("cat_"):
        cat = data[4:]
        kb = []
        for i, item in enumerate(PACKAGES[cat]):
            btn_text = item[0]
            kb.append([InlineKeyboardButton(btn_text, callback_data="item_" + cat + "_" + str(i))])
        kb.append([InlineKeyboardButton("رجوع", callback_data="main")])
        await q.edit_message_text(CATEGORY_NAMES[cat], reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("item_"):
        # الحل هنا: نفصل اخر رقم هو الـ idx والباقي هو اسم التصنيف
        # ده بيشتغل مع id_gems ومع airdrop الاتنين
        rest = data[5:]
        idx = int(rest.rsplit("_", 1)[-1])
        cat = rest.rsplit("_", 1)[0]
        item = PACKAGES[cat][idx]
        name = item[1]
        price = item[2]
        method = item[3]
        user_state[user_id] = {"name": name, "price": price, "method": method}
        kb = [
            [InlineKeyboardButton("اطلب الان", callback_data="order_now")],
            [InlineKeyboardButton("رجوع", callback_data="cat_" + cat)],
        ]
        txt = name + "\nالسعر: " + price + "\nالتسليم: في غضون دقائق"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu())
            return
        method = order["method"]
        txt = "طلبك: " + order["name"] + "\n"
        txt = txt + "السعر: " + order["price"] + "\n\n"
        txt = txt + "حول على بنكك:\n"
        txt = txt + "بنكك: " + BANKK_NUMBER + "\n"
        txt = txt + "الاسم: " + BANKK_NAME + "\n\n"
        if method == "id":
            txt = txt + "بعد التحويل رسل لينا في رسالة واحدة:\n"
            txt = txt + "1- صورة اشعار التحويل\n"
            txt = txt + "2- الـ ID حقك\n"
            txt = txt + "مثال: ID: 123456789"
        else:
            txt = txt + "بعد التحويل رسل لينا في رسالة واحدة:\n"
            txt = txt + "1- صورة اشعار التحويل\n"
            txt = txt + "2- ايميل حسابك\n"
            txt = txt + "3- كلمة السر\n"
            txt = txt + "4- ال ID لو موجود\n"
            txt = txt + "مثال:\nالايميل: xxx@gmail.com\nكلمة السر: xxx\nال ID: xxx"
        txt = txt + "\n\nرسل المعلومات هسي و حنجهز ليك الطلب."
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

    header = "طلب جديد!\n"
    header = header + "الزبون: " + user.first_name + "\n"
    header = header + "يوزر التليجرام: " + str(user_id) + "\n"
    header = header + "الباقة: " + order["name"] + "\n"
    header = header + "السعر: " + order["price"] + "\n"
    if order["method"] == "id":
        header = header + "الطريقة: عبر ID\n"
    else:
        header = header + "الطريقة: عبر الحساب\n"
    header = header + "بيانات الزبون:\n"

    try:
        if update.message.photo:
            caption = update.message.caption or ""
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار + نص: " + caption)
            await update.message.reply_text("وصلت صورة الاشعار ✅\nهسي رسل الـ ID حقك في رسالة براهو")
            # هنا ما بنقفل الانتظار، عشان الـ ID لسه ما وصل
            return
        else:
            txt = header + update.message.text
            await context.bot.send_message(chat_id=ADMIN_ID, text=txt)
            await update.message.reply_text("تم استلام طلبك! حنراجع التحويل ونشحن ليك.")
            user_state[user_id]["waiting"] = False
    except Exception as e:
        print(e)
        await update.message.reply_text("حصل خطأ، حاول تاني")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
