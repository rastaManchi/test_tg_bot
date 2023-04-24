from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, CallbackQuery, ContentType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def menu():
    btns = {}
    keyboard = InlineKeyboardMarkup(row_width=1)
    btns['Погода'] = 'weather'
    btns['Конвертировать валюту'] = 'converter'
    btns['Милые животные'] = 'animals'
    btns['Создать опрос'] = 'polls'
    for _ in btns:
        keyboard.insert(InlineKeyboardButton(_, callback_data=btns[_]))

    return keyboard


def groups(groups):
    btns = {}
    keyboard = InlineKeyboardMarkup(row_width=2)
    for group in groups:
        btns[group.group_name] = f'group_id={group.group_id}'
    btns['Назад'] = 'main_menu'
    for _ in btns:
        keyboard.insert(InlineKeyboardButton(_, callback_data=btns[_]))

    return keyboard


def symbols_menu(symbols):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for symbol in list(chunks(symbols, 4)):
        print(symbol)
        keyboard.add(*symbol)
    return keyboard
