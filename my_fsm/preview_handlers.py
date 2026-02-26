from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import ContractorStates, CustomerStates
from models import Contractor, Customer
from keyboards import start_btn

router = Router()

@router.callback_query(F.data == "save_contractor_card")
async def save_contractor_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Сохраняем в БД
    contractor = await Contractor.create(
        photo_url=data['photo_url'],
        name=data['name'],
        phone=data['phone'],
        services=data['services'],
        territory=data['territory'],
        user_id=callback.from_user.id
    )
    
    await callback.message.edit_text("✅ Ваша услуга добавлена и видна всем по фильтрам территории и профиля услуги!")
    await callback.message.answer("Выберите действие:", reply_markup=start_btn)
    await state.clear()

@router.callback_query(F.data == "edit_contractor_card")
async def edit_contractor_card(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Что хотите изменить?\n\n1. Имя\n2. Телефон\n3. Услуги\n4. Территория\n\nНапишите номер пункта:")
    await state.set_state(ContractorStates.name)  # Начинаем заново

@router.callback_query(F.data == "save_customer_card")
async def save_customer_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Сохраняем в БД
    customer = await Customer.create(
        name=data['name'],
        order_title=data['order_title'],
        order_description=data['order_description'],
        payment=data['payment'],
        territory=data['territory'],
        services=data['services'],
        user_id=callback.from_user.id
    )
    
    await callback.message.edit_text("✅ Вы успешно зарегистрированы как заказчик!")
    await callback.message.answer("Выберите действие:", reply_markup=start_btn)
    await state.clear()

@router.callback_query(F.data == "edit_customer_card")
async def edit_customer_card(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Что хотите изменить?\n\n1. Имя\n2. Название заказа\n3. Описание заказа\n4. Оплата\n5. Территория\n6. Услуги\n\nНапишите номер пункта:")
    await state.set_state(CustomerStates.name)  # Начинаем заново
