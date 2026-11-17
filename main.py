import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

# ====== بيانات المتجر ======
BANKK_NUMBER = "8994176"
BANKK_NAME = "ميسر معتز"
ADMIN_ID = 7269956912
# =====================

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
        ("100 جوهرة - 11,500", "100 جوهرة (عبر الحساب)", "11,500 جنيه", "account"),
    ],
    "acc_level": [
        ("مستوى 6 - 7,000", "Level Up - مستوى 6 (عبر الحساب)", "7,000 جنيه", "account"),
        ("مستوى 10 - 8,000", "Level Up - مستوى 10 (عبر الحساب)", "8,000 جنيه", "account"),
        ("مستوى 15 - 8,000", "Level Up - مستوى 15 (عبر الحساب)", "8,000 جنيه", "account"),
        ("مستوى 20 - 8,000", "Level Up - مستوى 20 (عبر الحساب)", "8,000 جنيه", "account"),
        ("مستوى 25 - 8,000", "Level Up - مستوى 25 (عبر الحساب)", "8,000 جنيه", "account"),
        ("مستوى 30 - 11,000", "Level Up - مستوى 30 (عبر الحساب)", "11,000 جنيه", "account"),
    ],
    "airdrop": [
        ("إنزال 1$ - 13,000", "إنزال جوي 1$", "13,000 جنيه", "id"),
        ("إنزال 2$ - 26,000", "إنزال جوي 2$", "26,000 جنيه", "id"),
    ],
}

CATEGORY_NAMES = {
    "id_gems": "💎 شحن جواهر وعضويات - عبر ID",
    "id_level": "🔥 Level Up Pass - عبر ID",
    "acc_gems": "💎 شحن جواهر - عبر الحساب (أرخص)",
    "acc_level": "🔥 Level Up Pass - عبر الحساب (أرخص)",
    "airdrop": "✈️ إنزالات جوية - Airdrop",
}

user_state = {}

def main_menu():
    kb = [
        [InlineKeyboardButton("💎 شحن جواهر وعضويات - ID", callback_data="cat_id_gems")],
        [InlineKeyboardButton("🔥 Level Up Pass - ID", callback_data="cat_id_level")],
        [InlineKeyboardButton("💎 شحن عبر الحساب - أرخص", callback_data="cat_acc_gems")],
        [InlineKeyboardButton("🔥 Level Up عبر الحساب - أرخص", callback_data="cat_acc_level")],
        [InlineKeyboardButton("✈️ إنزالات جوية", callback_data="cat_airdrop")],
        [InlineKeyboardButton("📞 تواصل معنا", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(kb)

def back_to_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="main")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 *متجرك المضمون لشحن فري فاير* 💎\n"
        "⚡ شحن سريع | آمن 100%\n\n"
        "اختر نوع الشحن:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id

    if data == "main":
        await start(update, context)
        return

    if data == "contact":
        await q.edit_message_text("📞 للتواصل والاستفسار:\nراسلنا هنا، وحنرد عليك في أسرع وقت.", reply_markup=back_to_main())
        return

    if data.startswith("cat_"):
        cat = data[4:]
        kb = []
        for i, (btn_text, name, price, method) in enumerate(PACKAGES[cat]):
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"item_{cat}_{i}")])
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="main")])
        await q.edit_message_text(f"{CATEGORY_NAMES[cat]}\n\nاختر الباقة:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("item_"):
        _, cat, idx = data.split("_")
        idx = int(idx)
        btn_text, name, price, method = PACKAGES[cat][idx]
        user_state[user_id] = {"name": name, "price": price, "method": method}
        kb = [
            [InlineKeyboardButton("🛒 اطلب الآن", callback_data="order_now")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=f"cat_{cat}")],
        ]
        txt = f"✅ *{name}*\n\n💰 السعر: *{price}*\n\n⚡ الدفع عبر بنكك\n✅ التسليم في دقائق"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "order_now":
        order = user_state.get(user_id)
        if not order:
            await q.edit_message_text("اختار باقة أولاً", reply_markup=back_to_main())
            return
        method = order["method"]
        txt = (
            f"🛒 *طلبك: {order['name']}*\n"
            f"💰 السعر: *{order['price']}*\n\n"
            f"💳 *حول القروش على بنكك:*\n"
            f"رقم الحساب: `{BANKK_NUMBER}`\n"
            f"الاسم: {BANKK_NAME}\n\n"
        )
        if method == "id":
            txt += (
                "بعد التحويل، رسل لينا في رسالة واحدة:\n"
                "1️⃣ صورة إشعار التحويل\n"
                "2️⃣ الـ ID حقك في اللعبة\n\n"
                "مثال:\nID: 123456789"
            )
        else:
            txt += (
                "بعد التحويل، رسل لينا في رسالة واحدة:\n"
                "1️⃣ صورة إشعار التحويل\n"
                "2️⃣ إيميل حساب فري فاير\n"
