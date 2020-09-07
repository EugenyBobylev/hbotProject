import logging
import os
import sys
from pathlib import Path

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from hbot.bot_stack import BotStack

# ************************** Initialisation ***************************************************
token = os.environ.get('HBOT_TOKEN_111')
if token:
    bot = telebot.TeleBot(token)
else:
    bot = telebot.TeleBot('')

stack = BotStack()
data = {}


# ************************** bot methods ***************************************************
@bot.message_handler(commands=['start'])
def start_message(message):
    log_info(f'{str(message.chat.id)} --> {message.text}')
    clear_messages(message.chat.id)

    if message.text == '/start':
        show_home_menu(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)


# ************************** bot menu methods ***************************************************
def show_home_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Список камер', callback_data='show_cameras'),
        InlineKeyboardButton('Снимки по группам', callback_data='show_groups')
    )
    # keyboard.add(InlineKeyboardButton('Список камер', callback_data='show_cameras'))
    # keyboard.add(InlineKeyboardButton('Снимки по группам', callback_data='show_groups'))
    msg = bot.send_message(chat_id, 'Выберите что нужно', reply_markup=keyboard)
    push(msg)


# ************************** stack methods ***************************************************
def clear_messages(chat_id):
    while stack.count(chat_id) > 0:
        pop(chat_id)
        # bot.delete_message(chat_id, msg_id)


def push(message):
    stack.push(message.chat.id, message.message_id)


def pop(chat_id):
    msg_id = stack.pop(chat_id)
    if msg_id is not None:
        bot.delete_message(chat_id, msg_id)


# ************************** log methods ***************************************************
def create_logger() -> logging.Logger:
    _logger = logging.getLogger('логгер бота')
    _logger.setLevel(logging.INFO)

    # create console log handler
    ch = logging.StreamHandler()
    setup_log_handler(ch)
    _logger.addHandler(ch)

    # create file log handler
    log_fn = Path('.') / "hbot.log"
    fh = logging.FileHandler(log_fn, mode='w', encoding='utf-8', delay=False)
    setup_log_handler(fh)
    _logger.addHandler(fh)
    return _logger


def setup_log_handler(log_handler) -> None:
    log_handler.setLevel(logging.INFO)
    _formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    log_handler.setFormatter(_formatter)


def log_info(msg: str):
    if logger:
        logger.info(msg)


def log_error(msg: str):
    if logger:
        logger.error(msg)


if __name__ == '__main__':
    get_tasks_dict = {
    #    'show_cameras': show_cameras,
    #    'show_groups': show_groups,
    #    'get_home': get_home,
    #    'send_email': send_email,
    #    'show_calendar': show_calendar
    }
    logger = create_logger()
    if token:
        log_info('bot started')
        bot.polling()
    else:
        log_error('bot token not found')
