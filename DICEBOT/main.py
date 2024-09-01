import asyncio
from contextlib import suppress

from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import DiceEmoji, ParseMode
from aiogram.utils.markdown import hcode
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase as MDB

from pymongo.errors import DuplicateKeyError


router = Router()


def reply_builder(
    text: str | list[str],
    sizes: int | list[int]=2,
    **kwargs
) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    text = [text] if isinstance(text, str) else text
    sizes = [sizes] if isinstance(sizes, int) else sizes

    [
        builder.button(text=txt)
        for txt in text
    ]

    builder.adjust(*sizes)
    return builder.as_markup(resize_keyboard=True, **kwargs)


@router.message(CommandStart())
async def start(message: Message, db: MDB) -> None:
    pattern = {
        "_id": message.from_user.id,
        "balance": 1000,
        "stats": {"wins": 0, "loses": 0, "tie": 0},
        "game": {"status": 0, "value": 0, "rid": ""}
    }

    with suppress(DuplicateKeyError):
        await db.general.insert_one(pattern)

    user = await db.general.find_one({"_id": message.from_user.id})
    users_in_search = await db.general.count_documents({"game.status": 1})

    await message.reply(
        "Начинай поиск и играй!\n"
        f"Пользователей в поиске: {hcode(users_in_search)}\n\n"
        f"Баланс: {user['balance']}\n"
        "Статистика (w/l/t): "
        f"{hcode(user['stats']['wins'])} / "
        f"{hcode(user['stats']['loses'])} / "
        f"{hcode(user['stats']['tie'])}",
        reply_markup=reply_builder("🔎 Поиск")
    )


@router.message(Command("search"))
@router.message(F.text.lower().contains("поиск"))
async def search_game(message: Message, bot: Bot, db: MDB) -> None:
    user = await db.users.find_one({"_id": message.from_user.id})
    pattern = {"text": "У вас уже есть активная игра!"}

    if user["game"]["status"] == 0:
        rival = await db.users.find_one({"game.status": 1})
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"game.status": 1}})

        if rival is None:
            pattern["text"] = "Вы успешно начали поск соперника!"
            pattern["reply_markup"] = reply_builder("❌ Отмена")
        else:
            pattern["text"] = "Соперник найден!"
            pattern["reply_markup"] = reply_builder("🔻 Завершить")

            await db.users.update_one(
                {"_id": user["_id"]}, {"$set": {"game.status": 2, "game.rid": rival["_id"]}}
            )
            await db.users.update_one(
                {"_id": rival["_id"]}, {"$set": {"game.status": 2, "game.rid": user["_id"]}}
            )

            await bot.send_message(rival["_id"], **pattern)
    elif user["game"]["status"] == 1:
        pattern["text"] = "Вы уже находитесь в поиске соперника!"

    await message.reply(**pattern)


@router.message(Command("cancel"))
@router.message(F.text.lower().contains("отмена"))
async def cancel_game(message: Message, db: MDB) -> None:
    user = await db.users.find_one({"_id": message.from_user.id})
    
    if user["game"]["status"] == 1:
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"game.status": 0}})
        await message.reply("Вы отменили поиск соперника!", reply_markup=reply_builder("🔎 Поиск"))


@router.message(Command("leave"))
@router.message(F.text.lower().contains("завершить"))
async def leave_game(message: Message, bot: Bot, db: MDB) -> None:
    user = await db.users.find_one({"_id": message.from_user.id})
    
    if user["game"]["status"] == 2:

        rival = await db.users.find_one({"_id": user["game"]["rid"]})
        if rival["game"]["value"] > 0:
            return await message.reply("Вы не можете завершить игру, ваш соперник сделал ход!")
        
        await message.reply("Вы покинули игру!", reply_markup=reply_builder("🔎 Поиск"))
        await bot.send_message(rival["_id"], "Ваш соперник покинул игру!", reply_markup=reply_builder("🔎 Поиск"))

        await db.users.update_many(
            {"_id": {"$in": [user["_id"], rival["_id"]]}},
            {"$set": {"game.status": 0, "game.value": 0, "game.rid": ""}}
        )


@router.message(F.dice.emoji == DiceEmoji.DICE)
async def play_game(message: Message, bot: Bot, db: MDB) -> None:
    user = await db.users.find_one({"_id": message.from_user.id})

    results = ["Ничья!", "Ничья!"]
    update_data = {"$set": {"game.value": 0}}

    if user["game"]["status"] == 2:
        if user["game"]["value"] > 0:
            return await message.reply("Вы не можете выкинуть кубик второй раз!")
        
        rival = await db.users.find_one({"_id": user["game"]["rid"]})

        uvalue = message.dice.value
        rvalue = rival["game"]["value"]

        await db.users.update_one({"_id": user["_id"]}, {"$set": {"game.value": uvalue}})

        if rvalue > 0:
            if rvalue > uvalue:
                await db.users.update_one({"_id": user["_id"]}, {"$inc": {"stats.loses": 1}})
                await db.users.update_one({"_id": rival["_id"]}, {"$inc": {"stats.wins": 1}})

                results = ["Вы проиграли!", "Вы выиграли!"]
            elif rvalue < uvalue:
                await db.users.update_one({"_id": user["_id"]}, {"$inc": {"stats.wins": 1}})
                await db.users.update_one({"_id": rival["_id"]}, {"$inc": {"stats.loses": 1}})

                results = ["Вы проиграли!", "Вы выиграли!"][::-1]
            else:
                update_data["$inc"] = {"stats.tie": 1}
            
            await message.reply(f"{results[0]} {hcode(uvalue)} | {hcode(rvalue)}")
            await bot.send_message(rival["_id"], f"{results[1]} {hcode(uvalue)} | {hcode(rvalue)}")

            await db.users.update_many(
                {"_id": {"$in": [user["_id"], rival["_id"]]}},
                update_data
            )


async def main() -> None:
    bot = Bot(token="7068307478:AAEPTE4OA9uInmFHh0Am-auyy1U-r6mCc_c") #, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(router)

    cluster = AsyncIOMotorClient("mongodb+srv://mouravyev:vektor202424@cluster0.vzhkb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = cluster.dicebotdb

    # cluster = AsyncIOMotorClient(host="localhost", port=27017)
    # db = cluster.testdb

    await bot.delete_webhook(True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is switched off')