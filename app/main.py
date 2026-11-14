import os
import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
CallbackQueryHandler,
ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

db = sqlite3.connect("dripcases.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
user_id INTEGER PRIMARY KEY,
username TEXT,
balance INTEGER DEFAULT 1000
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
item TEXT,
rarity TEXT
)
""")
db.commit()

CASES = {
"basic": {
"price": 100,
"items": [
("Nike Hoodie", "Common"),
("Adidas Pants", "Common"),
("Jordan Sneakers", "Rare"),
("Supreme Hoodie", "Epic")
]
},
"premium": {
"price": 500,
"items": [
("Nike Tech Fleece", "Rare"),
("Jordan 4", "Epic"),
("Balenciaga Sneakers", "Legendary"),
("Chrome Hearts Hoodie", "Legendary")
]
}
}

def register(user):
cursor.execute(
"INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
(user.id, user.username or user.first_name)
)
db.commit()

def get_balance(user_id):
cursor.execute(
"SELECT balance FROM players WHERE user_id=?",
(user_id,)
)
result = cursor.fetchone()
return result[0] if result else 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
register(user)

keyboard = [
    [InlineKeyboardButton("📦 Кейсы", callback_data="cases")],
    [InlineKeyboardButton("👕 Инвентарь", callback_data="inventory")],
    [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
]

await update.message.reply_text(
    f"🔥 DRIP CASES 2.0\n\n"
    f"Добро пожаловать, {user.first_name}!\n"
    f"💰 Баланс: {get_balance(user.id)} DC",
    reply_markup=InlineKeyboardMarkup(keyboard)
)
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

user_id = query.from_user.id
register(query.from_user)

if query.data == "cases":
    keyboard = [
        [InlineKeyboardButton("📦 Basic — 100 DC", callback_data="basic")],
        [InlineKeyboardButton("💎 Premium — 500 DC", callback_data="premium")]
    ]
    await query.edit_message_text(
        "Выбери кейс:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

elif query.data in CASES:
    case = CASES[query.data]
    balance = get_balance(user_id)

    if balance < case["price"]:
        await query.edit_message_text("❌ Недостаточно DC!")
        return

    cursor.execute(
        "UPDATE players SET balance=balance-? WHERE user_id=?",
        (case["price"], user_id)
    )

    item, rarity = random.choice(case["items"])

    cursor.execute(
        "INSERT INTO inventory (user_id, item, rarity) VALUES (?, ?, ?)",
        (user_id, item, rarity)
    )
    db.commit()

    await query.edit_message_text(
        f"🎉 КЕЙС ОТКРЫТ!\n\n"
        f"👕 Предмет: {item}\n"
        f"💎 Редкость: {rarity}\n"
        f"💰 Баланс: {get_balance(user_id)} DC"
    )

elif query.data == "profile":
    await query.edit_message_text(
        f"👤 Профиль\n\n"
        f"ID: {user_id}\n"
        f"💰 Баланс: {get_balance(user_id)} DC"
    )

elif query.data == "inventory":
    cursor.execute(
        "SELECT item, rarity FROM inventory WHERE user_id=?",
        (user_id,)
    )
    items = cursor.fetchall()

    if not items:
        text = "Инвентарь пуст."
    else:
        text = "👕 ТВОЙ ИНВЕНТАРЬ\n\n"
        for item, rarity in items:
            text += f"• {item} — {rarity}\n"

    await query.edit_message_text(text)
async def main():
if not TOKEN:
raise RuntimeError("Не задан BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("DRIP CASES 2.0 запущен!")
await app.initialize()
await app.start()
await app.updater.start_polling()
await app.updater.idle()
if name == "main":
import asyncio
asyncio.run(main())
