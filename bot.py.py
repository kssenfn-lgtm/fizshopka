import asyncio
import secrets

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    LabeledPrice,
    PreCheckoutQuery,
)

TOKEN = "8977327110:AAGSUtOhzv2w3c0XDAmqTNu0JFNjpwVCKmc"

WEB_APP_URL = "https://fizshopka-git-main-fizshopka.vercel.app"

ADMIN_ID = 1335121990

dp = Dispatcher()

orders = {}


# =========================
# СТРАНЫ
# =========================

COUNTRIES = {
    "usa": "🇺🇸 США",
    "canada": "🇨🇦 Канада",
    "uk": "🇬🇧 Великобритания",
    "germany": "🇩🇪 Германия",
    "france": "🇫🇷 Франция",
    "italy": "🇮🇹 Италия",
    "spain": "🇪🇸 Испания",
    "netherlands": "🇳🇱 Нидерланды",
    "poland": "🇵🇱 Польша",
    "czech": "🇨🇿 Чехия",
    "turkey": "🇹🇷 Турция",
    "india": "🇮🇳 Индия",
    "indonesia": "🇮🇩 Индонезия",
    "brazil": "🇧🇷 Бразилия",
    "mexico": "🇲🇽 Мексика",
    "argentina": "🇦🇷 Аргентина",
    "australia": "🇦🇺 Австралия",
    "japan": "🇯🇵 Япония",
    "korea": "🇰🇷 Южная Корея",
}


# =========================
# /start
# =========================

@dp.message()
async def start_handler(message: Message):

    if not message.text:
        return

    # Обычный /start
    if message.text == "/start":

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛒 Открыть магазин",
                        web_app=WebAppInfo(url=WEB_APP_URL)
                    )
                ]
            ]
        )

        await message.answer(
            "Добро пожаловать в Fizshopka! 🛍️\n\n"
            "Нажми кнопку ниже, чтобы открыть магазин:",
            reply_markup=keyboard
        )

        return

    # /start buy_usa
    if message.text.startswith("/start buy_"):

        country_code = message.text.replace(
            "/start buy_", "", 1
        ).strip()

        if country_code not in COUNTRIES:
            await message.answer(
                "❌ Такой страны нет в магазине."
            )
            return

        country_name = COUNTRIES[country_code]

        order_id = secrets.token_hex(4)

        payload = f"order_{order_id}"

        orders[order_id] = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "country_code": country_code,
            "country": country_name,
            "paid": False,
            "number": None,
        }

        invoice_link = await bot_global.create_invoice_link(
            title=f"{country_name} номер",
            description=f"Виртуальный номер — {country_name}",
            payload=payload,
            currency="XTR",
            prices=[
                LabeledPrice(
                    label=f"{country_name} — номер",
                    amount=75
                )
            ]
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⭐ Оплатить 75 Stars",
                        url=invoice_link
                    )
                ]
            ]
        )

        await message.answer(
            f"📦 Заказ #{order_id}\n\n"
            f"{country_name}\n"
            f"⭐ Цена: 75 Stars\n\n"
            f"Нажми кнопку ниже для оплаты:",
            reply_markup=keyboard
        )


# =========================
# PRE-CHECKOUT
# =========================

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):

    print("PRE-CHECKOUT:", query.invoice_payload)

    if query.invoice_payload.startswith("order_"):

        order_id = query.invoice_payload.replace(
            "order_", "", 1
        )

        if order_id in orders:
            await query.answer(ok=True)
            return

    await query.answer(
        ok=False,
        error_message="Заказ не найден."
    )


# =========================
# УСПЕШНАЯ ОПЛАТА
# =========================

@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: Message):

    payment = message.successful_payment

    order_id = payment.invoice_payload.replace(
        "order_", "", 1
    )

    if order_id not in orders:

        await message.answer(
            "✅ Оплата получена.\n"
            "Но заказ не найден. Обратись в поддержку."
        )

        return

    order = orders[order_id]

    order["paid"] = True

    print("")
    print("================================")
    print("💰 ОПЛАТА УСПЕШНА!")
    print("Заказ:", order_id)
    print("Страна:", order["country"])
    print("Покупатель:", order["user_id"])
    print("Username:", order["username"])
    print("================================")
    print("")

    await message.answer(
        f"✅ Оплата успешно получена!\n\n"
        f"📦 Заказ: #{order_id}\n"
        f"{order['country']}\n"
        f"⭐ 75 Stars\n\n"
        f"⏳ Ожидайте выдачи номера."
    )

    if ADMIN_ID != 1335121990:

        await bot_global.send_message(
            ADMIN_ID,

            f"💰 НОВЫЙ ЗАКАЗ!\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"{order['country']}\n"
            f"⭐ Оплачено: 75 Stars\n\n"
            f"👤 ID: {order['user_id']}\n"
            f"👤 Username: @{order['username'] or 'нет'}\n\n"
            f"📱 Чтобы выдать номер:\n"
            f"/send {order_id} +XXXXXXXXXXX"
        )


# =========================
# ВЫДАТЬ НОМЕР
# =========================

@dp.message(lambda message: message.text and message.text.startswith("/send "))
async def send_number(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "❌ У тебя нет доступа."
        )

        return

    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:

        await message.answer(
            "❌ Неверный формат.\n\n"
            "Используй:\n"
            "/send НОМЕР_ЗАКАЗА НОМЕР\n\n"
            "Например:\n"
            "/send a1b2c3d4 +12025550123"
        )

        return

    order_id = parts[1]
    number = parts[2]

    if order_id not in orders:

        await message.answer(
            "❌ Такой заказ не найден."
        )

        return

    order = orders[order_id]

    if not order["paid"]:

        await message.answer(
            "❌ Этот заказ ещё не оплачен."
        )

        return

    if order["number"]:

        await message.answer(
            "⚠️ Для этого заказа номер уже был выдан."
        )

        return

    order["number"] = number

    await bot_global.send_message(
        order["user_id"],

        f"✅ Ваш заказ #{order_id} готов!\n\n"
        f"{order['country']}\n\n"
        f"📱 Ваш номер:\n"
        f"`{number}`\n\n"
        f"Спасибо за покупку ❤️",

        parse_mode="Markdown"
    )

    await message.answer(
        f"✅ Номер отправлен покупателю!\n\n"
        f"📦 Заказ: #{order_id}\n"
        f"{order['country']}"
    )


# =========================
# ПРОВЕРИТЬ ЗАКАЗ
# =========================

@dp.message(lambda message: message.text and message.text.startswith("/order "))
async def check_order(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "❌ У тебя нет доступа."
        )

        return

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:

        await message.answer(
            "Используй:\n"
            "/order НОМЕР_ЗАКАЗА"
        )

        return

    order_id = parts[1]

    if order_id not in orders:

        await message.answer(
            "❌ Заказ не найден."
        )

        return

    order = orders[order_id]

    number_status = (
        "✅ Выдан"
        if order["number"]
        else "⏳ Ожидает выдачи"
    )

    await message.answer(
        f"📦 Заказ #{order_id}\n\n"
        f"{order['country']}\n"
        f"⭐ 75 Stars\n"
        f"💰 Оплата: "
        f"{'✅' if order['paid'] else '❌'}\n"
        f"📱 Номер: {number_status}\n\n"
        f"👤 ID: {order['user_id']}\n"
        f"👤 Username: "
        f"@{order['username'] or 'нет'}"
    )


# =========================
# ЗАПУСК
# =========================

bot_global = None


async def main():

    global bot_global

    bot_global = Bot(token=TOKEN)

    print("================================")
    print("Fizshopka bot запущен!")
    print("================================")

    await dp.start_polling(bot_global)


if __name__ == "__main__":
    asyncio.run(main())