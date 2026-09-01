import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    LabeledPrice,
    PreCheckoutQuery,
)

TOKEN = "8977327110:AAFXNHR_3jBNk7HrkcusxHeTPjeerJCCk8k"

WEB_APP_URL = "https://fizshopka-git-main-fizshopka.vercel.app"

dp = Dispatcher()


# =========================
# /start
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
        "Нажми кнопку ниже, чтобы открыть магазин:",
        reply_markup=keyboard
    )


# =========================
# ОПЛАТА 75 STARS
# =========================

async def send_stars_invoice(bot: Bot, user_id: int):

    prices = [
        LabeledPrice(
            label="🇺🇸 Номер США",
            amount=75
        )
    ]

    await bot.send_invoice(
        chat_id=user_id,
        title="🇺🇸 Номер США",
        description="Виртуальный номер США",
        payload="usa_number_75_stars",
        currency="XTR",
        prices=prices
    )


# =========================
# КНОПКА ИЗ MINI APP
# =========================

@dp.message(F.web_app_data)
async def web_app_data(message: Message, bot: Bot):

    if message.web_app_data.data == "buy_usa_number":

        await send_stars_invoice(
            bot,
            message.from_user.id
        )


# =========================
# PRE-CHECKOUT
# =========================

@dp.pre_checkout_query()
async def pre_checkout(
    query: PreCheckoutQuery,
    bot: Bot
):

    if query.invoice_payload != "usa_number_75_stars":
        await query.answer(
            ok=False,
            error_message="Ошибка заказа."
        )
        return

    await query.answer(ok=True)


# =========================
# УСПЕШНАЯ ОПЛАТА
# =========================

@dp.message(F.successful_payment)
async def successful_payment(message: Message):

    payment = message.successful_payment

    if payment.invoice_payload != "usa_number_75_stars":
        return

    await message.answer(
        "✅ Оплата успешно получена!\n\n"
        "Ваш заказ принят."
    )

    # ПОКА НОМЕРА НЕТ:
    # здесь позже добавим отправку купленного номера.


# =========================
# ЗАПУСК
# =========================

async def main():

    bot = Bot(token=TOKEN)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())