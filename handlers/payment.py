from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery

import models

from config import settings
from database import SessionLocal

payment_router = Router()


PRICE = types.LabeledPrice(label='Настоящая Машина Времени', amount=200*100)


@payment_router.message(Command('terms'))
async def process_terms_command(message: types.Message):
    await message.reply('terms', reply=False)


@payment_router.message(F.text == '👽👂👣👹🔥☠️')
async def process_buy_command(message: types.Message):
    if settings.payments_provider_token.split(':')[1] == 'TEST':
        await message.answer('Это тестовый платеж, *do not worry*')
    await message.answer_invoice(
        title='Секретный квест',
        description='🕵️‍♂️: - Что ты смог узнать?\n🥷: - Эти "рептилоиды" говорили о каком-то артефакте.\n🕵️‍♂️: - Что это? Что за арте.. ААА..\n🥷: - НЕТ! НЕТ! ОСТАВЬТЕ НАС! АААА.. ',
        provider_token=settings.payments_provider_token,
        currency='rub',
        photo_url='https://yandex-images.clstorage.net/fRiV49205/276b17YM/NuzUuwn0WrCvez0C5wOOFEy9aEP-LBm_MGWN6ODqU1vXBGVnsnz_W7DPNTofPs8qOyYj-txSThaRSXoZN3I2zSKJAN7IRa50in8YFxOy_tF5XKmGu6lpqzHVTdwhbtP7s0SmBKCf7YjTDKN4_Xw-yn8zdt4thgoABkhquiQnZf_1jYa9v9L5sL05TIHkl643D9rq8V_teow0pb6phwoCWtJ3VuWDDb8ZUb_jaM9cffkfg3XP2_XqMWVMqpgXl9TfldxUrTwS6jG8eU4hZzRf1r1LSVOsDzpNlEf-q-T5IziwRkRn4B2_GZGNEwvNTp-4HlAEPjgXyHBXDsj6RjdkP9efFb88QYvjTFtskKS2boQsmstgfA9JXyWEDUuW6gJbwwYGVSINX5tQj8N4_M6N6exBpbyJJnghdx_oi4Qld63n_qXdnHJ70F8ovdF3ZM9mLViI4f5dCJwkle2L9jtwaBFER8Uh7Y8bAX9TGx8cnQg9w3WcOUS589deOavmVpfPZXyWvN-CyTD-aS_DZiYfZB8pSVEtjquMNaXuKPb5QYsBNjdkYBzM2zD8kYsdP0z5fUEmLqgHO9HHHFgJxjXFLgfM5C4ecliD3wqsQwdFTrYf2uijz157bgfFfKsGCrOpg0aVJAL9TXojb2DYzx2-Og0jBx96d4hDZ84bGVe1ly4H77TuThOp861b_ZC1Zdylj5s5k02eqQ0l1Q475EpDijLFhbYTLX7L401RmeyeH-rNoke9e5dKIwX9CYm3p5evRp-1vs9g67GfSRyCpGbOR0_JW4HOLnnfpBf9iyR6A8hD9cXWEw0da6C8I0uNL85ZzKIEzNskq3Jn3fpZR-f33-ftxO4Oohni_VotgaRHn7SPuelxjL7ZvTRk7Pk1auFpAQf3N9LcjVnQ3-L4rc3sCt3CVx4KB5kgpS5JS3UkB4_2_UStjDLq8Mz6XCMnFDzk7Uro439fWQ2ltA2blKqR0',
        photo_height=512,  # !=0/None, иначе изображение не покажется
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[PRICE],
        start_parameter='time-machine-example',
        protect_content=True,
        payload='some-invoice-payload-for-our-internal-use'
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
    await message.answer('Теперь тебе доступен секретный квест🤫. Он теперь доступен по команде "🧩Квесты🧩"')
