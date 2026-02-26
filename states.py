from aiogram.fsm.state import StatesGroup, State

class ContractorStates(StatesGroup):
    photo_url = State()
    name = State()
    phone = State()
    services = State()  # исправлено с servese
    territory = State()  # исправлено с territoryail

class CustomerStates(StatesGroup):
    name = State()
    order_title = State()
    order_description = State()
    payment = State()
    territory = State()  # исправлено с territori
    services = State()  # добавлено поле services
