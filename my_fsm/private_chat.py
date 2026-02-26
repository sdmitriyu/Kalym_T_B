from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models import Contractor, Customer, Deal, Payment, Purchase
from datetime import datetime, timedelta
import asyncio

router = Router()

# Клавиатуры для приватных чатов
def private_chat_payment_kb(contractor_id: int):
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text="💳 Оплатить 50₽ за приватный чат", callback_data=f"pay_chat_{contractor_id}")],
			[InlineKeyboardButton(text="📞 Показать номер за 100₽", callback_data=f"pay_contact_{contractor_id}")],
			[InlineKeyboardButton(text="📦 5 номеров за 400₽", callback_data=f"buy_contact_pack_5")],
			[InlineKeyboardButton(text="💎 Чат + номер за 135₽", callback_data=f"pay_combo_{contractor_id}")],
			[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
		]
	)

def private_chat_actions_kb(deal_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отказаться", callback_data=f"decline_deal_{deal_id}")],
            [InlineKeyboardButton(text="✅ Завершить услугу", callback_data=f"complete_deal_{deal_id}")],
            [InlineKeyboardButton(text="⭐ Оценить", callback_data=f"rate_deal_{deal_id}")]
        ]
    )

# Создать приватный чат
@router.callback_query(F.data.startswith("create_chat_"))
async def create_private_chat(callback: CallbackQuery):
    if callback.from_user is None:
        return
    
    contractor_id = int(callback.data.split("_")[2])
    contractor = await Contractor.get_or_none(id=contractor_id)
    
    if not contractor:
        await callback.answer("❌ Подрядчик не найден.")
        return
    
    # Проверяем, есть ли уже активная сделка
    existing_deal = await Deal.filter(
        contractor=contractor,
        customer_id=callback.from_user.id,
        status__in=["waiting", "active"]
    ).first()
    
    if existing_deal:
        await callback.answer("❌ У вас уже есть активная сделка с этим подрядчиком.")
        return
    
    text = (
        f"💬 Приватный чат с {contractor.name}\n\n"
        f"🔧 Услуги: {contractor.services}\n"
        f"📍 Территория: {contractor.territory}\n\n"
        f"Выберите способ связи:"
    )
    
    await callback.message.edit_text(text, reply_markup=private_chat_payment_kb(contractor_id))

# Оплата приватного чата
@router.callback_query(F.data.startswith("pay_chat_"))
async def pay_private_chat(callback: CallbackQuery):
    if callback.from_user is None:
        return
    
    contractor_id = int(callback.data.split("_")[2])
    contractor = await Contractor.get_or_none(id=contractor_id)
    
    if not contractor:
        await callback.answer("❌ Подрядчик не найден.")
        return
    
    # Здесь должна быть интеграция с YooKassa
    # Пока просто создаем сделку
    deal = await Deal.create(
        contractor=contractor,
        customer_id=callback.from_user.id,
        status="active"
    )
    
    # Создаем запись о платеже
    await Payment.create(
        user_id=callback.from_user.id,
        deal_id=deal.id,
        product="private_chat",
        amount=5000,  # 50₽ в копейках
        status="completed",
        completed_at=datetime.now()
    )
    
    text = (
        f"✅ Приватный чат с {contractor.name} открыт!\n\n"
        f"💰 Оплачено: 50₽\n"
        f"⏰ Если подрядчик не ответит в течение 24 часов, деньги вернутся автоматически.\n\n"
        f"Теперь вы можете общаться в этом чате."
    )
    
    await callback.message.edit_text(text, reply_markup=private_chat_actions_kb(deal.id))

# Оплата показа контакта (с учётом пакета)
@router.callback_query(F.data.startswith("pay_contact_"))
async def pay_show_contact(callback: CallbackQuery):
	if callback.from_user is None:
		return
	
	contractor_id = int(callback.data.split("_")[2])
	contractor = await Contractor.get_or_none(id=contractor_id)
	
	if not contractor:
		await callback.answer("❌ Подрядчик не найден.")
		return
	
	# Сначала пробуем списать из пакета
	pack = await Purchase.filter(user_id=callback.from_user.id, product="contact_pack_5", remaining_uses__gt=0).first()
	if pack:
		pack.remaining_uses -= 1  # type: ignore
		await pack.save()
		text = (
			f"📞 Контакт {contractor.name}:\n\n"
			f"📱 Телефон: {contractor.phone}\n\n"
			f"📦 Осталось в пакете: {pack.remaining_uses}"
		)
		await callback.message.edit_text(text)
		return
	
	# Иначе — разовый показ за 100₽ (заглушка оплаты)
	await Payment.create(
		user_id=callback.from_user.id,
		product="show_contact",
		amount=10000,  # 100₽ в копейках
		status="completed",
		completed_at=datetime.now()
	)
	
	text = (
		f"📞 Контакт {contractor.name}:\n\n"
		f"📱 Телефон: {contractor.phone}\n\n"
		f"💳 Оплачено: 100₽\n"
		f"⚠️ Возврат невозможен после раскрытия контакта."
	)
	
	await callback.message.edit_text(text)

# Покупка пакета 5 номеров
@router.callback_query(F.data == "buy_contact_pack_5")
async def buy_contact_pack_5(callback: CallbackQuery):
	if callback.from_user is None:
		return
	
	# Заглушка YooKassa — просто создаём покупку
	await Payment.create(
		user_id=callback.from_user.id,
		product="contact_pack_5",
		amount=40000,  # 400₽ в копейках
		status="completed",
		completed_at=datetime.now()
	)
	
	# Активируем пакет на аккаунте
	pack = await Purchase.filter(user_id=callback.from_user.id, product="contact_pack_5").first()
	if not pack:
		await Purchase.create(user_id=callback.from_user.id, product="contact_pack_5", remaining_uses=5)
	else:
		# если уже есть, докинем ещё 5
		pack.remaining_uses = (pack.remaining_uses or 0) + 5
		await pack.save()
	
	await callback.answer("✅ Пакет из 5 номеров активирован!")
	await callback.message.edit_text("✅ Покупка успешна. Теперь вы можете раскрывать номера из пакета.")

# Оплата комбо (чат + контакт)
@router.callback_query(F.data.startswith("pay_combo_"))
async def pay_combo(callback: CallbackQuery):
    if callback.from_user is None:
        return
    
    contractor_id = int(callback.data.split("_")[2])
    contractor = await Contractor.get_or_none(id=contractor_id)
    
    if not contractor:
        await callback.answer("❌ Подрядчик не найден.")
        return
    
    # Создаем сделку
    deal = await Deal.create(
        contractor=contractor,
        customer_id=callback.from_user.id,
        status="active"
    )
    
    # Создаем запись о платеже
    await Payment.create(
        user_id=callback.from_user.id,
        deal_id=deal.id,
        product="combo",
        amount=13500,  # 135₽ в копейках
        status="completed",
        completed_at=datetime.now()
    )
    
    text = (
        f"💎 Комбо-доступ к {contractor.name}:\n\n"
        f"📱 Телефон: {contractor.phone}\n"
        f"💬 Приватный чат: открыт\n\n"
        f"💰 Оплачено: 135₽ (экономия 15₽)\n"
        f"⏰ Если подрядчик не ответит в чате в течение 24 часов, деньги вернутся автоматически."
    )
    
    await callback.message.edit_text(text, reply_markup=private_chat_actions_kb(deal.id))

# Отмена платежа
@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    await callback.message.edit_text("❌ Платеж отменен.")

# Завершить сделку
@router.callback_query(F.data.startswith("complete_deal_"))
async def complete_deal(callback: CallbackQuery):
    deal_id = int(callback.data.split("_")[2])
    deal = await Deal.get_or_none(id=deal_id)
    
    if not deal:
        await callback.answer("❌ Сделка не найдена.")
        return
    
    deal.status = "finished"
    deal.finished_at = datetime.now()
    await deal.save()
    
    await callback.message.edit_text("✅ Услуга завершена! Спасибо за использование нашего сервиса.")

# Отказаться от сделки
@router.callback_query(F.data.startswith("decline_deal_"))
async def decline_deal(callback: CallbackQuery):
    deal_id = int(callback.data.split("_")[2])
    deal = await Deal.get_or_none(id=deal_id)
    
    if not deal:
        await callback.answer("❌ Сделка не найдена.")
        return
    
    deal.status = "declined"
    deal.finished_at = datetime.now()
    await deal.save()
    
    await callback.message.edit_text("❌ Сделка отменена. Приватный чат закрыт.")

# Оценить сделку
@router.callback_query(F.data.startswith("rate_deal_"))
async def rate_deal(callback: CallbackQuery):
    deal_id = int(callback.data.split("_")[2])
    deal = await Deal.get_or_none(id=deal_id)
    
    if not deal:
        await callback.answer("❌ Сделка не найдена.")
        return
    
    # Здесь можно добавить логику оценки
    await callback.answer("⭐ Оценка будет добавлена в следующей версии.")
