from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery

import models

from config import settings
from database import SessionLocal

payment_router = Router()


PRICE = types.LabeledPrice(label='Өстәмә квестлар', amount=20000)


@payment_router.message(Command('terms'))
async def process_terms_command(message: types.Message):
    await message.reply('terms', reply=False)


@payment_router.message(F.text == '👑Түләүле квестлар👑')
async def process_buy_command(message: types.Message):
    # if settings.payments_provider_token.split(':')[1] == 'TEST':
    #     await message.answer('Это тестовый платеж, *do not worry*')
    await message.answer_invoice(
        title='Серле квест',
        description='Сезне тагын бик күп ачылмаган эшләр көтә🎩 Бер тапкыр подписка алып, атна саен яңа квест алыгыз ⭐ ️',
        provider_token=settings.payments_provider_token,
        currency='RUB',
        photo_url='https://storage.yandexcloud.net/sledobot/teenagers.jpg',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[PRICE],
        start_parameter='time-subscription',
        protect_content=True,
        payload='some-invoice-payload-for-my-internal-use'
    )


@payment_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


def update_user_paid_status(user_id):
    db = SessionLocal()
    try:
        quest_query = db.query(models.User).filter(models.User.user_tg_id == user_id)
        quest_query.update({'paid': True}, synchronize_session=False)
        db.commit()
    finally:
        db.close()


@payment_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    update_user_paid_status(message.from_user.id)
    await message.answer('Хәзер сиңа яшерен квест ачык. Ул хәзер "🧩Маҗаралар🧩 " командасы буенча чыга')
