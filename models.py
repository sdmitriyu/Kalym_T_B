import asyncio
import os
from tortoise import Tortoise, fields
from tortoise.models import Model

# 1. ОПРЕДЕЛЯЕМ МОДЕЛЬ (ТАБЛИЦУ)
class Contractor(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(index=True, null=True)
    photo_url = fields.CharField(max_length=225)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=100, unique=True)
    services = fields.TextField()  # исправлено с servese
    territory = fields.TextField()  # исправлено с Territoryail
    created_at = fields.DatetimeField(auto_now_add=True)

class Rating_Cont(Model):
    id = fields.IntField(pk=True)
    contractor = fields.ForeignKeyField('models.Contractor', related_name='ratings')
    score = fields.IntField()
    comment = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

class Customer(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(index=True, null=True)
    name = fields.CharField(max_length=100)
    order_title = fields.CharField(max_length=225)
    order_description = fields.TextField()
    payment = fields.IntField()
    territory = fields.CharField(max_length=100)  # исправлено с territori
    services = fields.TextField()  # добавлено поле services

class Deal(Model):
    id = fields.IntField(pk=True)
    contractor = fields.ForeignKeyField('models.Contractor', related_name='deals')
    customer = fields.ForeignKeyField('models.Customer', related_name='deals')
    status = fields.CharField(max_length=20)  # waiting, active, finished, declined
    created_at = fields.DatetimeField(auto_now_add=True)
    finished_at = fields.DatetimeField(null=True)
    # Можно добавить поле для хранения id чата, если потребуется
    # chat_id = fields.BigIntField(null=True)

class Payment(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(index=True)
    deal_id = fields.IntField(null=True)  # для приватных чатов
    product = fields.CharField(max_length=50)  # private_chat, show_contact, combo, rating_pass, contact_pack_5
    amount = fields.IntField()  # в копейках
    status = fields.CharField(max_length=20)  # pending, completed, failed, refunded
    external_id = fields.CharField(max_length=100, null=True)  # ID в YooKassa
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

class Purchase(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(index=True)
    product = fields.CharField(max_length=50)  # rating_pass, contact_pack_5
    expires_at = fields.DatetimeField(null=True)
    remaining_uses = fields.IntField(null=True)  # для пакетов контактов
    created_at = fields.DatetimeField(auto_now_add=True)


# 2. ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ И ПОДКЛЮЧЕНИЯ К БАЗЕ
async def init():
    db_url = os.getenv('DATABASE_URL', 'sqlite://kalym.db')
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['models']}
    )
    # Создаёт таблицы по моделям, если их ещё нет
    await Tortoise.generate_schemas()

