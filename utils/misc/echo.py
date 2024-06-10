from aiogram import types

from keyboards.default.mainMenu import main_menu

from loader import dp, db, bot
from data.config import ADMINS
from keyboards.default.admin import admin_menu

from googletrans import Translator
trans = Translator()


# Echo bot
async def bot_echo(message: types.Message):
    admin_ids = [record['chat_id'] for record in await db.select_admin_ids()]
    if message.from_user.id in admin_ids:
        language = await db.select_admin_lang(message.from_user.id)
        await message.answer(trans.translate("Asosiy menyu",dest=language).text, reply_markup=await admin_menu(language))
    else:
        language = await db.select_language(message.from_user.id)
        await message.answer(trans.translate("Asosiy menyu",dest=language).text, reply_markup=await main_menu(language))