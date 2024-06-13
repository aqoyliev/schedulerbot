# from tokenize import group
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import ADMINS
from keyboards.inline.settings import change_data_for_admin_markup, change_data_markup
from loader import dp, db, bot
from keyboards.inline.callbackdata import lang_callback
from keyboards.inline.languages import languages
from keyboards.inline.positions import positions_markup
from keyboards.default.mainMenu import main_menu
from keyboards.default.register import register_markup
from keyboards.default.settings import cancel_button, settings_markup
from keyboards.default.admin import admin_menu, admin_settings
from states.register import Register, SignUp
from utils.misc.get_schedule import get_schedules, get_full_schedules
from utils.misc.echo import bot_echo

from datetime import datetime, timezone, timedelta
from googletrans import Translator
trans = Translator()

weekdays = ['Dushanba','Seshanba','Chorshanba','Payshanba','Juma','Shanba','Yakshanba']


# @dp.message_handler(text = 'test')
# async def show_settings(msg: Message):
#     await plan_schedules()

@dp.message_handler(text = ['⚙️ Settings','⚙️ Sozlamalar','⚙️ Настройки'])
async def show_settings(msg: Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id not in admin_ids:
        lang = await db.select_language(msg.from_user.id)
        await msg.answer(msg.text, reply_markup=await settings_markup(lang))
        await db.update_username(msg.from_user.id,msg.from_user.username)
    else:
        lang = await db.select_admin_lang(msg.from_user.id)
        await msg.answer(msg.text, reply_markup=await admin_settings(lang))
        await db.update_botadmin_username(msg.from_user.id,msg.from_user.username)

@dp.message_handler(text = ['🌎 Change language',"🌎 Tilni o'zgartirish",'🌎 Изменить язык'])
async def show_languages(msg: Message):
    await msg.answer("🇬🇧 Choose language\n🇷🇺 Выберите язык\n🇺🇿 Tilni tanlang", reply_markup=languages)

@dp.message_handler(text = ['📝 Change data',"📝 Ma'lumotlarni o'zgartirish",'📝 Изменить данные'])
async def change_data(msg: Message, state: FSMContext):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id not in admin_ids:
        lang = await db.select_language(msg.from_user.id)
        full_name = await db.select_user_attribute(msg.from_user.id, 'fullname')
        phone = await db.select_user_attribute(msg.from_user.id, 'phone')
        group_id = await db.select_user_attribute(msg.from_user.id, 'group_id')
        group = await db.select_attribute('groups', group_id, 'name')
        text = trans.translate("Sizning ma'lumotlaringiz",dest=lang).text + '\n\n'
        text += trans.translate("Ism familiya:",dest=lang).text.capitalize() + '  ' + full_name + '\n'
        text += trans.translate("Telefon raqam:",dest=lang).text.capitalize() + '  ' + phone + '\n'
        text += trans.translate("Group:",dest=lang).text.capitalize() + '  ' + group + '\n\n'
        # text += trans.translate("Ma'lumotlarni o'zgartirish uchun tugmalar 👇",dest=lang).text
        await msg.answer(msg.text,reply_markup=await cancel_button(lang))
        data_msg = await msg.answer(text,reply_markup=await change_data_markup(lang))
        await state.update_data(msg_id=str(data_msg.message_id))
    else:
        lang = await db.select_admin_lang(msg.from_user.id)
        full_name = await db.select_admin_attribute(msg.from_user.id, 'fullname')
        phone = await db.select_admin_attribute(msg.from_user.id, 'phone')
        text = trans.translate("Sizning ma'lumotlaringiz",dest=lang).text + '\n\n'
        text += trans.translate("Ism familiya:",dest=lang).text.capitalize() + '  ' + full_name + '\n'
        text += trans.translate("Telefon raqam:",dest=lang).text.capitalize() + '  ' + phone + '\n\n'
        # text += trans.translate("Ma'lumotlarni o'zgartirish uchun tugmalar 👇",dest=lang).text
        await msg.answer(msg.text,reply_markup=await cancel_button(lang))
        data_msg = await msg.answer(text,reply_markup=await change_data_for_admin_markup(lang))
        await state.update_data(msg_id=str(data_msg.message_id))

@dp.message_handler(text = ['🔙 Main menu',"🔙 Asosiy menyu",'🔙 Главное меню'])
async def show_languages(msg: Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id in admin_ids:
        lang = await db.select_admin_lang(msg.from_user.id)
        await msg.answer(trans.translate("Asosiy menyu",dest=lang).text, reply_markup=await admin_menu(lang))
    else:
        lang = await db.select_language(msg.from_user.id)
        await msg.answer(trans.translate("Asosiy menyu",dest=lang).text, reply_markup=await main_menu(lang))

@dp.message_handler(text = ["🗒 Today's schedule","🗒 Bugungi jadval",'🗒 Расписание на сегодня'])
async def today_schedule_handler(msg: Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id not in admin_ids:
        lang = await db.select_language(msg.from_user.id)
        group_id = await db.select_user_attribute(msg.from_user.id, 'group_id')
        day = weekdays[datetime.now(timezone(timedelta(hours=5))).weekday()]
        schedule = await get_schedules('Today', group_id, day, lang)
        # photo_id = "https://telegra.ph/file/609ab0fe62d76fd03d899.png"
        # await msg.answer_photo(photo=photo_id, caption=schedule)
        await msg.answer(schedule)
    else:
        await bot_echo(msg)

@dp.message_handler(text = ["🗓 Tomorrow's schedule","🗓 Ertangi jadval",'🗓 Расписание на завтра'])
async def tomorrow_schedule_handler(msg: Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id not in admin_ids:
        lang = await db.select_language(msg.from_user.id)
        user_id = str(msg.from_user.id)
        group_id = await db.select_user_attribute(msg.from_user.id, 'group_id')
        day = weekdays[(datetime.now(timezone(timedelta(hours=5))).weekday()+1)%7]
        schedule = await get_schedules('Tomorrow', group_id, day, lang)
        # photo_id = "https://telegra.ph/file/609ab0fe62d76fd03d899.png"
        # await msg.answer_photo(photo=photo_id, caption=schedule)
        await msg.answer(schedule)
    else:
        await bot_echo(msg)

@dp.message_handler(text = ["📑 Full schedule","📑 To'liq jadval",'📑 Полное расписание'])
async def full_schedule_handler(msg: Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if msg.from_user.id not in admin_ids:
        lang = await db.select_language(msg.from_user.id)
        group_id = await db.select_user_attribute(msg.from_user.id, 'group_id')
        # photo_id = 'https://telegra.ph/file/609ab0fe62d76fd03d899.png'
        for day in weekdays:
            schedule = await get_full_schedules(group_id, day, lang)
            await msg.answer(schedule) if schedule is not None else None
        # await db.update_username(chat_id=msg.from_user.id, username=msg.from_user.username)
    else:
        await bot_echo(msg)

# @dp.message_handler(Command('universities'),state=SignUp.register)
# async def send_universities(message: Message):
#     admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
#     if message.from_user.id in admin_ids:
#         lang = await db.select_admin_lang(message.from_user.id)
#     else:
#         lang = await db.select_language(message.from_user.id)
#     universities = await db.select_all_universities()
#     text, k = '', 1
#     for university in universities:
#         text += f"<b>{k}</b>. " + str(university[1]) + '\n'
#         k += 1
#     await message.answer(text)

@dp.message_handler(text=["🚫 Bekor qilish","🚫 Cancel", "🚫 Отмена"])
async def cancel(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        msg_id = data.get('msg_id')
        await bot.delete_message(chat_id=message.from_user.id,message_id=msg_id)
    except:
        pass
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if message.from_user.id in admin_ids:
        lang = await db.select_admin_lang(message.from_user.id)
        await message.answer(trans.translate("Asosiy menyu",dest=lang).text, reply_markup=await admin_menu(lang))
    else:
        lang = await db.select_language(message.from_user.id)
        await message.answer(trans.translate("Asosiy menyu",dest=lang).text, reply_markup=await main_menu(lang))