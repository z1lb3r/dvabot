from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
#   from app.db.requests import get_data
#
#   ОСНОВНЫЕ КЛАВИАТУРЫ
back_to_main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="↩️ Вернуться в главное меню")]],
                                   resize_keyboard=True)


main_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💸 Получить отчет за день", callback_data="btn_day")],
                                                  [InlineKeyboardButton(text="💳 Получить динамику счета за неделю", callback_data="btn_week")],
                                                   [InlineKeyboardButton(text="💰 Получить динамику счета за месяц", callback_data="btn_month")]
                                                   ],resize_keyboard=True)


admin_panel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="↩️ Вернуться в главное меню")], 
                                            [KeyboardButton(text="🤖 Внести данные")]],
                                   resize_keyboard=True)
