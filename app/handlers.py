
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.handlers.message import MessageHandler
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import os
import json
import aiocron
import asyncio
import logging
import time
import random

from datetime import datetime
from app.config import bot
# from main import load_birthdays, save_birthdays

router = Router()

delay = 3
next_birthday_id = 1

# def generate_birthday_id():
#     global next_birthday_id
#     new_id = next_birthday_id
#     next_birthday_id += 1
#     return new_id

def name_of_json(chat_id):
    json_name = f"group_{chat_id}"
    print(json_name)
    return json_name

def load_birthdays():
    if os.path.exists(BIRTHDAYS_DATA) and os.path.getsize(BIRTHDAYS_DATA) > 0:
        with open(BIRTHDAYS_DATA, "r") as f:
            return json.load(f)
    else:
        return {"users": []}

    
def save_birthdays(data):
    with open(BIRTHDAYS_DATA, "w") as f:
        json.dump(data, f, indent=4)

async def handle_all_messages(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        group_name = message.chat.title
        await message.reply(f"Название группы: {group_name}")
        return group_name

async def send_temporary_message(text, chat_id, delay=3):
    reply = await bot.send_message(chat_id, text)
    await asyncio.sleep(delay)
    await bot.delete_message(chat_id, reply.message_id)


@router.message(CommandStart())
async def cmd_start(message: Message):
    global BIRTHDAYS_DATA
    chat_id = message.chat.id
    group_name = message.chat.title
    name = message.from_user.username
    BIRTHDAYS_DATA = f"group_{chat_id}({group_name}).json"
    birthdays = load_birthdays()

    await bot.send_message(chat_id, f"Приветствую, {name}!\nЯ бот для упоминаний дней рождений участников группы! (created by M∆)")
    
    if birthdays:
        time.sleep(delay)
        await message.answer("Используйте /help для работы со мной!")
    else:
        time.sleep(delay)
        await message.answer("Для начала работы со мной, введите свой день рождения!")



def generate_id(ids):
    while True:
        new_id = random.randint(1, 100)
        if new_id not in ids:
            return new_id

@router.message(Command("add_birthday"))
async def add_birthday(message: types.Message):
    try:
        _, name, date = message.text.split()
        datetime.strptime(date, "%Y-%m-%d")
        chat_id = message.chat.id

        if datetime.strptime(date, '%Y-%m-%d') > datetime.now():
            
            reply = await message.reply("Нельзя добавить будущую дату!") 
            await asyncio.sleep(3)
            await bot.delete_message(message.chat.id, reply.message_id)
            return
        
        
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        data = load_birthdays()
        print(data)
        
        for user in data["users"]:
            if user["chat_id"] == chat_id and user["name"] == name and user["user_id"] == user_id:
                user["birthday"] = date
                break
        else:
            ids = {user["id"] for user in data["users"]}
            birthday_id = generate_id(ids)
            
            data["users"].append({"id": birthday_id, "user_id": user_id ,"chat_id": chat_id, "name": name, "birthday": date})
            

        save_birthdays(data)
        await send_temporary_message(f"День рождения для {name} добавлен c датой - {date}", message.chat.id)

    except ValueError:
        await send_temporary_message("Пожалуйста, используйте правильный формат: /add_birthday ИМЯ ГГГГ-ММ-ДД", message.chat.id)
    

@router.message(Command("delete_birthday"))
async def delete_birthday(message:types.Message):
    try:
        _, birthday_id = message.text.split()
        chat_id = message.chat.id

        data = load_birthdays()

        for i, user in enumerate(data['users']):
            if user["chat_id"] == chat_id and user["id"] == int(birthday_id):
                await send_temporary_message(f"Запись о дне рождения с именем {user['name']} под ID ({birthday_id}) удалена.", message.chat.id)
                del data['users'][i]
                save_birthdays(data)
                

                for j, user in enumerate(data["users"], start=1):
                    user["id"] = j

                return
            
        await send_temporary_message(f"Запись о дне рождения с ID {birthday_id} не найдена.", message.chat.id)

    except ValueError:
        await send_temporary_message("Пожалуйста, используйте правильный формат: /delete_birthday ID", message.chat.id)


def names_of_months(num_of_months):
    days_and_months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }

    for num, months in days_and_months.items():
        if num_of_months == num:
            result = months

    return result


    # birthdays = load_birthdays()
    # dates = [date["birthday"] for date in birthdays["users"]]
    # print(dates)

def calc_age(birthday_str):
    birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age

@router.message(Command("next_birthday"))
async def next_birthday(message: types.Message):
    try:
        # ВОЗМОЖНО ИСПРАВИТЬ 
        username = message.from_user.username or message.from_user.full_name 
        data = load_birthdays()
        today = datetime.now()
        next_birthday = None
        min_days_diff = float("inf")
        # TODO доп проверка среди всех дней рождений какой самый ближайщий тот и выбрать
        # TODO по дню и по месяцу        
        for user in data["users"]:
            birthday_date = datetime.strptime(user["birthday"], '%Y-%m-%d')
            birthday_this_year = birthday_date.replace(year=today.year)
            print(birthday_this_year)
            print(today)
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)
            days_diff = (birthday_this_year - today).days
            print(days_diff)
            if days_diff < min_days_diff:
                # min_days_diffn = days_diff
                next_birthday = user
            
        if next_birthday:
            date = [int(part) for part in next_birthday["birthday"].split("-")]
            print(date)
            age = datetime.now().year - date[0]
            month_of_birthday = names_of_months(date[1])
            
            await message.reply(f"Ближайший день рождения у {next_birthday['name']}({username}) - {date[2]} {month_of_birthday}. \
                                \n(Исполняется {age})")
        else:
            await send_temporary_message("Информация о днях рождения отсутствует", message.chat_id)
    
    except Exception as e:
        logging.exception(e)


@router.message(Command("all_birthdays"))
async def all_birthdays(message: types.Message):
        data = load_birthdays()
        # print(result2)
        # date = [int(part) for part in users["birthday"].split("-")]

        if data['users']:
            
            birthdays_list = []
            for user in data["users"]:
                age = calc_age(user["birthday"])
                user_info = f"(ID: {user['id']}) {user['name']} - {user['birthday']} ({age})"
                birthdays_list.append(user_info)

            birthdays_string = '\n'.join(birthdays_list)
            await message.answer(f"Список дней рождений: \n{birthdays_string}")



            # birthdays_list = '\n'.join([f"{user['name']}: {user['birthday']}, (ID:{user['id']})" for user in data['users']])
            # await message.answer("Список дней рождений: \n" + birthdays_list)
        else:
            await send_temporary_message("Нет информаций о днях рождения.", message.chat.id)




async def check_birthdays():
    birthdays = load_birthdays()
    today = datetime.today().strftime("%d/%m")
    
    for user in birthdays['users']:
        user_birthday = user["birthday"]
        date_obj = datetime.strptime(user_birthday, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%m")

        if formatted_date == today:
            await bot.send_message(user["chat_id"], f"Сегодня день рождения у {user['name']}, давайте поздравим его!")

@router.message(Command("help"))
async def help_commands(message: Message):
    await bot.send_message(message.chat.id ,"P.S: Все что указано в скобках - формат ввода данных\n \
                        \nПримеры: \
                        \n/update_birthday 2, name, Алексей или /update_birthday 2, birthday, YYYY-MM-DD\n \
                        \n/add_birthday - (NAME, YYYY-MM-DD) - добавление информации о дня рождения пользователя \
                        \n/update_birthday - (ID, {name, birthday}, {new_name, new_birthday})  \
                        \n/delete_birthday - (ID) - удаление информации о пользователе и его дне рождения \
                        \n/next_birthday - ближайший день рождения \
                        \n/all_birthdays - список всех пользователей и их дней рождения")

@router.message(content)

@router.message(Command("update_birthday"))
async def update_birthday(message: Message, command: CommandObject):
    try:
        args = command.args
        
        if args == None or len(args.split()) != 3:
            await bot.send_message(message.chat.id ,"Используйте команду следующим образом: /update_birthday <ID> <name|date_of_birth> <новое значение>")
            return

        user_id, field, new_field = args.split()
        birthday = load_birthdays()

        user = next((user for user in birthday["users"] if user["id"] == int(user_id)), None)
        print(user)
        if user:
            if field == "name":
                user["name"] = new_field
            elif field == "birthday":
                user["birthday"] = new_field
            else:
                message.reply("Поле для обновления должно быть 'name' или 'date_of_birth'")
                return 
            
            save_birthdays(birthday)
            await send_temporary_message("Данные обновлены успешно!", message.chat.id)
        else:
            await message.reply("Пользователь с таким ID не найден")

    except ValueError:
        await send_temporary_message("Пожалуйста, введите значение в формате /update_birthday 2, name, Алексей или /update_birthday 2, birthday, YYYY-MM-DD ", message.chat.id)

@aiocron.crontab("0 0 * * *")
async def daily_birthday_check():
    print("Запуск шедулера")
    await check_birthdays()
    print("Запущен шедулер")

