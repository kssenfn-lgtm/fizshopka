import asyncio
import secrets

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

TOKEN = "8977327110:AAGSUtOhzv2w3c0XDAmqTNu0JFNjpwVCKmc"

ADMIN_ID = 1335121990

# ТВОЙ ЛИЧНЫЙ TELEGRAM USERNAME БЕЗ @
GIFT_USERNAME = "@zxkssen5rp"

WEB_APP_URL = "https://fizshopka-git-main-fizshopka.vercel.app"

dp = Dispatcher()

orders = {}


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

@dp.message(F.text)
async def message_handler(message: Message):

    text = message.text.strip()

    # Обычный /start
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
            "Магазин виртуальных номеров.\n\n"
            "Открой магазин кнопкой ниже.",
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
            f"🎁 Оплата подарками:\n"
            f"💐 Букет — 50 ⭐\n"
            f"🌹 Роза — 25 ⭐\n\n"
            f"Итого: 75 ⭐\n\n"
            f"После отправки подарков нажми «Я оплатил».",
            reply_markup=keyboard
        )

        return

    # /accept ORDER
    if text.startswith("/accept "):

        if message.from_user.id != ADMIN_ID:
            return

        order_id = text.split(maxsplit=1)[1].upper()

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

        return

    # /reject ORDER
    if text.startswith("/reject "):

        if message.from_user.id != ADMIN_ID:
            return

        order_id = text.split(maxsplit=1)[1].upper()

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
            f"Проверьте отправку подарков:\n"
            f"💐 Букет — 50 ⭐\n"
            f"🌹 Роза — 25 ⭐\n\n"
            f"Если это ошибка, обратитесь в поддержку."
        )

        await message.answer(
            f"❌ Заказ #{order_id} отклонён."
        )

        return

    # /send ORDER NUMBER
    if text.startswith("/send "):

        if message.from_user.id != ADMIN_ID:
            return

        parts = text.split(maxsplit=2)

        if len(parts) != 3:

            await message.answer(
                "Используй:\n"
                "/send ORDER_ID NUMBER"
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
                "❌ Сначала подтверди оплату командой:\n"
                f"/accept {order_id}"
            )

            return

        order["number"] = number
        order["status"] = "completed"

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
            f"Заказ: #{order_id}"
        )

        return


# =========================
# КНОПКА «КАК ОПЛАТИТЬ»
# =========================

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
                    text="🎁 Открыть мой профиль",
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
        f"Товар: {order['country']}\n\n"
        f"Отправьте на @{GIFT_USERNAME}:\n\n"
        f"💐 Букет — 50 ⭐\n"
        f"🌹 Роза — 25 ⭐\n\n"
        f"После этого нажмите «Я оплатил».\n\n"
        f"⚠️ Не нажимайте кнопку до фактической отправки подарков.",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# ПОКУПАТЕЛЬ НАЖАЛ «Я ОПЛАТИЛ»
# =========================

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

    if order["status"] == "confirmed":

        await callback.answer(
            "Заказ уже подтверждён.",
            show_alert=True
        )

        return

    order["status"] = "waiting_screenshots"

    await callback.message.answer(
        f"📸 Заказ #{order_id}\n\n"
        f"Теперь отправь сюда **скриншоты** "
        f"отправленных подарков.\n\n"
        f"Нужно показать:\n"
        f"💐 Букет — 50 ⭐\n"
        f"🌹 Роза — 25 ⭐",
        parse_mode="Markdown"
    )

    await callback.answer()


# =========================
# ПОЛУЧЕНИЕ ФОТО
# =========================

@dp.message(F.photo)
async def receive_photo(message: Message):

    user_id = message.from_user.id

    found_order = None

    for order_id, order in orders.items():

        if order["user_id"] == user_id and order["status"] == "waiting_screenshots":
            found_order = order_id
            break

    if not found_order:

        await message.answer(
            "❌ Сейчас нет заказа, ожидающего скриншоты."
        )

        return

    order = orders[found_order]

    order["screenshots"] += 1

    await message.answer(
        f"📸 Скриншот {order['screenshots']} получен.\n\n"
        f"Отправь второй скриншот, если он есть."
    )

    await bot_global.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"📸 СКРИНШОТ ОПЛАТЫ\n\n"
            f"📦 Заказ: #{found_order}\n"
            f"{order['country']}\n\n"
            f"👤 ID: {order['user_id']}\n"
            f"👤 Username: @{order['username'] or 'нет'}\n\n"
            f"Скриншотов получено: {order['screenshots']}\n\n"
            f"Проверить подарки на аккаунте.\n\n"
            f"Если всё верно:\n"
            f"/accept {found_order}\n\n"
            f"Если неверно:\n"
            f"/reject {found_order}"
        )
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