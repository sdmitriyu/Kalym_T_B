from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from better_profanity import profanity
from info import start_info
from keyboards import start_btn

router = Router()

# Команда для входа в режим "чат-доски"
@router.message(Command("start"))
async def enter_board(message: Message):
    await message.answer(text=start_info, reply_markup=start_btn)
    await message.answer("Вы вошли в чат-доску! Пишите свои сообщения, они будут видны всем.")

@router.message(F.text == "Руководство")
async def show_guide(message: Message):
    guide_text = """
📖 **Руководство по использованию бота**

**Для заказчиков:**
1. Нажмите "Создать заказ" и заполните все поля
2. Используйте "Мои заказы" для просмотра ваших заказов
3. "Показать услуги" - найти подходящих подрядчиков
4. "Показать рейтинг" - посмотреть рейтинги (бесплатно)
5. "Полный рейтинг" - детальные отзывы (платно)

**Для подрядчиков:**
1. Нажмите "Добавить услугу" и заполните профиль
2. Используйте "Мои услуги" для просмотра ваших услуг
3. "Показать заказы" - найти подходящие заказы

**Платные услуги:**
• Приватный чат - 50₽ (возврат если нет ответа 24ч)
• Показ номера - 100₽ (невозвратно)
• Комбо (чат + номер) - 135₽
• Полный рейтинг - 100₽/7 дней, 200₽/30 дней

**Подсказки:**
• Пишите услуги коротко: "электрик", "сантехник", "уборка"
• Территория: "Москва", "ул. Ленина", "Московская область"
• Это поможет найти друг друга!
    """
    await message.answer(guide_text)

# Обработчик сообщений для чат-доски убран - эхо-бот отключен
