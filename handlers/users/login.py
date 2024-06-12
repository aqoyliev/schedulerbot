import re
import random

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked

from data.config import ADMINS
from loader import dp, db, bot
from keyboards.inline.callbackdata import lang_callback, position_callback
from keyboards.inline.positions import positions_markup
from keyboards.default.mainMenu import main_menu
from keyboards.default.register import register_markup, phone_number_markup, back_markup, register_button
from keyboards.default.admin import admin_menu
from states.register import AdminRegister, Register, SignUp
from states.signin import SignIn

from googletrans import Translator
trans = Translator()


# @dp.message_handler(text = ['🔑 Login',"🔐 Kirish",'🔑 Войти'],state=SignUp.register)
async def login_handler(msg: Message):
    lang = await db.select_language(msg.from_user.id)
    text = "Iltimos oldingi hisobingizga ulangan telefon raqamingizni yuboring."
    await msg.answer(trans.translate(text=text, dest=lang).text,reply_markup=ReplyKeyboardRemove(True))
    await SignIn.phone.set()

@dp.message_handler(state=SignIn.phone)
async def phone_number_handler(msg: Message, state: FSMContext):
    lang = await db.select_language(msg.from_user.id)
    pattern = "^\+998[0-99]{2}[0-9]{7}$"
    if re.match(pattern, msg.text):
        code = random.randint(1000, 9999)
        old_id = await db.select_id_by_phone(msg.text)
        await state.update_data(old_id=old_id)
        await state.update_data(code=code)
        try:
            await bot.send_message(chat_id=old_id, text=code)
            text = "Oldingi telegram hisobingizga maxfiy kod jo'natildi, iltimos maxfiy kodni kiriting."
            await msg.answer(trans.translate(text=text, dest=lang).text,reply_markup=ReplyKeyboardRemove(True))
            await SignIn.secret_code.set()
        except BotBlocked:
            text = "Hisobingizga maxfiy kod jo'natib bo'lmadi, iltimos ro'yxatdan o'ting."
            await msg.answer(trans.translate(text=text, dest=lang).text, reply_markup=await register_button(lang))
            await SignUp.register.set()
    else:
        text = "Raqam noto'g'ri kiritildi, iltimos qaytadan tekshirib jo'nating."
        await msg.answer(trans.translate(text=text, dest=lang).text,reply_markup=ReplyKeyboardRemove(True))

@dp.message_handler(state=SignIn.secret_code)
async def secret_code_handler(msg: Message, state: FSMContext):
    lang = await db.select_language(msg.from_user.id)
    data = await state.get_data()
    code = str(data.get('code'))
    old_id = str(data.get('old_id'))
    if code == msg.text:
        await db.delete_user(msg.from_user.id)
        await db.update_user_chat_id(old_id, msg.from_user.id)
        await msg.answer(trans.translate(text="Asosiy menyu", dest=lang).text, reply_markup=await main_menu(lang))
        await state.finish()
    else:
        text = "Maxfiy kod mos kelmadi."
        await msg.answer(trans.translate(text=text, dest=lang).text, reply_markup=await register_button(lang))
        await SignUp.register.set()