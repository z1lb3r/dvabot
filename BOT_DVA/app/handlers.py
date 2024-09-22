import os

from aiogram import Bot
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command

from dotenv import load_dotenv
from app.db import requests as rq
from app import keyboard as kb


load_dotenv()
router = Router()

#
#   Старт и кнопки основного меню
@router.message(Command("start"))
async def btn_start(message: Message):
    file_path = "media/mainimg.jpg"  #"C:/Users/Kirill/Desktop/PYTHON/BETBOT_v1/media/tgbot_start.jpg"
    if message.from_user.id == os.getenv('ADMIN_ID'):
        await message.answer('Вы авторизовались как админ', reply_markup=kb.admin_panel)
        await message.answer('Выберите период, за который хотите получить отчет', reply_markup=kb.main_menu)        
    else:
        await message.reply_photo(photo=FSInputFile(path=file_path))        
        await message.answer("Добрый день и добро пожаловать в систему учета сделок!", reply_markup=kb.admin_panel)
        await message.answer("Пожалуйста, выберите период, за который хотите получить отчет",reply_markup=kb.main_menu)