from aiogram.types import Message
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path

# Routers
from handlers import router as handlers_router
from my_fsm.fsm_customer import router as fsm_customer_router
from my_fsm.fsm_contractor import router as fsm_contractor_router
from my_fsm.edit_customer import router as edit_customer_router
from my_fsm.edit_contractor import router as edit_contractor_router
from my_fsm.preview_handlers import router as preview_handlers_router
from my_fsm.rating_system import router as rating_system_router
from my_fsm.private_chat import router as private_chat_router

# DB init
from models import init as init_db

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

print("TOKEN from env:", os.getenv("TOKEN"))

token = os.getenv("TOKEN")
if token is None:
    raise ValueError("TOKEN not found in environment variables")

bot = Bot(token=token)
dp = Dispatcher()

# Register routers
dp.include_router(handlers_router)
dp.include_router(fsm_customer_router)
dp.include_router(fsm_contractor_router)
dp.include_router(edit_customer_router)
dp.include_router(edit_contractor_router)
dp.include_router(preview_handlers_router)
dp.include_router(rating_system_router)
dp.include_router(private_chat_router)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__=="__main__":
    try:
        asyncio.run(main())
    except Exception:
        print("Бот выключен")