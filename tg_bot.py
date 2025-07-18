import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from arbitrage_checker import check_arbitrage

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("arbitrage"))
async def cmd_arbitrage(message: types.Message):
    await message.reply("⏳ Vérification arbitrage en cours...")
    result = check_arbitrage()
    await message.reply(result)

async def auto_alert():
    while True:
        result = check_arbitrage()
        if "ARBITRAGE" in result:  # alerte que si opportunité réelle
            await bot.send_message(TELEGRAM_CHAT_ID, f"🚨 ALERTE AUTO !\n\n{result}")
        await asyncio.sleep(60)  # Check toutes les 60s

async def main():
    asyncio.create_task(auto_alert())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
