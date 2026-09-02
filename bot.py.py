import asyncio
import secrets

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)


# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = "ВСТАВЬ_НОВЫЙ_ТОКЕН"

# ТВОЙ Telegram ID
ADMIN_ID = 1335121990

# ТВОЙ ЛИЧНЫЙ Telegram username БЕЗ @
GIFT_USERNAME = "@zxkssen5rp"

# Ссылка на Mini App
WEB_APP_URL = "https://fizshopka-git-main-fizshopka.vercel.app"


dp = Dispatcher()

# Заказы хранятся пока бот запущен
orders = {}


# ==================================================
# СТРАНЫ
# ==================================================

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


# ==================================================
# /start
# ==================================================

@dp.message(F.text.startswith("/start"))
async def start(message: Message):

    text = message.text.strip()

    # Просто /start
    if text == "/start":

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
            "⚡ Fizshopka\n\n"
            "Магазин физ номеров.\n\n"
            "Нажми кнопку ниже:",
            reply_markup=keyboard
        )

        return

    # /start buy_usa
    if text.startswith("/start buy_"):

        country_code = text.replace(
            "/start buy_", "", 1
        )

        if country_code not in COUNTRIES:

            await message.answer(
                "❌ Страна не найдена."
            )

            return

        country = COUNTRIES[country_code]

        order_id = secrets.token_hex(4).upper()

        orders[order_id] = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "country": country,
            "country_code": country_code,
            "status": "waiting_payment",
            "screenshots": 0,
            "number": None,
            "code": None,
        }

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎁 Как оплатить",
                        callback_data=f"payinfo_{order_id}"
                    )
                ]
            ]
        )

        await message.answer(
            f"📦 Заказ #{order_id}\n\n"
            f"{country}\n\n"
            f"🎁 Оплата:\n"
            f"💐 Букет — 50 ⭐\n"
            f"🌹 Роза — 25 ⭐\n\n"
            f"Итого: 75 ⭐",
            reply_markup=keyboard
        )

        return


# ==================================================
# КАК ОПЛАТИТЬ
# ==================================================

@dp.callback_query(F.data.startswith("payinfo_"))
async def payment_info(callback):

    order_id = callback.data.replace(
        "payinfo_", ""
    )

    if order_id not in orders:

        await callback.answer(
            "Заказ не найден.",
            show_alert=True
        )

        return

    order = orders[order_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Открыть профиль",
                    url=f"https://t.me/{GIFT_USERNAME}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил",
                    callback_data=f"paid_{order_id}"
                )
            ]
        ]
    )

    await callback.message.answer(
        f"🎁 Оплата заказа #{order_id}\n\n"
        f"{order['country']}\n\n"
        f"Отправьте на @{GIFT_USERNAME}:\n\n"
        f"💐 Букет — 50 ⭐\n"
        f"🌹 Роза — 25 ⭐\n\n"
        f"После отправки обоих подарков "
        f"нажмите «Я оплатил».",
        reply_markup=keyboard
    )

    await callback.answer()


# ==================================================
# Я ОПЛАТИЛ
# ==================================================

@dp.callback_query(F.data.startswith("paid_"))
async def paid_button(callback):

    order_id = callback.data.replace(
        "paid_", ""
    )

    if order_id not in orders:

        await callback.answer(
            "Заказ не найден.",
            show_alert=True
        )

        return

    order = orders[order_id]

    order["status"] = "waiting_screenshots"

    await callback.message.answer(
        f"📸 Заказ #{order_id}\n\n"
        f"Отправь сюда скриншоты оплаты.\n\n"
        f"Нужно показать отправку:\n"
        f"💐 Букета — 50 ⭐\n"
        f"🌹 Розы — 25 ⭐"
    )

    await callback.answer()


# ==================================================
# ПОЛУЧЕНИЕ СКРИНШОТОВ
# ==================================================

@dp.message(F.photo)
async def receive_photo(message: Message):

    user_id = message.from_user.id

    order_id = None

    for oid, order in orders.items():

        if (
            order["user_id"] == user_id
            and order["status"] == "waiting_screenshots"
        ):
            order_id = oid
            break

    if order_id is None:

        await message.answer(
            "❌ Сейчас нет заказа, "
            "ожидающего скриншоты."
        )

        return

    order = orders[order_id]

    order["screenshots"] += 1

    await message.answer(
        f"📸 Скриншот получен.\n"
        f"Всего получено: {order['screenshots']}\n\n"
        f"После отправки всех скриншотов "
        f"ожидайте проверки."
    )

    await bot_global.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"📸 НОВЫЙ СКРИНШОТ ОПЛАТЫ\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"{order['country']}\n\n"
            f"👤 ID: {order['user_id']}\n"
            f"👤 Username: "
            f"@{order['username'] or 'нет'}\n\n"
            f"Скриншотов: {order['screenshots']}\n\n"
            f"Проверь подарки на своём аккаунте.\n\n"
            f"Подтвердить:\n"
            f"/accept {order_id}\n\n"
            f"Отклонить:\n"
            f"/reject {order_id}"
        )
    )


# ==================================================
# /accept ORDER_ID
# ==================================================

@dp.message(F.text.startswith("/accept "))
async def accept_order(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:

        await message.answer(
            "Используй:\n"
            "/accept ORDER_ID"
        )

        return

    order_id = parts[1].upper()

    if order_id not in orders:

        await message.answer(
            "❌ Заказ не найден."
        )

        return

    order = orders[order_id]

    if order["status"] == "confirmed":

        await message.answer(
            "⚠️ Заказ уже подтверждён."
        )

        return

    order["status"] = "confirmed"

    await bot_global.send_message(
        order["user_id"],
        f"✅ Заказ #{order_id} подтверждён!\n\n"
        f"{order['country']}\n\n"
        f"🎁 Оплата проверена.\n"
        f"⏳ Ожидайте выдачи номера."
    )

    await message.answer(
        f"✅ Заказ #{order_id} подтверждён.\n"
        f"Покупатель уведомлён."
    )


# ==================================================
# /reject ORDER_ID
# ==================================================

@dp.message(F.text.startswith("/reject "))
async def reject_order(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:

        await message.answer(
            "Используй:\n"
            "/reject ORDER_ID"
        )

        return

    order_id = parts[1].upper()

    if order_id not in orders:

        await message.answer(
            "❌ Заказ не найден."
        )

        return

    order = orders[order_id]

    order["status"] = "rejected"

    await bot_global.send_message(
        order["user_id"],
        f"❌ Заказ #{order_id} не подтверждён.\n\n"
        f"Проверьте отправку подарков.\n\n"
        f"Если это ошибка, обратитесь в поддержку."
    )

    await message.answer(
        f"❌ Заказ #{order_id} отклонён."
    )


# ==================================================
# /send ORDER_ID NUMBER
# ==================================================

@dp.message(F.text.startswith("/send "))
async def send_number(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:

        await message.answer(
            "Используй:\n\n"
            "/send ORDER_ID NUMBER\n\n"
            "Например:\n"
            "/send A82F91C2 +123456789"
        )

        return

    order_id = parts[1].upper()
    number = parts[2]

    if order_id not in orders:

        await message.answer(
            "❌ Заказ не найден."
        )

        return

    order = orders[order_id]

    if order["status"] != "confirmed":

        await message.answer(
            "❌ Сначала подтверди оплату:\n\n"
            f"/accept {order_id}"
        )

        return

    order["number"] = number
    order["status"] = "number_sent"

    await bot_global.send_message(
        order["user_id"],
        f"📱 Номер для заказа #{order_id}\n\n"
        f"{order['country']}\n\n"
        f"Ваш номер:\n"
        f"{number}\n\n"
        f"⏳ Ожидайте код, если он потребуется."
    )

    await message.answer(
        f"✅ Номер отправлен покупателю.\n\n"
        f"Заказ: #{order_id}"
    )


# ==================================================
# /code ORDER_ID CODE
# ==================================================

@dp.message(F.text.startswith("/code "))
async def send_code(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:

        await message.answer(
            "Используй:\n\n"
            "/code ORDER_ID CODE\n\n"
            "Например:\n"
            "/code A82F91C2 12345"
        )

        return

    order_id = parts[1].upper()
    code = parts[2]

    if order_id not in orders:

        await message.answer(
            "❌ Заказ не найден."
        )

        return

    order = orders[order_id]

    order["code"] = code

    await bot_global.send_message(
        order["user_id"],
        f"🔐 Код для заказа #{order_id}\n\n"
        f"{order['country']}\n\n"
        f"Код:\n"
        f"`{code}`\n\n"
        f"⚠️ Никому не передавайте этот код.",
        parse_mode="Markdown"
    )

    await message.answer(
        f"✅ Код отправлен покупателю.\n\n"
        f"📦 Заказ: #{order_id}"
    )


# ==================================================
# ЗАПУСК
# ==================================================

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