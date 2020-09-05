import logging
from pathlib import Path

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from hbot.bot_stack import BotStack


bot = telebot.TeleBot('1395562593:AAFwTa_4KJ1wz6-EfLN-2hlMfmMCrH70whA')
stack = BotStack()
data = {}


def create_logger() -> logging.Logger:
    _logger = logging.getLogger('логгер бота')
    _logger.setLevel(logging.INFO)

    # create console log handler
    ch = logging.StreamHandler()
    setup_log_handler(ch)
    _logger.addHandler(ch)

    # create file log handler
    log_fn = Path('.') / "snapchat_bot.log"
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


if __name__ == '__main__':
    get_tasks_dict = {
        'show_cameras': show_cameras,
        'show_groups': show_groups,
        'get_home': get_home,
        'send_email': send_email,
        'show_calendar': show_calendar
    }
    logger = create_logger()

    bot.polling()
