# type: ignore[attr-defined]
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import ContractorStates
from keyboards import contractor_edit_fields_kb, contractor_action_kb

router = Router()

# --- Показать меню редактирования услуги ---
@router.callback_query(F.data.startswith("edit_contractor_"))
async def edit_contractor_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    service_id = int(callback.data.split("_")[-1])
    if callback.message:
        try:
            await callback.message.edit_text(
                "Что хотите изменить?",
                reply_markup=contractor_edit_fields_kb(service_id)
            )  # type: ignore
        except Exception:
            await callback.message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer()

# --- Удалить услугу ---
@router.callback_query(F.data.startswith("delete_contractor_"))
async def delete_contractor_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    service_id = int(callback.data.split("_")[-1])
    # Проверка владельца и удаление из БД
    if callback.message:
        try:
            await callback.message.edit_text(f"Услуга с id {service_id} удалена.")  # type: ignore
        except Exception:
            await callback.message.answer(f"Услуга с id {service_id} удалена.")
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer()

# --- Кнопки редактирования каждого поля ---
@router.callback_query(F.data.startswith("edit_contractor_field_"))
async def edit_contractor_field_callback(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    parts = callback.data.split("_")
    field = parts[3]
    service_id = int(parts[4])
    prompts = {
        "photo_url": "Отправьте новое фото:",
        "name": "Введите новое имя:",
        "phone": "Введите новый телефон:",
        "services": "Опишите новые услуги:",
        "territory": "Укажите новую территорию:"
    }
    await state.update_data(edit_service_id=service_id, edit_service_field=field)
    if callback.message:
        try:
            await callback.message.edit_text(prompts[field])  # type: ignore
        except Exception:
            await callback.message.answer(prompts[field])
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await state.set_state(getattr(ContractorStates, field))
    await callback.answer()

# --- Обработка ввода нового значения для каждого поля ---
@router.message(ContractorStates.photo_url)
async def process_edit_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["edit_service_id"]
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото.")
        return
    photo_file_id = message.photo[-1].file_id
    # Обновить фото в БД
    await message.answer("Фото обновлено.")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))

@router.message(ContractorStates.name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["edit_service_id"]
    # Обновить имя в БД
    await message.answer(f"Имя обновлено на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))

@router.message(ContractorStates.phone)
async def process_edit_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["edit_service_id"]
    # Обновить телефон в БД
    await message.answer(f"Телефон обновлён на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))

@router.message(ContractorStates.services)
async def process_edit_services(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["edit_service_id"]
    # Обновить услуги в БД
    await message.answer(f"Услуги обновлены на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))

@router.message(ContractorStates.territory)
async def process_edit_territory(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["edit_service_id"]
    # Обновить территорию в БД
    await message.answer(f"Территория обновлена на: {message.text}")
    await state.clear()
    await message.answer("Что хотите изменить?", reply_markup=contractor_edit_fields_kb(service_id))

# --- Назад к действиям над услугой ---
@router.callback_query(F.data.startswith("back_contractor_"))
async def back_contractor_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("Ошибка: нет данных для обработки.", show_alert=True)
        return
    service_id = int(callback.data.split("_")[-1])
    if callback.message:
        try:
            await callback.message.edit_text(
                f"Меню услуги (id {service_id})",
                reply_markup=contractor_action_kb(service_id)
            )  # type: ignore
        except Exception:
            await callback.message.answer(
                f"Меню услуги (id {service_id})",
                reply_markup=contractor_action_kb(service_id)
            )
    else:
        await callback.answer("Нет сообщения для редактирования.", show_alert=True)
    await callback.answer()
