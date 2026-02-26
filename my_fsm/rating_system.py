from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models import Contractor, Customer, Rating_Cont, Payment, Purchase
from datetime import datetime, timedelta
import asyncio

router = Router()

# Клавиатуры для рейтинга
def rating_kb(contractor_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 1", callback_data=f"rate_1_{contractor_id}")],
            [InlineKeyboardButton(text="⭐⭐ 2", callback_data=f"rate_2_{contractor_id}")],
            [InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data=f"rate_3_{contractor_id}")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data=f"rate_4_{contractor_id}")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data=f"rate_5_{contractor_id}")]
        ]
    )

def rating_pass_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купить доступ 7 дней - 100₽", callback_data="buy_rating_7")],
            [InlineKeyboardButton(text="💳 Купить доступ 30 дней - 200₽", callback_data="buy_rating_30")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_rating")]
        ]
    )

# Показать рейтинг подрядчика (бесплатно)
@router.message(F.text == "Показать рейтинг")
async def show_rating(message: Message):
    if message.from_user is None:
        return
    
    # Получаем всех подрядчиков
    contractors = await Contractor.all()
    if not contractors:
        await message.answer("Пока нет подрядчиков.")
        return
    
    text = "📊 Рейтинги подрядчиков:\n\n"
    for contractor in contractors:
        # Получаем рейтинги
        ratings = await Rating_Cont.filter(contractor=contractor)
        if ratings:
            avg_score = sum(r.score for r in ratings) / len(ratings)
            count = len(ratings)
            text += f"👤 {contractor.name}\n"
            text += f"⭐ {avg_score:.1f} ({count} отзывов)\n"
            text += f"🔧 {contractor.services}\n"
            text += f"📍 {contractor.territory}\n\n"
        else:
            text += f"👤 {contractor.name}\n"
            text += f"⭐ Нет оценок\n"
            text += f"🔧 {contractor.services}\n"
            text += f"📍 {contractor.territory}\n\n"
    
    text += "\n💡 Для просмотра полных отзывов нужен платный доступ."
    await message.answer(text, reply_markup=rating_pass_kb())

# Показать полный рейтинг (платно)
@router.message(F.text == "Полный рейтинг")
async def show_full_rating(message: Message):
    if message.from_user is None:
        return
    
    # Проверяем доступ
    user_id = message.from_user.id
    active_purchase = await Purchase.filter(
        user_id=user_id,
        product="rating_pass",
        expires_at__gt=datetime.now()
    ).first()
    
    if not active_purchase:
        await message.answer("❌ У вас нет доступа к полному рейтингу. Купите доступ для просмотра всех отзывов.")
        return
    
    # Получаем всех подрядчиков с полными рейтингами
    contractors = await Contractor.all()
    if not contractors:
        await message.answer("Пока нет подрядчиков.")
        return
    
    text = "📊 Полные рейтинги подрядчиков:\n\n"
    for contractor in contractors:
        ratings = await Rating_Cont.filter(contractor=contractor).order_by('-created_at')
        if ratings:
            avg_score = sum(r.score for r in ratings) / len(ratings)
            count = len(ratings)
            text += f"👤 {contractor.name}\n"
            text += f"⭐ {avg_score:.1f} ({count} отзывов)\n"
            text += f"🔧 {contractor.services}\n"
            text += f"📍 {contractor.territory}\n"
            
            # Показываем последние 3 отзыва
            text += "📝 Последние отзывы:\n"
            for rating in ratings[:3]:
                text += f"  • {rating.score}⭐ - {rating.comment or 'Без комментария'}\n"
            text += "\n"
        else:
            text += f"👤 {contractor.name}\n"
            text += f"⭐ Нет оценок\n"
            text += f"🔧 {contractor.services}\n"
            text += f"📍 {contractor.territory}\n\n"
    
    await message.answer(text)

# Оценить подрядчика
@router.callback_query(F.data.startswith("rate_"))
async def rate_contractor(callback: CallbackQuery):
    if callback.from_user is None:
        return
    
    # Парсим данные
    parts = callback.data.split("_")
    score = int(parts[1])
    contractor_id = int(parts[2])
    
    # Получаем подрядчика
    contractor = await Contractor.get_or_none(id=contractor_id)
    if not contractor:
        await callback.answer("❌ Подрядчик не найден.")
        return
    
    # Проверяем, не оценивал ли уже этот пользователь
    existing_rating = await Rating_Cont.filter(
        contractor=contractor,
        user_id=callback.from_user.id
    ).first()
    
    if existing_rating:
        await callback.answer("❌ Вы уже оценили этого подрядчика.")
        return
    
    # Создаем оценку
    await Rating_Cont.create(
        contractor=contractor,
        score=score,
        user_id=callback.from_user.id
    )
    
    await callback.answer(f"✅ Оценка {score}⭐ сохранена!")
    await callback.message.edit_text("✅ Спасибо за оценку! Хотите добавить комментарий? (Напишите текст или отправьте 'Пропустить')")

# Покупка доступа к рейтингу
@router.callback_query(F.data.startswith("buy_rating_"))
async def buy_rating_access(callback: CallbackQuery):
    if callback.from_user is None:
        return
    
    days = int(callback.data.split("_")[2])
    amount = 100 if days == 7 else 200
    
    # Здесь должна быть интеграция с YooKassa
    # Пока просто создаем покупку
    expires_at = datetime.now() + timedelta(days=days)
    await Purchase.create(
        user_id=callback.from_user.id,
        product="rating_pass",
        expires_at=expires_at
    )
    
    await callback.answer(f"✅ Доступ к рейтингу на {days} дней активирован!")
    await callback.message.edit_text(f"✅ Доступ к полному рейтингу на {days} дней активирован!\n\nТеперь вы можете использовать команду 'Полный рейтинг' для просмотра всех отзывов.")

@router.callback_query(F.data == "cancel_rating")
async def cancel_rating(callback: CallbackQuery):
    await callback.message.edit_text("❌ Покупка отменена.")
