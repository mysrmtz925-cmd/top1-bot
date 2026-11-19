import os
import asyncio
import sqlite3
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز"
ADMIN_ID = 7269956912
DB = "wallet.db"

PACKAGES = {
    "id_gems": [
        ("100💎 - 12,000", "100 جوهرة", "12,000 جنيه", "id", 12000),
        ("200💎 - 24,000", "200 جوهرة", "24,000 جنيه", "id", 24000),
        ("500💎 - 60,000", "500 جوهرة", "60,000 جنيه", "id", 60000),
        ("28,000 - العضوية الأسبوعية", "العضوية الأسبوعية", "28,000 جنيه", "id", 28000),
    ],
    "id_level": [
        ("7,000 - Level Up - 6 مستوى", "Level Up - 6 مستوى", "7,000 جنيه", "id", 7000),
        ("8,500 - Level Up - 10 مستوى", "Level Up - 10 مستوى", "8,500 جنيه", "id", 8500),
        ("8,500 - Level Up - 15 مستوى", "Level Up - 15 مستوى", "8,500 جنيه", "id", 8500),
        ("8,500 - Level Up - 20 مستوى", "Level Up - 20 مستوى", "8,500 جنيه", "id", 8500),
        ("8,500 - Level Up - 25 مستوى", "Level Up - 25 مستوى", "8,500 جنيه", "id", 8500),
        ("13,000 - Level Up - 30 مستوى", "Level Up - 30 مستوى", "13,000 جنيه", "id", 13000),
    ],
    "acc_gems": [
        ("100💎 عبر الحساب - 11,000", "100 جوهرة عبر الحساب", "11,000 جنيه", "acc", 11000),
        ("200💎 عبر الحساب - 22,000", "200 جوهرة عبر الحساب", "22,000 جنيه", "acc", 22000),
        ("500💎 عبر الحساب - 55,000", "500 جوهرة عبر الحساب", "55,000 جنيه", "acc", 55000),
    ],
    "acc_level": [
        ("6,500 - Level Up عبر الحساب - 6 مستوى", "Level Up عبر الحساب - 6 مستوى", "6,500 جنيه", "acc", 6500),
        ("7,500 - Level Up عبر الحساب - 10 مستوى", "Level Up عبر الحساب - 10 مستوى", "7,500 جنيه", "acc", 7500),
        ("7,500 - Level Up عبر الحساب - 15 مستوى", "Level Up عبر الحساب - 15 مستوى", "7,500 جنيه", "acc", 7500),
        ("7,500 - Level Up عبر الحساب - 20 مستوى", "Level Up عبر الحساب - 20 مستوى", "7,500 جنيه", "acc", 7500),
        ("7,500 - Level Up عبر الحساب - 25 مستوى", "Level Up عبر الحساب - 25 مستوى", "7,500 جنيه", "acc", 7500),
        ("10,500 - Level Up عبر الحساب - 30 مستوى", "Level Up عبر الحساب - 30 مستوى", "10,500 جنيه", "acc", 10500),
    ],
    "airdrop": [
        ("انزال $1 - 12,500", "انزال جوي $1", "12,500 جنيه", "id", 12500),
        ("انزال $2 - 25,000", "انزال جوي $2", "25,000 جنيه", "id", 25000),
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

# ---------- Wallet DB ----------
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, balance INTEGER DEFAULT 0)")
    con.commit()
    con.close()

def ensure_user(user):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, balance) VALUES (?,?,?,0)", (user.id, user.username or "", user.first_name or ""))
    cur.execute("UPDATE users SET username=?, first_name=? WHERE user_id=?", (user.username or "", user.first_name or "", user.id))
    con.commit()
    con.close()

def get_balance(user_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else 0

def change_balance(user_id, amount):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    con.commit()
    con.close()
    return get_balance(user_id)

def get_all_users():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT user_id, username, first_name, balance FROM users ORDER BY balance DESC")
    rows = cur.fetchall()
    con.close()
    return rows

def parse_price(price_text):
    nums = re.findall(r'\d+', price_text.replace(",", ""))
    return int(nums[0]) if nums else 0

# ---------- Menus ----------
def main_menu(user_id=None):
    bal = get_balance(user_id) if user_id else 0
    kb = [
        [InlineKeyboardButton(f"💰 محفظتي : {bal:,} SDG", callback_data="my_wallet")],
        [InlineKeyboardButton("💳 تغذية محفظتي", callback_data="topup_start")],
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

def admin_keyboard(user_id, price_num=0):
    kb = [
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}_{price_num}")],
        [InlineKeyboardButton("❌ فشل الطلب وتم إرجاع المبلغ", callback_data=f"fail_{user_id}_{price_num}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}_{price_num}")],
        [InlineKeyboardButton("🚫 إشعار غير صحيح", callback_data=f"wrong_{user_id}_{price_num}")],
        [InlineKeyboardButton("🚫 غير متوفر", callback_data=f"unavail_{user_id}_{price_num}")],
    ]
    return InlineKeyboardMarkup(kb)

def topup_admin_keyboard(user_id, amount):
    kb = [
        [InlineKeyboardButton("✅ قبول وشحن المحفظة", callback_data=f"topup_yes_{user_id}_{amount}")],
        [InlineKeyboardButton("❌ رفض", callback_data=f"topup_no_{user_id}_{amount}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"topup_dup_{user_id}_{amount}")],
        [InlineKeyboardButton("🚫 إشعار غير صحيح", callback_data=f"topup_wrong_{user_id}_{amount}")],
    ]
    return InlineKeyboardMarkup(kb)

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user)
    bal = get_balance(user.id)
    text = f"اهلا بيك في TOP 1 👑\n💰 محفظتك: {bal:,} SDG\nاختار من القائمة:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu(user.id))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu(user.id))

async def wallet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user)
    bal = get_balance(user.id)
    await update.message.reply_text(f"💰 محفظتي\n\nرصيدك الحالي: {bal:,} SDG\n\nلشحن المحفظة دوس زر تغذية محفظتي من القائمة", reply_markup=back_to_main())

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_users()
    total = sum(u[3] for u in users)
    txt = f"📊 لوحة الأدمن - TOP 1\n\nعدد المستخدمين: {len(users)}\nإجمالي الأرصدة: {total:,} SDG\n\nآخر 10:\n"
    for u in users[:10]:
        txt += f"- {u[2]} (@{u[1]}) - {u[3]:,} SDG - ID: {u[0]}\n"
    txt += "\nأوامر:\n/balances - كل الأرصدة\n/add [ID] [المبلغ] - إضافة رصيد\n/deduct [ID] [المبلغ] - خصم رصيد"
    await update.message.reply_text(txt)

async def balances_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("لا يوجد مستخدمين بعد.")
        return
    txt = "💰 قائمة أرصدة العملاء\n\n"
    for i, u in enumerate(users, 1):
        txt += f"{i}. {u[2]} (@{u[1]}) - {u[3]:,} SDG - {u[0]}\n"
    txt += f"\nإجمالي: {sum(u[3] for u in users):,} SDG"
    for j in range(0, len(txt), 4000):
        await update.message.reply_text(txt[j:j+4000])

async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target = int(context.args[0])
        amount = int(context.args[1].replace(",", ""))
        ensure_user(type("obj", (), {"id": target, "username": "", "first_name": "User"})())
        new_bal = change_balance(target, amount)
        await update.message.reply_text(f"✅ تم إضافة {amount:,} SDG للمستخدم {target}\nرصيدو الجديد: {new_bal:,} SDG")
        try:
            await context.bot.send_message(target, f"✅ تم شحن محفظتك بـ {amount:,} SDG\nرصيدك الحالي: {new_bal:,} SDG")
        except:
            pass
    except:
        await update.message.reply_text("الاستخدام: /add [ID] [المبلغ]\nمثال: /add 123456 10000")

async def deduct_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target = int(context.args[0])
        amount = int(context.args[1].replace(",", ""))
        new_bal = change_balance(target, -amount)
        await update.message.reply_text(f"✅ تم خصم {amount:,} SDG من {target}\nرصيدو الجديد: {new_bal:,} SDG")
    except:
        await update.message.reply_text("الاستخدام: /deduct [ID] [المبلغ]")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    ensure_user(q.from_user)
    if data == "main":
        await start(update, context)
        return
    if data == "my_wallet":
        bal = get_balance(user_id)
        kb = [
            [InlineKeyboardButton("💳 تغذية محفظتي", callback_data="topup_start")],
            [InlineKeyboardButton("الرئيسية", callback_data="main")]
        ]
        await q.edit_message_text(f"💰 محفظتي\n\nرصيدك: {bal:,} SDG\n\nدوس تغذية عشان تشحن.", reply_markup=InlineKeyboardMarkup(kb))
        return

    # تغذية المحفظة - طلب المبلغ
    if data == "topup_start":
        user_state[user_id] = {"waiting_topup_amount": True}
        await q.edit_message_text("💳 تغذية محفظتي\n\nاكتب المبلغ الداير تشحن بيهو المحفظة\nمثال: 10000\n\nاكتبو في رسالة هسي:", reply_markup=back_to_main())
        return

    # أزرار الأدمن لتغذية المحفظة
    if data.startswith("topup_"):
        parts = data.rsplit("_", 2)
        sub = data.split("_")[1]
        target = int(parts[1]); amount = int(parts[2])
        if sub == "yes":
            new_bal = change_balance(target, amount)
            await context.bot.send_message(target, f"✅ تم قبول شحن محفظتك!\nتم إضافة {amount:,} SDG\nرصيدك الحالي: {new_bal:,} SDG")
            suffix = f"\n\n✅ تم الشحن - {amount:,} SDG"
        elif sub == "no":
            await context.bot.send_message(target, f"❌ تم رفض طلب شحن المحفظة {amount:,} SDG. راسلنا للتأكد.")
            suffix = "\n\n❌ تم الرفض"
        elif sub == "dup":
            await context.bot.send_message(target, "⚠️ الإشعار ده مكرر، انت رسلت الاشعار ده قبل كدا. لو عندك اشعار جديد رسلو.")
            suffix = "\n\n⚠️ إشعار مكرر"
        elif sub == "wrong":
            await context.bot.send_message(target, "🚫 الإشعار ده غير صحيح، اتأكد من صورة الاشعار ورسل اشعار صحيح، أو راسلنا.")
            suffix = "\n\n🚫 إشعار غير صحيح"
        else:
            return
        try:
            if q.message.photo:
                await q.edit_message_caption((q.message.caption or "") + suffix)
            else:
                await q.edit_message_text((q.message.text or "") + suffix)
        except:
            pass
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
        user_state[user_id] = {"name": item[1], "price": item[2], "method": item[3], "price_num": item[4]}
        kb = [[InlineKeyboardButton("اطلب الان", callback_data="order_now")],[InlineKeyboardButton("رجوع", callback_data="cat_" + cat)]]
        await q.edit_message_text(item[1] + "\nالسعر: " + item[2] + "\nالتسليم: في غضون دقائق", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu(user_id))
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
    ensure_user(user)
    state = user_state.get(user_id, {})

    # الزبون كتب مبلغ التغذية
    if state.get("waiting_topup_amount") and update.message.text:
        txt = update.message.text.replace(",", "").strip()
        nums = re.findall(r'\d+', txt)
        if not nums:
            await update.message.reply_text("اكتب المبلغ بالأرقام بس، مثال: 10000")
            return
        amount = int(nums[0])
        user_state[user_id] = {"waiting_topup_receipt": True, "topup_amount": amount}
        await update.message.reply_text(f"تمام 👌\nداير تشحن {amount:,} SDG\n\nحول على بنكك:\nبنكك: {BANKK_NUMBER}\nالاسم: {BANKK_NAME}\n\nبعد التحويل رسل صورة الاشعار هسي:")
        return

    # الزبون رسل اشعار التغذية
    if state.get("waiting_topup_receipt"):
        amount = state.get("topup_amount", 0)
        header = f"💳 طلب شحن محفظة\nالزبون: {user.first_name}\n@{user.username or ''} - ID: {user_id}\nالمبلغ: {amount:,} SDG\nرصيدو الحالي: {get_balance(user_id):,} SDG\n"
        if update.message.photo:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار الشحن", reply_markup=topup_admin_keyboard(user_id, amount))
            await update.message.reply_text("تم استلام اشعار شحن المحفظة ✅\nحنراجعو ونشحن ليك.")
            user_state[user_id] = {}
            return
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=header + "نص: " + update.message.text, reply_markup=topup_admin_keyboard(user_id, amount))
            await update.message.reply_text("تم استلام طلب شحن المحفظة ✅")
            user_state[user_id] = {}
            return

    order = state
    if not order or not order.get("waiting"):
        await update.message.reply_text("اهلا بيك اختار من القائمة /start")
        return
    header = "طلب جديد!\nالزبون: " + user.first_name + "\nيوزر التليجرام: " + str(user_id) + "\nالباقة: " + order["name"] + "\nالسعر: " + order["price"] + "\n"
    header += "الطريقة: عبر ID\n" if order["method"] == "id" else "الطريقة: عبر الحساب\n"
    header += f"رصيد محفظتو: {get_balance(user_id):,} SDG\n"
    header += "بيانات الزبون:\n"
    price_num = order.get("price_num", parse_price(order["price"]))
    try:
        if update.message.photo:
            caption = update.message.caption or ""
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار + نص: " + caption, reply_markup=admin_keyboard(user_id, price_num))
            await update.message.reply_text("وصلت صورة الاشعار ✅\nهسي رسل الـ ID حقك في رسالة براهو")
            return
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=header + update.message.text, reply_markup=admin_keyboard(user_id, price_num))
            await update.message.reply_text("تم استلام طلبك! حنراجع التحويل ونشحن ليك.")
            user_state[user_id]["waiting"] = False
    except Exception as e:
        print(e)
        await update.message.reply_text("حصل خطأ، حاول تاني")

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.rsplit("_", 2)
    if len(parts) == 3:
        action = parts[0]
        user_id = int(parts[1])
        price_num = int(parts[2])
    else:
        action, user_id = q.data.rsplit("_", 1)
        user_id = int(user_id)
        price_num = 0

    if action == "done":
        msg = "تم ✅ تم شحن طلبك بنجاح، شكراً ليك ❤️"
        suffix = "\n\n✅ تم التنفيذ"
    elif action == "fail":
        if price_num > 0:
            new_bal = change_balance(user_id, price_num)
            msg = f"عذراً ❌ فشل طلبك، وتم إرجاع المبلغ {price_num:,} SDG لمحفظتك.\nرصيدك الحالي: {new_bal:,} SDG"
            suffix = f"\n\n❌ فشل وتم الإرجاع {price_num:,} SDG للمحفظة"
        else:
            msg = "عذراً ❌ فشل طلبك، وتم إرجاع المبلغ لحسابك. راسلنا لو ما وصلك."
            suffix = "\n\n❌ فشل وتم الإرجاع"
    elif action == "dup":
        msg = "تنبيه ⚠️ الإشعار ده مكرر، تم تجاهل الطلب المكرر."
        suffix = "\n\n⚠️ إشعار مكرر"
    elif action == "wrong":
        msg = "🚫 الإشعار ده غير صحيح، اتأكد من صورة الاشعار ورسل اشعار صحيح."
        suffix = "\n\n🚫 إشعار غير صحيح"
    elif action == "unavail":
        if price_num > 0:
            new_bal = change_balance(user_id, price_num)
            msg = f"عذراً 🚫 الباقة دي غير متوفرة حالياً. تم إرجاع {price_num:,} SDG لمحفظتك.\nرصيدك: {new_bal:,} SDG"
            suffix = f"\n\n🚫 غير متوفر - تم الإرجاع {price_num:,} SDG"
        else:
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
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wallet", wallet_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("balances", balances_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("deduct", deduct_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup|wrong|unavail)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
