from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

start_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Руководство")],
        [KeyboardButton(text="Добавить услугу"), KeyboardButton(text="Создать заказ")],
        [KeyboardButton(text="Мои услуги"), KeyboardButton(text="Мои заказы")],
        [KeyboardButton(text="Показать рейтинг"), KeyboardButton(text="Полный рейтинг")]
    ], resize_keyboard=True
)

# --- Для УСЛУГ (Contractor) ---

def contractor_action_kb(service_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_contractor_{service_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_contractor_{service_id}")]
        ]
    )

def contractor_edit_fields_kb(service_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Фото", callback_data=f"edit_contractor_field_photo_url_{service_id}")],
            [InlineKeyboardButton(text="Имя", callback_data=f"edit_contractor_field_name_{service_id}")],
            [InlineKeyboardButton(text="Телефон", callback_data=f"edit_contractor_field_phone_{service_id}")],
            [InlineKeyboardButton(text="Услуги", callback_data=f"edit_contractor_field_services_{service_id}")],
            [InlineKeyboardButton(text="Территория", callback_data=f"edit_contractor_field_territory_{service_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_contractor_{service_id}")]
        ]
    )

# --- Для ЗАКАЗОВ (Customer) ---

def customer_action_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_customer_{order_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_customer_{order_id}")]
        ]
    )

def customer_edit_fields_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data=f"edit_customer_field_name_{order_id}")],
            [InlineKeyboardButton(text="Название заказа", callback_data=f"edit_customer_field_order_title_{order_id}")],
            [InlineKeyboardButton(text="Описание заказа", callback_data=f"edit_customer_field_order_description_{order_id}")],
            [InlineKeyboardButton(text="Оплата", callback_data=f"edit_customer_field_payment_{order_id}")],
            [InlineKeyboardButton(text="Территория", callback_data=f"edit_customer_field_territory_{order_id}")],
            [InlineKeyboardButton(text="Услуги", callback_data=f"edit_customer_field_services_{order_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_customer_{order_id}")]
        ]
    )

def take_order_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Взять заказ", callback_data=f"take_order_{order_id}")]
        ]
    )

def confirm_order_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Согласиться", callback_data=f"confirm_order_{order_id}")],
            [InlineKeyboardButton(text="Отклонить", callback_data=f"decline_order_{order_id}")]
        ]
    )

private_chat_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отказаться")],
        [KeyboardButton(text="Завершить услугу")],
        [KeyboardButton(text="Оценить")]
    ], resize_keyboard=True
)

# Клавиатура для отправки контакта
contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить контакт", request_contact=True)],
        [KeyboardButton(text="Ввести вручную")]
    ], resize_keyboard=True, one_time_keyboard=True
)

# Клавиатура для предпросмотра карточки
def preview_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Сохранить", callback_data="save_contractor_card")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_contractor_card")]
        ]
    )

def preview_customer_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Сохранить", callback_data="save_customer_card")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_customer_card")]
        ]
    )

