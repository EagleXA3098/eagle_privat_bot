import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

users = {}
PRICE = 50
REF_BONUS = 20

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrer": None, "invited": []}
    if args and args.isdigit() and args != user_id:
        ref = args
        if ref in users and user_id not in users[ref]["invited"]:
            users[ref]["invited"].append(user_id)
            users[ref]["balance"] += REF_BONUS
            users[user_id]["referrer"] = ref
            await bot.send_message(ref, f"✅ +{REF_BONUS} ★ за нового участника!")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💰 Купить доступ (50 ★)", callback_data="buy"),
        InlineKeyboardButton("👥 Рефералы", callback_data="my_refs"),
        InlineKeyboardButton("💳 Баланс", callback_data="balance")
    )
    await message.answer(
        "🔥 Приват с пресетами\nДоступ — 50 ★\nТвоя ссылка: https://t.me/"+bot.get_me().username+"?start="+user_id,
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "buy")
async def buy(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    if users[uid]["balance"] >= PRICE:
        users[uid]["balance"] -= PRICE
        await callback.message.answer("✅ Доступ открыт! Ссылка на архив: ТВОЯ_ССЫЛКА")
    else:
        await callback.message.answer("❌ Не хватает ★. Приведи друга (20 ★).")

@dp.callback_query_handler(lambda c: c.data == "my_refs")
async def my_refs(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    count = len(users[uid]["invited"])
    await callback.message.answer(f"👥 Привёл: {count} чел. Заработал: {count*REF_BONUS} ★")

@dp.callback_query_handler(lambda c: c.data == "balance")
async def balance(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    await callback.message.answer(f"💳 Баланс: {users[uid]['balance']} ★")

if name == "main":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
