import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI, Request
import uvicorn

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

users = {}
PRICE = 50
REF_BONUS = 20

@dp.message(Command("start"))
async def start(message: types.Message):
    args = message.text.split()
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrer": None, "invited": []}
    if len(args) > 1 and args[1].isdigit() and args[1] != user_id:
        ref = args[1]
        if ref in users and user_id not in users[ref]["invited"]:
            users[ref]["invited"].append(user_id)
            users[ref]["balance"] += REF_BONUS
            users[user_id]["referrer"] = ref
            await bot.send_message(ref, f"✅ +{REF_BONUS} ★ за нового участника!")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Купить доступ (50 ★)", callback_data="buy")],
            [InlineKeyboardButton(text="👥 Рефералы", callback_data="my_refs")],
            [InlineKeyboardButton(text="💳 Баланс", callback_data="balance")]
        ]
    )
    await message.answer(
        f"🔥 Приват с пресетами\nДоступ — 50 ★\nТвоя ссылка: https://t.me/{bot.get_me().username}?start={user_id}",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "buy")
async def buy(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    if users[uid]["balance"] >= PRICE:
        users[uid]["balance"] -= PRICE
        await callback.message.answer("✅ Доступ открыт! Ссылка на архив: ТВОЯ_ССЫЛКА")
    else:
        await callback.message.answer("❌ Не хватает ★. Приведи друга (20 ★).")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "my_refs")
async def my_refs(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    count = len(users[uid]["invited"])
    await callback.message.answer(f"👥 Привёл: {count} чел. Заработал: {count*REF_BONUS} ★")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "balance")
async def balance(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    await callback.message.answer(f"💳 Баланс: {users[uid]['balance']} ★")
    await callback.answer()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = "https://eagle-privat-bot.onrender.com/webhook"
    await bot.set_webhook(webhook_url)

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
