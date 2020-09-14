import logging
import os
from pathlib import Path

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from hbot.bot_stack import BotStack

# ************************** Initialisation ***************************************************
token = os.environ.get('HBOT_TOKEN')
if token:
    bot = telebot.TeleBot(token)
else:
    bot = telebot.TeleBot('')

stack = BotStack()
data = {}


# ************************** bot methods ***************************************************
@bot.message_handler(commands=['start', 'stop'])
def start_message(message):
    log_info(f'{str(message.chat.id)} --> {message.text}')
    clear_messages(message.chat.id)

    if message.text == '/start':
        start_task(message)
        show_home_menu(message.chat.id)
    if message.text == '/stop':
        clear_messages(message.chat_id)
    bot.delete_message(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(query):
    log_info(f'{str(query.message.chat.id)} --> {query.data}')
    _qdata = query.data
    if _qdata in get_tasks_dict:
        func = get_tasks_dict[_qdata]
        func(query.message)


def start_task(message):
    msg = bot.send_message(message.chat.id, 'Введите описание задачи:')
    push(msg)


def m_start(message):
    clear_messages(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Start time tracking')
    push(msg)
    get_home(msg)


def m_stop(message):
    clear_messages(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Stop time tracking')
    push(msg)
    get_home(msg)


def get_today_report(message):
    msg = bot.send_message(message.chat.id, 'Here will be show today report')
    push(msg)
    get_reports(msg)


def get_yesterday_report(message):
    msg = bot.send_message(message.chat.id, 'Here will be show yesterday report')
    push(msg)
    get_reports(msg)


def get_monthly_report(message):
    msg = bot.send_message(message.chat.id, 'Here will be show monthly report')
    push(msg)
    get_reports(msg)


def get_weekly_report(message):
    msg = bot.send_message(message.chat.id, 'Here will be show weekle report')
    push(msg)
    get_reports(msg)


def get_bydate_report(message):
    msg = bot.send_message(message.chat.id, 'Here will be show report for a given date')
    push(msg)
    get_reports(msg)


# ************************** bot menu methods ***************************************************
def get_home(message):
    stack.all_count()
    clear_messages(message.chat.id)
    show_home_menu(message.chat.id)


def show_home_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Start', callback_data='start'),
        InlineKeyboardButton('Stop', callback_data='stop'),
        InlineKeyboardButton('Report', callback_data='get_reports'),
    )
    msg = bot.send_message(chat_id, 'Select from menu', reply_markup=keyboard)
    push(msg)


def get_reports(message):
    clear_messages(message.chat.id)
    show_reports_menu(message.chat.id)


def show_reports_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('today', callback_data='today_report'))
    keyboard.add(InlineKeyboardButton('yesterday', callback_data='yesterday_report'))
    keyboard.add(InlineKeyboardButton('weekly', callback_data='weekly_report'))
    keyboard.add(InlineKeyboardButton('monthly', callback_data='monthly_report'))
    keyboard.add(InlineKeyboardButton('by date', callback_data='bydate_report'))
    keyboard.add(InlineKeyboardButton('back...', callback_data='get_home'))
    msg = bot.send_message(chat_id, "Select report action", reply_markup=keyboard)
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
        'get_home': get_home,
        'get_reports': get_reports,
        'start': m_start,
        'stop': m_stop,
        'today_report': get_today_report,
        'yesterday_report': get_yesterday_report,
        'weekly_report': get_weekly_report,
        'monthly_report': get_monthly_report,
        'bydate_report': get_bydate_report
    }
    logger = create_logger()
    if token:
        log_info('bot started')
        bot.polling()
    else:
        log_error('bot token not found')
