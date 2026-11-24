import os
import asyncio
import sqlite3
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز صالح"
MYCASHI_NUMBER = "400110751"
MYCASHI_NAME = "ميسر معتز صالح"
ADMIN_ID = 7269956912
DB = "wallet.db"

PACKAGES = {
    "id_gems": [
        ("100💎 - 12,500", "100 جوهرة", "12,500 جنيه", "id", 12500),
        ("200💎 - 25,000", "200 جوهرة", "25,000 جنيه", "id", 25000),
        ("500💎 - 62,500", "500 جوهرة", "62,500 جنيه", "id", 62500),
        ("1000💎 - 125,000", "1000 جوهرة", "125,000 جنيه", "id", 125000),
        ("28,000 - العضوية الأسبوعية", "العضوية الأسبوعية", "28,000 جنيه", "id", 28000),
        ("136,000 - العضوية الشهرية", "العضوية الشهرية", "136,000 جنيه", "id", 136000),
    ],
    "id_level": [
        ("7,500 - Level Up - 6 مستوى", "Level Up - 6 مستوى", "7,500 جنيه", "id", 7500),
        ("9,000 - Level Up - 10 مستوى", "Level Up - 10 مستوى", "9,000 جنيه", "id", 9000),
        ("9,000 - Level Up - 15 مستوى", "Level Up - 15 مستوى", "9,000 جنيه", "id", 9000),
        ("9,000 - Level Up - 20 مستوى", "Level Up - 20 مستوى", "9,000 جنيه", "id", 9000),
        ("9,000 - Level Up - 25 مستوى", "Level Up - 25 مستوى", "9,000 جنيه", "id", 9000),
        ("13,500 - Level Up - 30 مستوى", "Level Up - 30 مستوى", "13,500 جنيه", "id", 13500),
    ],
        "acc_gems": [
        ("100💎 عبر الحساب - 11,500", "100 جوهرة عبر الحساب", "11,500 جنيه", "acc", 11500),
        ("200💎 عبر الحساب - 23,000", "200 جوهرة عبر الحساب", "23,000 جنيه", "acc", 23000),
        ("500💎 عبر الحساب - 57,500", "500 جوهرة عبر الحساب", "57,500 جنيه", "acc", 57500),
        ("1000💎 عبر الحساب - 115,000", "1000 جوهرة عبر الحساب", "115,000 جنيه", "acc", 115000),
    ],
    "airdrop": [
        ("انزال $1 - 12,500", "انزال جوي $1", "12,500 جنيه", "acc", 12500),
        ("انزال $2 - 25,000", "انزال جوي $2", "25,000 جنيه", "acc", 25000),
    ],
}

CATEGORY_NAMES = {
    "id_gems": "شحن جواهر وعملات - ID",
    "id_level": "Level Up Pass - ID",
    "acc_gems": "شحن جواهر عبر الحساب",
    "airdrop": "انزالات جوية - Airdrop",
}

user_state = {}

def payment_text(method):
    if method == "mycashi":
        return f"ماي كاشي:\nالرقم: {MYCASHI_NUMBER}\nالاسم: {MYCASHI_NAME}"
    return f"بنكك:\nبنكك: {BANKK_NUMBER}\nالاسم: {BANKK_NAME}"

def payment_keyboard(prefix="pay"):
    kb = [
        [InlineKeyboardButton("🏦 بنكك", callback_data=f"{prefix}_bankak")],
        [InlineKeyboardButton("📱 ماي كاشي", callback_data=f"{prefix}_mycashi")],
        [InlineKeyboardButton("رجوع", callback_data="main")],
    ]
    return InlineKeyboardMarkup(kb)

# ---------- Wallet DB ----------
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, balance INTEGER DEFAULT 0, blocked INTEGER DEFAULT 0)")
    try:
        cur.execute("ALTER TABLE users ADD COLUMN blocked INTEGER DEFAULT 0")
    except:
        pass
    con.commit()
    con.close()

def ensure_user(user):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, balance, blocked) VALUES (?,?,?,0,0)", (user.id, user.username or "", user.first_name or ""))
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

def is_blocked(user_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT blocked FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return bool(row and row[0] == 1)

def set_blocked(user_id, blocked):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE users SET blocked=? WHERE user_id=?", (1 if blocked else 0, user_id))
    con.commit()
    con.close()

def get_blocked_users():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT user_id, username, first_name FROM users WHERE blocked=1")
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
        [InlineKeyboardButton("انزالات جوية - Airdrop", callback_data="cat_airdrop")],
        [InlineKeyboardButton("📞 التواصل والدعم", url="https://t.me/TOP1MOYASAR")],
    ]
    return InlineKeyboardMarkup(kb)

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("الرئيسية", callback_data="main")]])

def admin_menu_keyboard():
    kb = [
        [InlineKeyboardButton("✉️ رسالة لزول محدد (نص + صورة)", callback_data="admin_msg_start")],
        [InlineKeyboardButton("📢 رسالة جماعية (نص أو صورة)", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_block_start")],
        [InlineKeyboardButton("✅ فك حظر مستخدم", callback_data="admin_unblock_start")],
        [InlineKeyboardButton("📋 قائمة المحظورين", callback_data="admin_blocked_list")],
        [InlineKeyboardButton("💰 كل الأرصدة", callback_data="admin_balances")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main")],
    ]
    return InlineKeyboardMarkup(kb)

def admin_keyboard(user_id, price_num=0):
    kb = [
        [InlineKeyboardButton("✅ تم الطلب", callback_data=f"done_{user_id}_{price_num}")],
        [InlineKeyboardButton("❌ فشل الطلب وتم إرجاع المبلغ", callback_data=f"fail_{user_id}_{price_num}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"dup_{user_id}_{price_num}")],
        [InlineKeyboardButton("🚫 إشعار غير صحيح", callback_data=f"wrong_{user_id}_{price_num}")],
        [InlineKeyboardButton("🚫 غير متوفر", callback_data=f"unavail_{user_id}_{price_num}")],
        [InlineKeyboardButton("🚫 حظر الزبون ده", callback_data=f"admin_block_user_{user_id}")],
    ]
    return InlineKeyboardMarkup(kb)

def topup_admin_keyboard(user_id, amount):
    kb = [
        [InlineKeyboardButton("✅ قبول وشحن المحفظة", callback_data=f"topup_yes_{user_id}_{amount}")],
        [InlineKeyboardButton("❌ رفض", callback_data=f"topup_no_{user_id}_{amount}")],
        [InlineKeyboardButton("⚠️ إشعار مكرر", callback_data=f"topup_dup_{user_id}_{amount}")],
        [InlineKeyboardButton("🚫 إشعار غير صحيح", callback_data=f"topup_wrong_{user_id}_{amount}")],
        [InlineKeyboardButton("🚫 حظر الزبون ده", callback_data=f"admin_block_user_{user_id}")],
    ]
    return InlineKeyboardMarkup(kb)

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user)
    if is_blocked(user.id):
        txt = "🚫 تم حظرك من استخدام البوت.\nراسل الدعم لو شايف ده غلط: @TOP1MOYASAR"
        if update.message:
            await update.message.reply_text(txt)
        else:
            await update.callback_query.edit_message_text(txt)
        return
    bal = get_balance(user.id)
    text = f"اهلا بيك في TOP 1 👑\n💰 محفظتك: {bal:,} SDG\nاختار من القائمة:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu(user.id))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu(user.id))

async def wallet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user)
    if is_blocked(user.id):
        await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return
    bal = get_balance(user.id)
    await update.message.reply_text(f"💰 محفظتي\n\nرصيدك الحالي: {bal:,} SDG\n\nلشحن المحفظة دوس زر تغذية محفظتي من القائمة", reply_markup=back_to_main())

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_users()
    total = sum(u[3] for u in users)
    blocked = get_blocked_users()
    txt = f"📊 لوحة الأدمن - TOP 1\n\nعدد المستخدمين: {len(users)}\nإجمالي الأرصدة: {total:,} SDG\nالمحظورين: {len(blocked)}\n\nآخر 10:\n"
    for u in users[:10]:
        txt += f"- {u[2]} (@{u[1]}) - {u[3]:,} SDG - ID: {u[0]}\n"
    txt += "\nأوامر سريعة:\n/balances - كل الأرصدة\n/add [ID] [المبلغ]\n/deduct [ID] [المبلغ]\n/msg [ID] [الرسالة]\n/block [ID]\n/unblock [ID]\n/broadcast [الرسالة]"
    await update.message.reply_text(txt, reply_markup=admin_menu_keyboard())

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

async def msg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    raw_text = update.message.text or update.message.caption or ""
    parts = raw_text.split()
    try:
        if len(parts) >= 2 and parts[0].startswith("/msg"):
            target = int(re.findall(r'\d+', parts[1])[0])
            text = " ".join(parts[2:])
        else:
            target = int(context.args[0])
            text = " ".join(context.args[1:])
        if update.message.photo:
            await context.bot.send_photo(target, photo=update.message.photo[-1].file_id, caption=text if text else "📩 رسالة من TOP 1")
            await update.message.reply_text(f"✅ تم ارسال الصورة + النص لـ {target}")
            return
        if update.message.reply_to_message and update.message.reply_to_message.photo:
            photo = update.message.reply_to_message.photo[-1].file_id
            await context.bot.send_photo(target, photo=photo, caption=text if text else "📩 رسالة من TOP 1")
            await update.message.reply_text(f"✅ تم ارسال الصورة لـ {target}")
            return
        if not text:
            await update.message.reply_text("اكتب الرسالة: /msg [ID] [الرسالة]")
            return
        await context.bot.send_message(target, text)
        await update.message.reply_text(f"✅ تم ارسال الرسالة لـ {target}")
    except Exception as e:
        print(e)
        await update.message.reply_text("ما قدرت ارسل.\nجرب:\n/msg 123456 اهلا بيك")

async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target = int(context.args[0])
        ensure_user(type("obj", (), {"id": target, "username": "", "first_name": "User"})())
        set_blocked(target, True)
        await update.message.reply_text(f"🚫 تم حظر المستخدم {target} من البوت.")
        try:
            await context.bot.send_message(target, "🚫 تم حظرك من استخدام بوت TOP 1.\nراسل الدعم لو شايف ده غلط: @TOP1MOYASAR")
        except:
            pass
    except:
        await update.message.reply_text("الاستخدام: /block [ID]\nمثال: /block 123456")

async def unblock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target = int(context.args[0])
        set_blocked(target, False)
        await update.message.reply_text(f"✅ تم فك حظر المستخدم {target}.")
        try:
            await context.bot.send_message(target, "✅ تم فك الحظر عنك، تقدر تستخدم بوت TOP 1 تاني. اكتب /start")
        except:
            pass
    except:
        await update.message.reply_text("الاستخدام: /unblock [ID]")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.message.photo:
        caption = update.message.caption or ""
        caption = caption.replace("/broadcast", "").strip()
        users = get_all_users()
        sent = failed = 0
        for u in users:
            uid = u[0]
            if uid == ADMIN_ID or is_blocked(uid):
                continue
            try:
                await context.bot.send_photo(uid, photo=update.message.photo[-1].file_id, caption=f"📢 رسالة من TOP 1 👑\n\n{caption}" if caption else "📢 رسالة من TOP 1 👑")
                sent += 1
            except:
                failed += 1
        await update.message.reply_text(f"✅ تم الانتهاء\nتم: {sent} | فشل: {failed}")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("اكتب الرسالة: /broadcast [الرسالة]")
        return
    users = get_all_users()
    await update.message.reply_text(f"📢 جاري الارسال لـ {len(users)} مستخدم...")
    sent = failed = 0
    for u in users:
        uid = u[0]
        if uid == ADMIN_ID or is_blocked(uid):
            continue
        try:
            await context.bot.send_message(uid, f"📢 رسالة من TOP 1 👑\n\n{text}")
            sent += 1
        except:
            failed += 1
    await update.message.reply_text(f"✅ تم الانتهاء\nتم الارسال: {sent}\nفشل: {failed}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    ensure_user(q.from_user)

    if data == "admin_msg_start" and user_id == ADMIN_ID:
        user_state[user_id] = {"waiting_msg_id": True}
        await q.edit_message_text("✉️ رسالة لزول محدد\n\nاكتب ID الزول الداير ترسل ليهو:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إلغاء", callback_data="admin_back")]]))
        return
    if data == "admin_broadcast_start" and user_id == ADMIN_ID:
        user_state[user_id] = {"waiting_broadcast": True}
        await q.edit_message_text("📢 رسالة جماعية\n\nارسل هسي:\n- نص ساي\n- أو صورة + نص في التعليق", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إلغاء", callback_data="admin_back")]]))
        return
    if data == "admin_block_start" and user_id == ADMIN_ID:
        user_state[user_id] = {"waiting_block_id": True}
        await q.edit_message_text("🚫 حظر مستخدم\n\nاكتب ID الزول الداير تحظرو:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إلغاء", callback_data="admin_back")]]))
        return
    if data == "admin_unblock_start" and user_id == ADMIN_ID:
        user_state[user_id] = {"waiting_unblock_id": True}
        await q.edit_message_text("✅ فك حظر مستخدم\n\nاكتب ID الزول الداير تفك حظرو:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إلغاء", callback_data="admin_back")]]))
        return
    if data == "admin_blocked_list" and user_id == ADMIN_ID:
        blocked = get_blocked_users()
        if not blocked:
            await q.edit_message_text("لا يوجد مستخدمين محظورين.", reply_markup=admin_menu_keyboard())
            return
        kb = []
        for b in blocked:
            kb.append([InlineKeyboardButton(f"✅ فك حظر {b[2]} - {b[0]}", callback_data=f"admin_unblock_user_{b[0]}")])
        kb.append([InlineKeyboardButton("رجوع", callback_data="admin_back")])
        await q.edit_message_text(f"📋 المحظورين ({len(blocked)}):", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "admin_balances" and user_id == ADMIN_ID:
        users = get_all_users()
        txt = "💰 قائمة أرصدة العملاء\n\n"
        for i, u in enumerate(users[:20], 1):
            txt += f"{i}. {u[2]} (@{u[1]}) - {u[3]:,} SDG - {u[0]}\n"
        await q.edit_message_text(txt, reply_markup=admin_menu_keyboard())
        return
    if data == "admin_back" and user_id == ADMIN_ID:
        user_state[user_id] = {}
        users = get_all_users()
        total = sum(u[3] for u in users)
        txt = f"📊 لوحة الأدمن - TOP 1\n\nعدد المستخدمين: {len(users)}\nإجمالي الأرصدة: {total:,} SDG\n\nاختار:"
        await q.edit_message_text(txt, reply_markup=admin_menu_keyboard())
        return
    if data.startswith("admin_block_user_") and user_id == ADMIN_ID:
        target = int(data.replace("admin_block_user_", ""))
        set_blocked(target, True)
        await q.edit_message_text(f"🚫 تم حظر {target}", reply_markup=admin_menu_keyboard())
        try:
            await context.bot.send_message(target, "🚫 تم حظرك من استخدام بوت TOP 1.")
        except:
            pass
        return
    if data.startswith("admin_unblock_user_") and user_id == ADMIN_ID:
        target = int(data.replace("admin_unblock_user_", ""))
        set_blocked(target, False)
        await q.edit_message_text(f"✅ تم فك حظر {target}", reply_markup=admin_menu_keyboard())
        try:
            await context.bot.send_message(target, "✅ تم فك الحظر عنك، اكتب /start")
        except:
            pass
        return

    if is_blocked(user_id):
        await q.edit_message_text("🚫 تم حظرك من استخدام البوت.")
        return

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
    if data == "topup_start":
        user_state[user_id] = {"waiting_topup_amount": True}
        await q.edit_message_text("💳 تغذية محفظتي\n\nاكتب المبلغ الداير تشحن بيهو المحفظة\nمثال: 10000\n\nاكتبو في رسالة هسي:", reply_markup=back_to_main())
        return

    if data.startswith("topup_pay_"):
        method = data.replace("topup_pay_", "")
        amount = user_state.get(user_id, {}).get("topup_amount", 0)
        user_state[user_id] = {"waiting_topup_receipt": True, "topup_amount": amount, "pay_method": method}
        await q.edit_message_text(f"تمام 👌\nداير تشحن {amount:,} SDG\n\nحول على:\n{payment_text(method)}\n\nبعد التحويل رسل صورة الاشعار هسي:", reply_markup=back_to_main())
        return

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
        user_state[user_id] = {"name": item[1], "price": item[2], "method": item[3], "price_num": item[4], "cat": cat}
        kb = [[InlineKeyboardButton("اطلب الان", callback_data="order_now")],[InlineKeyboardButton("رجوع", callback_data="cat_" + cat)]]
        await q.edit_message_text(item[1] + "\nالسعر: " + item[2] + "\nالتسليم: في غضون دقائق", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu(user_id))
            return
        await q.edit_message_text(f"طلبك: {order['name']}\nالسعر: {order['price']}\n\nاختار طريقة الدفع:", reply_markup=payment_keyboard("pay"))
        return

    if data.startswith("pay_"):
        method = data.replace("pay_", "")
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=main_menu(user_id))
            return
        order_method = order["method"]
        cat = order.get("cat", "")
        txt = "طلبك: " + order["name"] + "\nالسعر: " + order["price"] + f"\nطريقة الدفع: {'ماي كاشي' if method=='mycashi' else 'بنكك'}\n\nحول على:\n{payment_text(method)}\n\n"
        if cat == "airdrop":
            txt += "بعد التحويل رسل لينا:\n1- صورة اشعار التحويل\n2- بعدها رسل البريد الالكتروني وكلمة السر مع بعض في رسالة واحدة\n\nمثال:\nbasomaa891@gmail.com\nكلمة السر: 123456"
        elif order_method == "id":
            txt += "بعد التحويل رسل لينا في رسالة واحدة:\n1- صورة اشعار التحويل\n2- الـ ID حقك\nمثال: ID: 123456789"
        else:
            txt += "بعد التحويل رسل لينا:\n1- صورة اشعار التحويل\n2- بعدها رسل البريد الالكتروني وكلمة السر مع بعض في رسالة واحدة\n\nمثال:\nxxx@gmail.com\nكلمة السر: xxx"
        txt += "\n\nرسل صورة الاشعار هسي."
        user_state[user_id]["waiting"] = True
        user_state[user_id]["stage"] = "waiting_photo"
        user_state[user_id]["pay_method"] = method
        await q.edit_message_text(txt, reply_markup=back_to_main())
        return

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    ensure_user(user)
    state = user_state.get(user_id, {})

    if user_id == ADMIN_ID and update.message.photo and update.message.caption and update.message.caption.strip().startswith("/msg"):
        await msg_cmd(update, context)
        return
    if user_id == ADMIN_ID and update.message.caption and update.message.caption.strip().startswith("/broadcast"):
        await broadcast_cmd(update, context)
        return

    if user_id == ADMIN_ID and state.get("waiting_msg_id") and update.message.text:
        nums = re.findall(r'\d+', update.message.text)
        if not nums:
            await update.message.reply_text("اكتب ID بالأرقام بس")
            return
        target = int(nums[0])
        user_state[user_id] = {"waiting_msg_content": True, "msg_target": target}
        await update.message.reply_text(f"تمام، حترسل لـ {target}\n\nهسي ارسل الرسالة:\n- نص ساي\n- أو صورة + نص في تعليقها")
        return

    if user_id == ADMIN_ID and state.get("waiting_msg_content"):
        target = state.get("msg_target")
        if update.message.photo:
            caption = update.message.caption or ""
            try:
                await context.bot.send_photo(target, photo=update.message.photo[-1].file_id, caption=caption if caption else "📩 رسالة من TOP 1")
                user_state[user_id] = {}
                await update.message.reply_text(f"✅ تم ارسال الصورة + النص لـ {target}")
            except:
                user_state[user_id] = {}
                await update.message.reply_text("ما قدرت ارسل، الزول ده ما بدأ البوت.")
            return
        if update.message.text:
            try:
                await context.bot.send_message(target, update.message.text)
                user_state[user_id] = {}
                await update.message.reply_text(f"✅ تم ارسال الرسالة لـ {target}")
            except:
                user_state[user_id] = {}
                await update.message.reply_text("ما قدرت ارسل، الزول ده ما بدأ البوت.")
            return

    if user_id == ADMIN_ID and state.get("waiting_broadcast"):
        users = get_all_users()
        if update.message.photo:
            caption = update.message.caption or ""
            sent = failed = 0
            for u in users:
                uid = u[0]
                if uid == ADMIN_ID or is_blocked(uid):
                    continue
                try:
                    await context.bot.send_photo(uid, photo=update.message.photo[-1].file_id, caption=f"📢 رسالة من TOP 1 👑\n\n{caption}" if caption else "📢 رسالة من TOP 1 👑")
                    sent += 1
                except:
                    failed += 1
            user_state[user_id] = {}
            await update.message.reply_text(f"✅ تم\nتم: {sent} | فشل: {failed}")
            return
        if update.message.text:
            text = update.message.text
            sent = failed = 0
            for u in users:
                uid = u[0]
                if uid == ADMIN_ID or is_blocked(uid):
                    continue
                try:
                    await context.bot.send_message(uid, f"📢 رسالة من TOP 1 👑\n\n{text}")
                    sent += 1
                except:
                    failed += 1
            user_state[user_id] = {}
            await update.message.reply_text(f"✅ تم\nتم: {sent} | فشل: {failed}")
            return

    if user_id == ADMIN_ID and state.get("waiting_block_id") and update.message.text:
        nums = re.findall(r'\d+', update.message.text)
        if not nums:
            await update.message.reply_text("اكتب ID بالأرقام بس")
            return
        target = int(nums[0])
        set_blocked(target, True)
        user_state[user_id] = {}
        await update.message.reply_text(f"🚫 تم حظر {target}")
        try:
            await context.bot.send_message(target, "🚫 تم حظرك من استخدام بوت TOP 1.")
        except:
            pass
        return

    if user_id == ADMIN_ID and state.get("waiting_unblock_id") and update.message.text:
        nums = re.findall(r'\d+', update.message.text)
        if not nums:
            await update.message.reply_text("اكتب ID بالأرقام بس")
            return
        target = int(nums[0])
        set_blocked(target, False)
        user_state[user_id] = {}
        await update.message.reply_text(f"✅ تم فك حظر {target}")
        try:
            await context.bot.send_message(target, "✅ تم فك الحظر عنك، اكتب /start")
        except:
            pass
        return

    if is_blocked(user_id):
        await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return

    if state.get("waiting_topup_amount") and update.message.text:
        txt = update.message.text.replace(",", "").strip()
        nums = re.findall(r'\d+', txt)
        if not nums:
            await update.message.reply_text("اكتب المبلغ بالأرقام بس، مثال: 10000")
            return
        amount = int(nums[0])
        user_state[user_id] = {"waiting_topup_pay_choice": True, "topup_amount": amount}
        await update.message.reply_text(f"تمام 👌\nداير تشحن {amount:,} SDG\n\nاختار طريقة الدفع:", reply_markup=payment_keyboard("topup_pay"))
        return

    if state.get("waiting_topup_receipt"):
        amount = state.get("topup_amount", 0)
        pay_method = state.get("pay_method", "bankak")
        header = f"💳 طلب شحن محفظة\nالزبون: {user.first_name}\n@{user.username or ''} - ID: {user_id}\nالمبلغ: {amount:,} SDG\nطريقة الدفع: {'ماي كاشي' if pay_method=='mycashi' else 'بنكك'}\nرصيدو الحالي: {get_balance(user_id):,} SDG\n"
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

    cat = order.get("cat", "")
    method = order.get("method", "id")
    stage = order.get("stage", "waiting_photo")
    price_num = order.get("price_num", parse_price(order["price"]))
    pay_method = order.get("pay_method", "bankak")

    if stage == "waiting_photo":
        if update.message.photo:
            caption = update.message.caption or ""
            header = "طلب جديد!\nالزبون: " + user.first_name + "\nيوزر التليجرام: " + str(user_id) + "\nالباقة: " + order["name"] + "\nالسعر: " + order["price"] + "\n"
            header += "الطريقة: عبر ID\n" if method == "id" and cat != "airdrop" else "الطريقة: عبر الحساب / انزال\n"
            header += f"طريقة الدفع: {'ماي كاشي' if pay_method=='mycashi' else 'بنكك'}\n"
            header += f"رصيد محفظتو: {get_balance(user_id):,} SDG\n"
            header += "بيانات الزبون:\n"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=header + "صورة اشعار + نص: " + caption, reply_markup=admin_keyboard(user_id, price_num))
            user_state[user_id]["stage"] = "waiting_details"
            if cat == "airdrop":
                await update.message.reply_text("وصلت صورة الاشعار ✅\n\nهسي رسل البريد الالكتروني وكلمة السر مع بعض في رسالة واحدة 👇\n\nمثال:\nbasomaa891@gmail.com\nكلمة السر: 123456")
            elif method == "id":
                await update.message.reply_text("وصلت صورة الاشعار ✅\nهسي رسل الـ ID حقك في رسالة براهو")
            else:
                await update.message.reply_text("وصلت صورة الاشعار ✅\n\nهسي رسل البريد الالكتروني وكلمة السر مع بعض في رسالة واحدة 👇\n\nمثال:\nxxx@gmail.com\nكلمة السر: xxx")
            return
        else:
            await update.message.reply_text("رسل صورة الاشعار أولاً 📸")
            return

    if stage == "waiting_details":
        if update.message.photo:
            await update.message.reply_text("خلاص وصلت الصورة، هسي رسل البيانات في رسالة نصية")
            return
        header2 = f"📩 بيانات الزبون - {order['name']}\nالزبون: {user.first_name} - ID: {user_id}\n"
        await context.bot.send_message(chat_id=ADMIN_ID, text=header2 + update.message.text, reply_markup=admin_keyboard(user_id, price_num))
        await update.message.reply_text("تم استلام طلبك! حنراجع التحويل ونشحن ليك ✅")
        user_state[user_id] = {}
        return

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
    app.add_handler(CommandHandler("msg", msg_cmd))
    app.add_handler(CommandHandler("block", block_cmd))
    app.add_handler(CommandHandler("unblock", unblock_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^(done|fail|dup|wrong|unavail)_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, receive_message))
    print("Bot is running...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
