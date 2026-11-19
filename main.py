import os, sqlite3, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes


TOKEN = os.environ.get("BOT_TOKEN") or "0x9880b5513f2ef6a8b89ce6b0eb09f3e2ea14b5b2"
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز"
ADMIN_ID = 7269956912

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

db = sqlite3.connect("wallet.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, balance REAL DEFAULT 0)")
cur.execute("CREATE TABLE IF NOT EXISTS topups (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, status TEXT DEFAULT 'pending')")
db.commit()

def get_balance(uid):
    cur.execute("SELECT balance FROM users WHERE id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r else 0

user_state = {}

def main_menu(uid=None):
    bal = get_balance(uid) if uid else 0
    kb = [
        [InlineKeyboardButton(f"💰 محفظتي: {bal:,.0f} SDG", callback_data="my_wallet")],
        [InlineKeyboardButton("💳 تعبئة محفظة - بنكك", callback_data="topup_wallet")],
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
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}")],
        [InlineKeyboardButton("❌ فشل الطلب وتم إرجاع المبلغ", callback_data=f"fail_{user_id}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}")],
        [InlineKeyboardButton("🚫 غير متوفر", callback_data=f"unavail_{user_id}")],
    ])

def admin_topup_kb(topup_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول التعبئة", callback_data=f"accept_{topup_id}"), InlineKeyboardButton("❌ رفض", callback_data=f"reject_{topup_id}")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (u.id, u.username or u.first_name))
    db.commit()
    text = f"اهلا بيك في TOP 1 👑\nميسر معتز\n\n💰 رصيدك: {get_balance(u.id):,.0f} SDG\nاختار من القائمة:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu(u.id))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu(u.id))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (user_id, q.from_user.username or q.from_user.first_name))
    db.commit()
    if data == "main":
        await start(update, context); return
    if data == "my_wallet":
        await q.edit_message_text(f"💰 محفظتك:\nالرصيد: {get_balance(user_id):,.0f} SDG\nID: `{user_id}`\n\nاشحنها ببنكك واشتري بيها أي باقة طوالي.", parse_mode="Markdown", reply_markup=main_menu(user_id)); return
    if data == "topup_wallet":
        user_state[user_id] = {"mode": "topup", "step": "amount"}
        await q.edit_message_text(f"💳 تعبئة محفظة:\n\nحول بنكك لـ:\nرقم: {BANKK_NUMBER}\nالاسم: {BANKK_NAME}\n\nاكتب المبلغ الحولتو:", reply_markup=back_to_main()); return
    if data.startswith("cat_"):
        cat = data[4:]
        kb = []
        for i, item in enumerate(PACKAGES[cat]):
            kb.append([InlineKeyboardButton(item[0], callback_data=f"item_{cat}_{i}")])
        kb.append([InlineKeyboardButton("رجوع", callback_data="main")])
        await q.edit_message_text(CATEGORY_NAMES[cat], reply_markup=InlineKeyboardMarkup(kb)); return
    if data.startswith("item_"):
        rest = data[5:]
        idx = int(rest.rsplit("_", 1)[-1]); cat = rest.rsplit("_", 1)[0]
        item = PACKAGES[cat][idx]
        user_state[user_id] = {"mode": "buy", "name": item[1], "price": item[2], "price_num": item[4], "method": item[3], "cat": cat}
        kb = [[InlineKeyboardButton("💰 اشتري بالمحفظة", callback_data="buy_wallet")],[InlineKeyboardButton("🏦 اطلب ببنكك مباشر", callback_data="order_now")],[InlineKeyboardButton("رجوع", callback_data=f"cat_{cat}")]]
        await q.edit_message_text(f"{item[1]}\nالسعر: {item[2]}\nرصيدك: {get_balance(user_id):,.0f} SDG\nالتسليم: في غضون دقائق", reply_markup=InlineKeyboardMarkup(kb)); return
    if data == "buy_wallet":
        order = user_state.get(user_id)
        if not order: return
        if get_balance(user_id) < order["price_num"]:
            await q.edit_message_text(f"❌ رصيدك ما كافي!\nالسعر: {order['price']}\nرصيدك: {get_balance(user_id):,.0f}\n\nاشحن محفظتك أولاً.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 اشحن هسي", callback_data="topup_wallet")],[InlineKeyboardButton("رجوع", callback_data="main")]])); return
        cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (order["price_num"], user_id)); db.commit()
        order["waiting"] = True; order["pay_method"] = "wallet"
        txt = f"تم خصم {order['price']} من محفظتك ✅\nرصيدك الجديد: {get_balance(user_id):,.0f}\n\n"
        if order["method"] == "id":
            txt += "رسل الـ ID حقك هسي:"
        else:
            txt += "رسل بيانات حسابك هسي:\nالايميل:\nكلمة السر:\nال ID لو موجود:"
        await q.edit_message_text(txt, reply_markup=back_to_main()); return
    if data == "order_now":
        order = user_state.get(user_id)
        if not order: return
        order["waiting"] = True; order["pay_method"] = "bankak"
        txt = f"طلبك: {order['name']}\nالسعر: {order['price']}\n\nحول على بنكك:\nبنكك: {BANKK_NUMBER}\nالاسم: {BANKK_NAME}\n\n"
        if order["method"] == "id":
            txt += "بعد التحويل رسل في رسالة واحدة:\n1- صورة اشعار التحويل\n2- الـ ID حقك"
        else:
            txt += "بعد التحويل رسل في رسالة واحدة:\n1- صورة اشعار التحويل\n2- ايميل حسابك\n3- كلمة السر\n4- ال ID لو موجود"
        await q.edit_message_text(txt, reply_markup=back_to_main()); return

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user; user_id = user.id
    order = user_state.get(user_id)
    if not order:
        await update.message.reply_text("اهلا بيك اختار من القائمة /start"); return
    if order.get("mode") == "topup":
        if order.get("step") == "amount":
            try: amount = float(re.sub(r'[^0-9.]', '', update.message.text))
            except:
                await update.message.reply_text("اكتب المبلغ بالأرقام بس"); return
            order["amount"] = amount; order["step"] = "receipt"
            await update.message.reply_text("تمام، هسي رسل صورة إشعار بنكك 📸"); return
        elif order.get("step") == "receipt":
            amount = order["amount"]
            cur.execute("INSERT INTO topups (user_id, amount) VALUES (?,?)", (user_id, amount))
            tid = cur.lastrowid; db.commit()
            caption = f"طلب تعبئة محفظة 🔔\nالزبون: {user.first_name}\nID: `{user_id}`\nالمبلغ: {amount:,.0f}"
            if update.message.photo:
                await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=caption, reply_markup=admin_topup_kb(tid), parse_mode="Markdown")
            else:
                await context.bot.send_message(ADMIN_ID, caption, reply_markup=admin_topup_kb(tid), parse_mode="Markdown")
            await update.message.reply_text("✅ طلب التعبئة اترسل، أول ما الأدمن يقبلو رصيدك حينزل.", reply_markup=main_menu(user_id))
            user_state[user_id] = {}; return
    if not order.get("waiting"):
        await update.message.reply_text("اختار باقة أولاً /start"); return
    pay = order.get("pay_method", "bankak")
    header = f"طلب جديد! {'💰 بالمحفظة' if pay=='wallet' else '🏦 بنكك مباشر'}\nالزبون: {user.first_name}\nID تليجرام: {user_id}\nالباقة: {order['name']}\nالسعر: {order['price']}\nالطريقة: {'عبر ID' if order['method']=='id' else 'عبر الحساب'}\nبيانات الزبون:\n"
    try:
        if update.message.photo:
            caption = update.message.caption or ""
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار + نص: " + caption, reply_markup=admin_keyboard(user_id))
            await update.message.reply_text("وصلت صورة الاشعار ✅\nهسي رسل باقي البيانات في رسالة براها")
            return
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=header + update.message.text, reply_markup=admin_keyboard(user_id))
            await update.message.reply_text("تم استلام طلبك! حنراجع ونشحن ليك.")
            user_state[user_id] = {}
    except Exception as e:
        print(e); await update.message.reply_text("حصل خطأ، حاول تاني")

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    data = q.data
    if data.startswith("accept_") or data.startswith("reject_"):
        action, tid = data.split("_"); tid = int(tid)
        cur.execute("SELECT user_id, amount, status FROM topups WHERE id=?", (tid,))
        row = cur.fetchone()
        if not row or row[2] != "pending":
            await q.edit_message_caption("اتعالج قبل كدا."); return
        uid, amount = row[0], row[1]
        if action == "accept":
            cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, uid))
            cur.execute("UPDATE topups SET status='accepted' WHERE id=?", (tid,)); db.commit()
            try: await q.edit_message_caption((q.message.caption or "") + f"\n\n✅ تم قبول {amount:,.0f}")
            except: pass
            await context.bot.send_message(uid, f"🎉 تم قبول تعبئتك {amount:,.0f} SDG. رصيدك: {get_balance(uid):,.0f}")
        else:
            cur.execute("UPDATE topups SET status='rejected' WHERE id=?", (tid,)); db.commit()
            try: await q.edit_message_caption((q.message.caption or "") + "\n\n❌ تم الرفض")
            except: pass
            await context.bot.send_message(uid, "❌ تم رفض طلب التعبئة."); return
    action, user_id = data.rsplit("_", 1); user_id = int(user_id)
    msgs = {
        "done": ("تم ✅ تم شحن طلبك بنجاح، شكراً ليك ❤️", "\n\n✅ تم التنفيذ"),
        "fail": ("عذراً ❌ فشل طلبك، وتم إرجاع المبلغ لحسابك.", "\n\n❌ فشل وتم الإرجاع"),
        "dup": ("تنبيه ⚠️ الإشعار ده مكرر، تم تجاهل الطلب.", "\n\n⚠️ إشعار مكرر"),
        "unavail": ("عذراً 🚫 الباقة غير متوفرة حالياً.", "\n\n🚫 غير متوفر"),
    }
    if action not in msgs: return
    msg, suffix = msgs[action]
    await context.bot.send_message(user_id, msg)
    try:
        if q.message.photo: await q.edit_message_caption((q.message.caption or "") + suffix)
        else: await q.edit_message_text((q.message.text or "") + suffix)
    except: pass

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    cur.execute("SELECT COUNT(*), SUM(balance) FROM users")
    c, t = cur.fetchone()
    await update.message.reply_text(f"📊 لوحة ميسر:\nمستخدمين: {c}\nإجمالي الأرصدة: {t or 0:,.0f}\nشحن يدوي: /add ID المبلغ")

async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        target = int(context.args[0]); amount = float(context.args[1])
        cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, target)); db.commit()
        await update.message.reply_text(f"تم إضافة {amount:,.0f} لـ {target}")
        await context.bot.send_message(target, f"💰 الأدمن أضاف ليك {amount:,.0f} SDG. رصيدك: {get_balance(target):,.0f}")
    except: await update.message.reply_text("مثال: /add 123456 5000")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup|unavail|accept|reject)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running..."); app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
