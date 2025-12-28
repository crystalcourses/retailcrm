import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config
from bot.handlers import start, customers, orders

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=config.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(start.router)
    dp.include_router(customers.router)
    dp.include_router(orders.router)
    
    logger.info("Bot started")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")