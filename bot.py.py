import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message

TOKEN = "8977327110:AAE5lzA_ht1lDgzJPe97JA0-TpeyyyscHrc"

dp = Dispatcher()


@dp.message()
async def echo(message: Message):
    await message.answer("Привет! Бот работает ✅")
async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())