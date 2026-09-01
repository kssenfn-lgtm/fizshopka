import asyncio
import secrets

from aiogram import Bot, Dispatcher, F
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

# ВСТАВЬ СЮДА СВОЙ TELEGRAM ID
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
# START
# =========================

@dp.message(F.text == "/start")
async def start(message: Message):

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
        "Выбери номер в магазине:",
        reply_markup=keyboard
    )


# =========================
# PRE-CHECKOUT
# =========================

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):

    print("PRE-CHECKOUT:", query.invoice_payload)

    if query.invoice_payload.startswith("order_"):
        await query.answer(ok=True)
    else:
        await query.answer(
            ok=False,
            error_message="Неизвестный заказ."
        )


# =========================
# УСПЕШНАЯ ОПЛАТА
# =========================

@dp.message(F.successful_payment)
async def successful_payment(message: Message):

    payment = message.successful_payment

    order_id = payment.invoice_payload.replace("order_", "")

    if order_id not in orders:
        await message.answer(
            "✅ Оплата получена, но заказ не найден. "
            "Обратись в поддержку."
        )
        return

    order = orders[order_id]

    order["paid"] = True

    country = order["country"]

    print("================================")
    print("ОПЛАТА УСПЕШНА!")
    print("Заказ:", order_id)
    print("Страна:", country)
    print("Покупатель:", message.from_user.id)
    print("Username:", message.from_user.username)
    print("================================")

    await message.answer(
        f"✅ Оплата успешно получена!\n\n"
        f"📦 Заказ: #{order_id}\n"
        f"{country}\n"
        f"⭐ 75 Stars\n\n"
        f"⏳ Номер будет выдан после обработки заказа."
    )

    if ADMIN_ID != 1335121990:

        await bot_global.send_message(
            ADMIN_ID,
            f"💰 НОВЫЙ ЗАКАЗ\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"{country}\n"
            f"⭐ Оплачено: 75 Stars\n\n"
            f"👤 ID: {message.from_user.id}\n"
            f"👤 Username: @{message.from_user.username or 'нет'}\n\n"
            f"Чтобы выдать номер:\n"
            f"/send {order_id} +XXXXXXXXXXX"
        )


# =========================
# ВЫДАЧА НОМЕРА
# =========================

@dp.message(F.text.startswith("/send "))
async def send_number(message: Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет доступа.")
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:
        await message.answer(
            "Использование:\n\n"
            "/send НОМЕР_ЗАКАЗА НОМЕР\n\n"
            "Например:\n"
            "/send a1b2c3d4 +12025550123"
        )
        return

    order_id = parts[1]
    number = parts[2]

    if order_id not in orders:
        await message.answer("❌ Такой заказ не найден.")
        return

    order = orders[order_id]

    if not order["paid"]:
        await message.answer("❌ Этот заказ ещё не оплачен.")
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
        f"✅ Номер отправлен покупателю.\n\n"
        f"📦 Заказ: #{order_id}\n"
        f"{order['country']}"
    )


# =========================
# ПРОВЕРКА ЗАКАЗА
# =========================

@dp.message(F.text.startswith("/order "))
async def check_order(message: Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет доступа.")
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        await message.answer(
            "Использование:\n"
            "/order НОМЕР_ЗАКАЗА"
        )
        return

    order_id = parts[1]

    if order_id not in orders:
        await message.answer("❌ Заказ не найден.")
        return

    order = orders[order_id]

    if order["number"]:
        status = "✅ Номер выдан"
    else:
        status = "⏳ Номер ещё не выдан"

    await message.answer(
        f"📦 Заказ #{order_id}\n\n"
        f"{order['country']}\n"
        f"⭐ 75 Stars\n"
        f"💰 Оплата: {'✅' if order['paid'] else '❌'}\n"
        f"📱 {status}\n\n"
        f"👤 ID: {order['user_id']}"
    )


# =========================
# СОЗДАНИЕ ЗАКАЗА
# =========================

async def create_invoice(bot: Bot, country_code: str):

    order_id = secrets.token_hex(4)

    country_name = COUNTRIES[country_code]

    payload = f"order_{order_id}"

    invoice_link = await bot.create_invoice_link(
        title=f"{country_name} номер",
        description=f"Виртуальный номер: {country_name}",
        payload=payload,
        currency="XTR",
        prices=[
            LabeledPrice(
                label=f"{country_name} — номер",
                amount=75
            )
        ]
    )

    return order_id, invoice_link


# =========================
# КОМАНДА ДЛЯ СОЗДАНИЯ ТЕСТОВОГО INVOICE
# =========================

@dp.message(F.text == "/invoice")
async def invoice_command(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    order_id, link = await create_invoice(
        bot_global,
        "usa"
    )

    await message.answer(
        f"Invoice создан.\n\n"
        f"Заказ: #{order_id}\n\n"
        f"{link}"
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