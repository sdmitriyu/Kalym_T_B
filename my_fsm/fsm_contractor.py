from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import ContractorStates
from models import Contractor, Customer  # Предполагаем, что есть модель Order
from aiogram.filters import Command
from filters.match_filters import filter_orders_for_contractor
from keyboards import contact_kb, preview_kb

router = Router()

@router.message(F.text == "Добавить услугу")
async def start_register_contractor(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте фото.")
    await state.set_state(ContractorStates.photo_url)

@router.message(ContractorStates.photo_url)
async def process_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте ваше фото.")
        return
    largest_photo = message.photo[-1]
    photo_file_id = largest_photo.file_id
    await state.update_data(photo_url=photo_file_id)
    await message.answer("Введите ваше имя:")
    await state.set_state(ContractorStates.name)

@router.message(ContractorStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш телефон:", reply_markup=contact_kb)
    await state.set_state(ContractorStates.phone)

@router.message(ContractorStates.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text == "Ввести вручную":
        await message.answer("Введите номер телефона вручную:")
        return  # Не меняем состояние, ждем ввод
    else:
        phone = message.text
    
    await state.update_data(phone=phone)
    await message.answer("Опишите ваши услуги:\n\nПримеры: электрик, сантехник, уборка, ремонт, доставка\nПишите коротко, как в примерах.")
    await state.set_state(ContractorStates.services)

@router.message(ContractorStates.services)
async def process_services(message: Message, state: FSMContext):
    await state.update_data(services=message.text)
    await message.answer("Укажите территорию:\n\nПримеры: Москва, СПб, ул. Ленина, ул. Пушкина, Московская область, Краснодарский край\nПишите как в примерах, чтобы найти друг друга.")
    await state.set_state(ContractorStates.territory)

@router.message(ContractorStates.territory)
async def process_territory(message: Message, state: FSMContext):
    await state.update_data(territory=message.text)
    data = await state.get_data()
    
    # Показываем предпросмотр
    preview_text = (
        f"📋 Предпросмотр вашей услуги:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🔧 Услуги: {data['services']}\n"
        f"📍 Территория: {data['territory']}\n\n"
        f"Всё верно?"
    )
    await message.answer(preview_text, reply_markup=preview_kb())

@router.message(F.text == "Мои услуги")
async def show_my_services(message: Message):
    if message.from_user is None:
        return
    
    # Получаем услуги текущего пользователя
    services = await Contractor.filter(user_id=message.from_user.id)
    if not services:
        await message.answer("У вас пока нет добавленных услуг.")
        return
    
    for service in services:
        text = (
            f"🔧 Ваша услуга:\n\n"
            f"👤 Имя: {service.name}\n"
            f"📞 Телефон: {service.phone}\n"
            f"🔧 Услуги: {service.services}\n"
            f"📍 Территория: {service.territory}\n"
            f"📅 Создана: {service.created_at.strftime('%d.%m.%Y %H:%M')}"
        )
        await message.answer(text)

@router.message(F.text == "Показать заказы")
async def show_orders_for_contractor(message: Message):
    # Получаем данные подрядчика по user_id Telegram
    contractor = await Contractor.get(user_id=message.from_user.id)
    if not contractor:
        await message.answer("Сначала добавьте услугу, чтобы видеть подходящие заказы.")
        return
    # Получаем все заказы
    all_orders = await Customer.all()
    # Преобразуем объекты в dict для фильтра
    suitable_orders = filter_orders_for_contractor(contractor.__dict__, [order.__dict__ for order in all_orders])
    if not suitable_orders:
        await message.answer("Нет подходящих заказов по вашим услугам и территории.")
        return
    for order in suitable_orders:
        text = (
            f"Название: {order.get('order_title', '')}\n"
            f"Описание: {order.get('order_description', '')}\n"
            f"Оплата: {order.get('payment', '')}\n"
            f"Территория: {order.get('territory', '')}\n"
            f"Услуги: {order.get('services', '')}"
        )
        await message.answer(text)
