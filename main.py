import os
import asyncio
import sqlite3, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes


TOKEN = os.environ.get("9088330525:AAGSB9gSfCXRsbxL5grMc4dshfbr4cMFrK8") or "9088330525:AAGSB9gSfCXRsbxL5grMc4dshfbr4cMFrK8"
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

# --- قاعدة بيانات المحفظة والطلبات ---
db = sqlite3.connect("wallet.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, balance REAL DEFAULT 0)")
cur.execute("CREATE TABLE IF NOT EXISTS topups (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, status TEXT DEFAULT 'pending')")
cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, package TEXT, amount REAL, pay_method TEXT, status TEXT DEFAULT 'pending')")
db.commit()

def get_balance(uid):
    cur.execute("SELECT balance FROM users WHERE id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r else 0

def price_to_num(price_str):
    try: return float(re.sub(r'[^0-9.]', '', price_str))
    except: return 0

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
    kb = [
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}")],
        [InlineKeyboardButton("❌ فشل الطلب", callback_data=f"fail_{user_id}")],
        [InlineKeyboardButton("📄 إشعار غير صحيح", callback_data=f"wrong_{user_id}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}")],
        [InlineKeyboardButton("🚫 غير متوفر", callback_data=f"unavail_{user_id}")],
    ]
    return InlineKeyboardMarkup(kb)

def admin_topup_kb(tid):
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول التعبئة", callback_data=f"accept_{tid}"), InlineKeyboardButton("❌ رفض", callback_data=f"reject_{tid}"), InlineKeyboardButton("📄 إشعار غير صحيح", callback_data=f"wrongtop_{tid}")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (u.id, u.username or u.first_name)); db.commit()
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
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (user_id, q.from_user.username or q.from_user.first_name)); db.commit()

    if data == "main":
        await start(update, context)
        return
    if data == "my_wallet":
        await q.edit_message_text(f"💰 محفظتك:\nالرصيد: {get_balance(user_id):,.0f} SDG\nID: `{user_id}`\n\nاشحنها ببنكك واشتري بيها أي باقة طوالي.", parse_mode="Markdown", reply_markup=main_menu(user_id))
        return
    if data == "topup_wallet":
        user_state[user_id] = {"mode": "topup", "step": "amount"}
        await q.edit_message_text(f"💳 تعبئة محفظة:\n\nحول على بنكك:\nبنكك: {BANKK_NUMBER}\nالاسم: {BANKK_NAME}\n\nاكتب المبلغ الحولتو:", reply_markup=back_to_main())
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
        user_state[user_id] = {"mode": "buy", "name": item[1], "price": item[2], "price_num": price_to_num(item[2]), "method": item[3], "cat": cat}
        kb = [[InlineKeyboardButton("💰 اشتري بالمحفظة", callback_data="buy_wallet")],[InlineKeyboardButton("🏦 اطلب ببنكك مباشر", callback_data="order_now")],[InlineKeyboardButton("رجوع", callback_data="cat_" + cat)]]
        await q.edit_message_text(item[1] + "\nالسعر: " + item[2] + "\nرصيدك: " + f"{get_balance(user_id):,.0f} SDG" + "\nالتسليم: في غضون دقائق", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "buy_wallet":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu(user_id)); return
        if get_balance(user_id) < order["price_num"]:
            await q.edit_message_text(f"❌ رصيدك ما كافي!\nالسعر: {order['price']}\nرصيدك: {get_balance(user_id):,.0f}\n\nاشحن محفظتك أولاً.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 اشحن هسي", callback_data="topup_wallet")],[InlineKeyboardButton("رجوع", callback_data="main")]])); return
        cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (order["price_num"], user_id))
        cur.execute("INSERT INTO orders (user_id, package, amount, pay_method) VALUES (?,?,?,?)", (user_id, order["name"], order["price_num"], "wallet")); db.commit()
        order["waiting"] = True; order["pay_method"] = "wallet"
        txt = f"تم خصم {order['price']} من محفظتك ✅\nرصيدك الجديد: {get_balance(user_id):,.0f}\n\n"
        if order["method"] == "id":
            txt += "رسل الـ ID حقك هسي:"
        else:
            txt += "رسل بيانات حسابك هسي:\nالايميل:\nكلمة السر:\nال ID لو موجود:"
        await q.edit_message_text(txt, reply_markup=back_to_main())
        return
    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu(user_id))
            return
        order["waiting"] = True; order["pay_method"] = "bankak"
        cur.execute("INSERT INTO orders (user_id, package, amount, pay_method) VALUES (?,?,?,?)", (user_id, order["name"], order["price_num"], "bankak")); db.commit()
        method = order["method"]
        txt = "طلبك: " + order["name"] + "\nالسعر: " + order["price"] + "\n\nحول على بنكك:\nبنكك: " + BANKK_NUMBER + "\nالاسم: " + BANKK_NAME + "\n\n"
        if method == "id":
            txt += "بعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- الـ ID حقك\nمثال: ID: 123456789"
        else:
            txt += "بعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- ايميل حسابك\n3- كلمة السر\n4- ال ID لو موجود\nمثال:\nالايميل: xxx@gmail.com\nكلمة السر: xxx\nال ID: xxx"
        txt += "\n\nرسل المعلومات هسي و حنجهز ليك الطلب."
        await q.edit_message_text(txt, reply_markup=back_to_main())
        return

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    order = user_state.get(user_id)
    if not order:
        await update.message.reply_text("اهلا بيك اختار من القائمة /start")
        return
    # --- تعبئة محفظة ---
    if order.get("mode") == "topup":
        if order.get("step") == "amount":
            try: amount = float(re.sub(r'[^0-9.]', '', update.message.text or ""))
            except:
                await update.message.reply_text("اكتب المبلغ بالأرقام بس"); return
            order["amount"] = amount; order["step"] = "receipt"
            await update.message.reply_text("تمام، هسي رسل صورة إشعار بنكك 📸"); return
        elif order.get("step") == "receipt":
            amount = order["amount"]
            cur.execute("INSERT INTO topups (user_id, amount) VALUES (?,?)", (user_id, amount)); tid = cur.lastrowid; db.commit()
            caption = f"طلب تعبئة محفظة 🔔\nالزبون: {user.first_name}\nID: `{user_id}`\nالمبلغ: {amount:,.0f}"
            if update.message.photo:
                await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=caption, reply_markup=admin_topup_kb(tid), parse_mode="Markdown")
            else:
                await context.bot.send_message(ADMIN_ID, caption, reply_markup=admin_topup_kb(tid), parse_mode="Markdown")
            await update.message.reply_text("✅ طلب التعبئة اترسل، أول ما الأدمن يقبلو رصيدك حينزل.", reply_markup=main_menu(user_id))
            user_state[user_id] = {}; return

    if not order.get("waiting"):
        await update.message.reply_text("اهلا بيك اختار من القائمة /start")
        return
    pay = order.get("pay_method", "bankak")
    header = "طلب جديد! " + ("💰 بالمحفظة" if pay=="wallet" else "🏦 بنكك مباشر") + "\nالزبون: " + user.first_name + "\nيوزر التليجرام: " + str(user_id) + "\nالباقة: " + order["name"] + "\nالسعر: " + order["price"] + "\n"
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
    data = q.data

    # --- تعبئة: إشعار غير صحيح ---
    if data.startswith("wrongtop_"):
        tid = int(data.split("_")[1])
        cur.execute("SELECT user_id, amount, status FROM topups WHERE id=?", (tid,)); row = cur.fetchone()
        if not row or row[2] != "pending":
            await q.edit_message_caption("اتعالج قبل كدا."); return
        cur.execute("UPDATE topups SET status='wrong' WHERE id=?", (tid,)); db.commit()
        await context.bot.send_message(row[0], "📄 عذراً، إشعار التعبئة غير صحيح أو غير واضح.\nرسل صورة إشعار بنكك الصحيحة.")
        try: await q.edit_message_caption((q.message.caption or "") + "\n\n📄 إشعار تعبئة غير صحيح")
        except: pass
        return

    # --- تعبئة: قبول / رفض ---
    if data.startswith("accept_") or data.startswith("reject_"):
        action, tid = data.split("_"); tid = int(tid)
        cur.execute("SELECT user_id, amount, status FROM topups WHERE id=?", (tid,)); row = cur.fetchone()
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
            await context.bot.send_message(uid, "❌ تم رفض طلب التعبئة.")
        return

    # --- طلبات ---
    action, user_id = q.data.rsplit("_", 1)
    user_id = int(user_id)
    cur.execute("SELECT id, package, amount, pay_method FROM orders WHERE user_id=? AND status='pending' ORDER BY id DESC LIMIT 1", (user_id,)); order_row = cur.fetchone()

    if action == "done":
        if order_row: cur.execute("UPDATE orders SET status='done' WHERE id=?", (order_row[0],)); db.commit()
        msg = "تم ✅ تم شحن طلبك بنجاح، شكراً ليك ❤️"
        suffix = "\n\n✅ تم التنفيذ"
    elif action in ["fail", "unavail"]:
        if not order_row:
            msg = "عذراً ❌ فشل طلبك."
            suffix = "\n\n❌ فشل"
        elif order_row[3] == "wallet":
            oid, pname, amount, pay = order_row
            cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
            cur.execute("UPDATE orders SET status=? WHERE id=?", (action, oid)); db.commit()
            refund = f"\n\n💰 تم إرجاع {amount:,.0f} SDG لمحفظتك أوتوماتيك.\nرصيدك الجديد: {get_balance(user_id):,.0f} SDG"
            if action == "fail": msg = f"عذراً ❌ فشل طلبك {pname}.{refund}"
            else: msg = f"عذراً 🚫 الباقة {pname} غير متوفرة.{refund}"
            suffix = f"\n\n❌ فشل - رجع أوتوماتيك {amount:,.0f}" if action=="fail" else f"\n\n🚫 غير متوفر - رجع أوتوماتيك {amount:,.0f}"
        else:
            oid, pname, amount, pay = order_row
            cur.execute("UPDATE orders SET status='wait_manual' WHERE id=?", (oid,)); db.commit()
            if action == "fail":
                msg = f"عذراً ❌ فشل طلبك {pname}.\nحنرجع ليك مبلغ {amount:,.0f} يدوي ببنكك، راسلنا لو ما وصلك."
                suffix = f"\n\n❌ فشل - بنكك: رجع يدوي {amount:,.0f}"
            else:
                msg = f"عذراً 🚫 الباقة {pname} غير متوفرة.\nحنرجع ليك مبلغ {amount:,.0f} يدوي ببنكك."
                suffix = f"\n\n🚫 غير متوفر - بنكك: رجع يدوي {amount:,.0f}"
    elif action == "wrong":
        if order_row and order_row[3] == "wallet":
            cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (order_row[2], user_id))
            cur.execute("UPDATE orders SET status='wrong' WHERE id=?", (order_row[0],)); db.commit()
            msg = f"📄 الإشعار غير صحيح.\nتم إرجاع {order_row[2]:,.0f} SDG لمحفظتك."
            suffix = f"\n\n📄 إشعار غير صحيح وتم إرجاع {order_row[2]:,.0f}"
        else:
            if order_row: cur.execute("UPDATE orders SET status='wrong' WHERE id=?", (order_row[0],)); db.commit()
            msg = "📄 عذراً، الإشعار الرسلتو غير صحيح أو غير واضح.\nرسل صورة إشعار بنكك الصحيحة."
            suffix = "\n\n📄 إشعار غير صحيح - بدون إرجاع"
    elif action == "dup":
        msg = "تنبيه ⚠️ الإشعار ده مكرر، تم تجاهل الطلب المكرر."
        suffix = "\n\n⚠️ إشعار مكرر"
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

async def balances_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    cur.execute("SELECT id, username, balance FROM users ORDER BY balance DESC")
    rows = cur.fetchall()
    if not rows:
        await update.message.reply_text("ما فيه زباين لسه."); return
    total = sum(r[2] for r in rows)
    text = f"💰 قائمة أرصدة العملاء ({len(rows)} زبون)\nإجمالي الأرصدة: {total:,.0f} SDG\n\n"
    for i, (uid, uname, bal) in enumerate(rows, 1):
        name = f"@{uname}" if uname else f"ID {uid}"
        text += f"{i}. {name} - {bal:,.0f} SDG - `{uid}`\n"
        if len(text) > 3500:
            await update.message.reply_text(text); text = ""
    if text.strip():
        await update.message.reply_text(text)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    cur.execute("SELECT COUNT(*), SUM(balance) FROM users"); c,t = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orders WHERE status='wait_manual'"); wait = cur.fetchone()[0]
    await update.message.reply_text(f"📊 لوحة ميسر:\nمستخدمين: {c}\nإجمالي الأرصدة: {t or 0:,.0f}\nطلبات مستنية إرجاع يدوي ببنكك: {wait}\n\nالأوامر:\n/balances - كل الأرصدة\n/add ID المبلغ - شحن يدوي\n/admin - اللوحة دي")

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
    app.add_handler(CommandHandler("balances", balances_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup|unavail|wrong|accept|reject|wrongtop)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    # Fix for Python 3.14 - no current event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
