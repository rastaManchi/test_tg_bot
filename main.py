import random
import re
import json
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types.message import ContentTypes
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests

from config import *
from keyboards import *
from models.db import *

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Polls(StatesGroup):  # класс для хранения состояний (опросы)
    group_id = State()
    question = State()
    answers = State()


class Weather(StatesGroup):  # класс для хранения состояний (погода)
    city = State()


class Converter(StatesGroup):  # класс для хранения состояний (конвертер)
    from_symbol = State()
    to_symbol = State()
    amount = State()


async def on_start(_):  # проверка запуска бота
    me = await bot.me
    print(f'Бот запустился под ником {me.username}.')


@dp.message_handler(state='*', commands=['start'])  # Приветственное сообщение
async def start(msg: types.Message):
    try:
        if not get_user(user_id=msg.from_user.id):
            create_user(user_id=msg.from_user.id, user_name=msg.from_user.username)
        await bot.send_message(msg.from_user.id,
                               "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                               reply_markup=menu())
    except Exception as e:
        print(f'Error -- {e}')


@dp.message_handler(content_types=['new_chat_members'])  # отслеживания добавления бота в группу
async def new_group(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id and not get_group(group_id=message.chat.id):
            add_group(user_id=message.from_user.id, group_id=message.chat.id, group_name=message.chat.title)  # добавление группы и user_id в базу данных
            await bot.send_message(message.from_user.id, f"Success! Спасибо, что добавили меня в группу <b>{message.chat.title}</b>", parse_mode="HTML")


@dp.callback_query_handler(state='*')
async def inline_keyboard(callback_query: CallbackQuery):  # Обработчик Inline кнопок
    if callback_query.data == 'weather':  # Функция, после нажатия кнопки 'Погода'
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, 'Укажите город')
        await Weather.city.set()  # Finite State Machine
    elif callback_query.data == 'converter':  # Функция, после нажатия кнопки 'Конвертировать валюту'
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, 'Какую валюту конвертируем?', reply_markup=symbols_menu(symbols))
        await Converter.from_symbol.set()  # Finite State Machine
    elif callback_query.data == 'animals':  # Функция, после нажатия кнопки 'Милые животные'
        try:
            page = random.randint(0, 100)
            r = requests.get(f'https://fonwall.ru/search?q=милые+животные&page={page}&format=js')  # запрос на сайт с картинками
            images = re.findall('(https://img2.fonwall.ru\S+h=750)"', str(r.content))
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_photo(callback_query.from_user.id, photo=random.choice(images))
            await bot.send_message(callback_query.from_user.id,
                                   "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                                   reply_markup=menu())
        except Exception as e:
            await callback_query.answer("Ошибка, попробуйте позже", show_alert=True)
            await bot.send_message(callback_query.from_user.id,
                                   "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                                   reply_markup=menu())
    elif callback_query.data == 'polls':  # Функция, после нажатия кнопки 'Создать опрос'
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, 'Укажите опрос')
        await Polls.question.set()  # Finite State Machine
    elif callback_query.data == 'main_menu':  # Вернуться в главное меню
        await callback_query.message.edit_text( "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                                   reply_markup=menu())
    elif 'group_id' in callback_query.data:  # Обработчик Inline кнопок с группами, куда добавили бота
        try:
            group_id = int(callback_query.data.split('=')[1])
            question = re.search('Вопрос: (.+)', callback_query.message.text).group(1)
            answers = re.search("Ответы:\n(.+)", callback_query.message.text).group(1)
            await bot.send_poll(group_id, question, answers.split(';'), is_anonymous=False)
        except Exception:
            await callback_query.answer("Ошибка, попробуйте позже\nВозможно, бот уже не состоит в указанной группе", show_alert=True)
        await callback_query.message.edit_text(
            "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
            reply_markup=menu())



@dp.message_handler(state=Weather.city)
async def get_info(msg: types.Message, state: FSMContext):  # Ожидание ввода города и сбор данных с помощью API OpenWeatherMap
    try:
        r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={msg.text}&appid=3140cf48db6a89dd9eb2dc1338ae400d')
        info = json.loads(r.content)
        print(json)
        message = ''
        message += f'<b>Город</b>: {info["name"]}\n'
        message += f'<b>Температура</b>: {info["main"]["temp"]}°F || {int(info["main"]["temp"])-273}°C\n'
        message += f'<b>Ощущается</b>: {info["main"]["feels_like"]}°F || {int(info["main"]["feels_like"])-273}°C\n'
        message += f'<b>Давление</b>: {int(info["main"]["pressure"]/1.33322)} мм.рт.ст.'
        await bot.send_message(msg.from_user.id, message, parse_mode="HTML")
        await bot.send_message(msg.from_user.id,
                               "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                               reply_markup=menu())
    except Exception:
        await bot.send_message(msg.from_user.id, 'Ошибка, попробуйте позже.', parse_mode="HTML")
        await bot.send_message(msg.from_user.id,
                               "Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                               reply_markup=menu())
    await state.finish()


@dp.message_handler(state=Polls.question)
async def get_question(msg: types.Message, state: FSMContext):  # Ожидание ввода вопроса к опроснику
    await state.update_data(question=msg.text)
    await msg.answer("Отлично! Введите варианты ответов следующим образом:\n\nОтвет1\nОтвет2\nОтвет3")
    await Polls.next()


@dp.message_handler(state=Polls.answers)
async def get_answers(msg: types.Message, state: FSMContext):  # Ожидание ввода ответов к опроснику
    await state.update_data(answers=msg.text.replace('\n', ';'))
    data = await state.get_data()
    await msg.answer(f"Укажите группу для опроса\n\nВопрос: {data['question']}\n"
                         f"Ответы:\n{data['answers']}", reply_markup=groups(get_all_groups(msg.from_user.id)))
    await state.finish()


@dp.message_handler(state=Converter.from_symbol)
async def get_from_symbol(msg: types.Message, state: FSMContext):  # Ожидание ввода валюты из которой конвертируем
    await state.update_data(from_symbol=msg.text)
    await msg.answer("Отлично! В какую валюту конвертируем?")
    await Converter.next()


@dp.message_handler(state=Converter.to_symbol)
async def get_to_symbol(msg: types.Message, state: FSMContext):  # Ожидание ввода валюты в которую конвертируем
    await state.update_data(to_symbol=msg.text)
    await msg.answer("Отлично! Введите сумму, которую нужно конвертировать?")
    await Converter.next()


@dp.message_handler(state=Converter.amount)
async def get_amount(msg: types.Message, state: FSMContext):  # Ожидание ввода суммы конвертации и использования Exchange Rates API, чтобы получмить результат конвертации
    await state.update_data(amount=msg.text)
    data = await state.get_data()
    r = requests.get(f'https://api.apilayer.com/exchangerates_data/convert?to={data["to_symbol"]}&from={data["from_symbol"]}&amount={data["amount"]}', headers=headers)
    converted_info = json.loads(r.content)
    await msg.answer(f"Из <b>{data['from_symbol']}</b> в <b>{data['to_symbol']}</b>\n1 <b>{data['from_symbol']}</b> = {converted_info['info']['rate']} <b>{data['to_symbol']}</b>\n{data['amount']} <b>{data['from_symbol']}</b> = {converted_info['result']} <b>{data['to_symbol']}</b>", parse_mode="HTML")
    await msg.answer("Добрый день, это мое тестовое задание, надеюсь, что вам все понравится.",
                               reply_markup=menu())
    await state.finish()


if __name__ == '__main__':
    headers = {
        'apikey': 'r4qpT7dkbcPGoYT2UM3LgN8IBMnYrmB4'
    }
    symbols_dict = json.loads(requests.get(f'https://api.apilayer.com/exchangerates_data/symbols', headers=headers).content)['symbols']  # Получение списков валют, которые мы можем конвертировать (Exchange Rates API)
    symbols = []
    for symbol in symbols_dict:
        symbols.append(symbol)  # Создание массива с шифрами валют
    while True:
        try:
            executor.start_polling(dp, on_startup=on_start)
        except Exception:
            pass

