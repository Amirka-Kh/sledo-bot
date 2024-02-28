from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.handlers import PreCheckoutQueryHandler
from aiogram.types import PreCheckoutQuery

# from aiogram.types.successful_payment import SuccessfulPayment

from config import settings


payment_router = Router()


PRICE = types.LabeledPrice(label='Настоящая Машина Времени', amount=20000)


@payment_router.message(Command('terms'))
async def process_terms_command(message: types.Message):
    await message.reply('terms', reply=False)


@payment_router.message(F.text == '👽👂👣👹🔥☠️')
async def process_buy_command(message: types.Message):
    if settings.payments_provider_token.split(':')[1] == 'TEST':
        await message.answer('pre_buy_demo_alert')
    await message.answer_invoice(
        title='Секретный квест',
        description='Инопланетное нашествие',
        provider_token=settings.payments_provider_token,
        currency='rub',
        photo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYscfUBUbqwGd_DHVhG-ZjCOD7MUpxp4uhNe7toUg4ug&s',
        photo_height=512,  # !=0/None, иначе изображение не покажется
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[PRICE],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )


@payment_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@payment_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await message.answer(
        'successful_payment, total amount: {total_amount}, currency: {currency}'.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        )
    )
