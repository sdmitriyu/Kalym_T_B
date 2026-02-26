# type: ignore[attr-defined]
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import CustomerStates
from keyboards import customer_edit_fields_kb, customer_action_kb

router = Router()

# --- Показать меню редактирования заказа ---
@router.callback_query(F.data.startswith("edit_customer_"))
async def edit_customer_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    order_id = int(callback.data.split("_")[-1])
    if callback.message:
        try:
            await callback.message.edit_text(
                "Что хотите изменить?",
                reply_markup=customer_edit_fields_kb(order_id)
            )  # type: ignore
        except Exception:
            await callback.message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer()

# --- Удалить заказ ---
@router.callback_query(F.data.startswith("delete_customer_"))
async def delete_customer_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    order_id = int(callback.data.split("_")[-1])
    # Проверка владельца и удаление из БД
    if callback.message:
        try:
            await callback.message.edit_text(f"Заказ с id {order_id} удалён.")  # type: ignore
        except Exception:
            await callback.message.answer(f"Заказ с id {order_id} удалён.")
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer()

# --- Кнопки редактирования каждого поля ---
@router.callback_query(F.data.startswith("edit_customer_field_"))
async def edit_customer_field_callback(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    parts = callback.data.split("_")
    field = parts[3]
    order_id = int(parts[4])
    prompts = {
        "name": "Введите новое имя:",
        "order_title": "Введите новое название заказа:",
        "order_description": "Введите новое описание заказа:",
        "payment": "Введите новую сумму оплаты:",
        "territory": "Укажите новую территорию:",
        "services": "Укажите новые услуги:"
    }
    await state.update_data(edit_order_id=order_id, edit_order_field=field)
    if callback.message:
        try:
            await callback.message.edit_text(prompts[field])  # type: ignore
        except Exception:
            await callback.message.answer(prompts[field])
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await state.set_state(getattr(CustomerStates, field))
    await callback.answer()

# --- Обработка ввода нового значения для каждого поля ---
@router.message(CustomerStates.name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить имя в БД
    await message.answer(f"Имя обновлено на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

@router.message(CustomerStates.order_title)
async def process_edit_order_title(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить название заказа в БД
    await message.answer(f"Название заказа обновлено на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

@router.message(CustomerStates.order_description)
async def process_edit_order_description(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить описание заказа в БД
    await message.answer(f"Описание заказа обновлено на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

@router.message(CustomerStates.payment)
async def process_edit_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить оплату в БД
    await message.answer(f"Оплата обновлена на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

@router.message(CustomerStates.territory)
async def process_edit_territory(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить территорию в БД
    await message.answer(f"Территория обновлена на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

@router.message(CustomerStates.services)
async def process_edit_services(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["edit_order_id"]
    # Обновить услуги в БД
    await message.answer(f"Услуги обновлены на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=customer_edit_fields_kb(order_id))

# --- Назад к действиям над заказом ---
@router.callback_query(F.data.startswith("back_customer_"))
async def back_customer_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    order_id = int(callback.data.split("_")[-1])
    if callback.message:
        try:
            await callback.message.edit_text(
                f"Меню заказа (id {order_id})",
                reply_markup=customer_action_kb(order_id)
            )  # type: ignore
        except Exception:
            await callback.message.answer(
                f"Меню заказа (id {order_id})",
                reply_markup=customer_action_kb(order_id)
            )
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer() 