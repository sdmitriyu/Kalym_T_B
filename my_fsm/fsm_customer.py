from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CustomerStates
from models import Customer, Contractor
from aiogram.filters import Command
from filters.match_filters import filter_services_for_customer
from keyboards import preview_customer_kb
from my_fsm.rating_system import rating_kb
from my_fsm.private_chat import private_chat_payment_kb

router = Router()

@router.message(F.text == "Создать заказ")
async def start_register_customer(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(CustomerStates.name)

@router.message(CustomerStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите название заказа:")
    await state.set_state(CustomerStates.order_title)

@router.message(CustomerStates.order_title)
async def process_order_title(message: Message, state: FSMContext):
    await state.update_data(order_title=message.text)
    await message.answer("Опишите заказ:")
    await state.set_state(CustomerStates.order_description)

@router.message(CustomerStates.order_description)
async def process_order_description(message: Message, state: FSMContext):
    await state.update_data(order_description=message.text)
    await message.answer("Укажите сумму оплаты:")
    await state.set_state(CustomerStates.payment)

@router.message(CustomerStates.payment)
async def process_payment(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("Пожалуйста, введите сумму числом.")
        return
    await state.update_data(payment=int(message.text))
    await message.answer("Укажите территорию:\n\nПримеры: Москва, СПб, ул. Ленина, ул. Пушкина, Московская область, Краснодарский край\nПишите как в примерах, чтобы найти друг друга.")
    await state.set_state(CustomerStates.territory)

@router.message(CustomerStates.territory)
async def process_territory(message: Message, state: FSMContext):
    await state.update_data(territory=message.text)
    await message.answer("Укажите нужные услуги:\n\nПримеры: электрик, сантехник, уборка, ремонт, доставка\nПишите коротко, как в примерах.")
    await state.set_state(CustomerStates.services)

@router.message(CustomerStates.services)
async def process_services(message: Message, state: FSMContext):
    await state.update_data(services=message.text)
    data = await state.get_data()
    
    # Показываем предпросмотр
    preview_text = (
        f"📋 Предпросмотр вашего заказа:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📝 Название: {data['order_title']}\n"
        f"📄 Описание: {data['order_description']}\n"
        f"💰 Оплата: {data['payment']} ₽\n"
        f"📍 Территория: {data['territory']}\n"
        f"🔧 Услуги: {data['services']}\n\n"
        f"Всё верно?"
    )
    await message.answer(preview_text, reply_markup=preview_customer_kb())

@router.message(F.text == "Мои заказы")
async def show_my_orders(message: Message):
    if message.from_user is None:
        return
    
    # Получаем заказы текущего пользователя
    orders = await Customer.filter(user_id=message.from_user.id)
    if not orders:
        await message.answer("У вас пока нет созданных заказов.")
        return
    
    for order in orders:
        text = (
            f"📝 Ваш заказ:\n\n"
            f"👤 Имя: {order.name}\n"
            f"📝 Название: {order.order_title}\n"
            f"📄 Описание: {order.order_description}\n"
            f"💰 Оплата: {order.payment} ₽\n"
            f"📍 Территория: {order.territory}\n"
            f"🔧 Услуги: {order.services}"
        )
        await message.answer(text)

@router.message(F.text == "Показать услуги")
async def show_services_for_customer(message: Message):
    # Получаем данные заказа заказчика по user_id Telegram
    if message.from_user is None:
        await message.answer("Не удалось определить пользователя.")
        return
    user_id = message.from_user.id
    order = await Customer.get(user_id=user_id)
    if not order:
        await message.answer("Сначала создайте заказ, чтобы видеть подходящие услуги.")
        return
    # Получаем все услуги подрядчиков
    all_services = await Contractor.all()
    suitable_services = filter_services_for_customer(order.__dict__, [service.__dict__ for service in all_services])
    if not suitable_services:
        await message.answer("Нет подходящих услуг по вашему заказу и территории.")
        return
    for service in suitable_services:
        text = (
            f"👤 Имя: {service.get('name', '')}\n"
            f"🔧 Услуги: {service.get('services', '')}\n"
            f"📍 Территория: {service.get('territory', '')}\n"
            f"📞 Телефон: [Скрыт - нужна оплата]\n\n"
            f"💬 Связаться с подрядчиком:"
        )
        await message.answer(text, reply_markup=private_chat_payment_kb(service.get('id')))
