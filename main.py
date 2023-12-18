import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from settings import settings
from gpt import gpt4_free
import textwrap


token = settings['Token']
bot = telebot.TeleBot(token)
schedule_dict = {}


class Schedule:
    """
    Сохраняет атрибуты для промпта

    Args:
        subject (str): Предметы
    """
    def __init__(self, subject):
        self.subject = subject
        self.amount = str()
        self.time = str()
        self.extra = str()


@bot.message_handler(commands=['start'])
def greetings(message):
    """
    Запуск бота

    Args:
        message (str): Сообщение пользователя

    Returns:
        Сообщение (str): "Добро пожаловать" и клавиатуру
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_schedule = InlineKeyboardButton('Создать расписание', callback_data='Создать расписание')
    button_recommendations = InlineKeyboardButton('Получить рекомендации', callback_data='Получить рекомендации')
    button_questions = InlineKeyboardButton('Задать вопрос', callback_data='Задать вопрос')
    button_reminder = InlineKeyboardButton('Установить напоминания', callback_data='Установить напоминания')
    button_ChatGPT = InlineKeyboardButton('Свободная генерация текста', callback_data='ChatGPT')
    markup.add(button_schedule, button_recommendations, button_questions, button_reminder, button_ChatGPT)
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Создать расписание")
def schedule_choice(message):
    """
    Предоставляет запись предметов для расписания

    Args:
        message (str): "Создать расписание"

    Returns:
        Направляет к функции "subject_step"
    """
    msg = bot.send_message(message.chat.id, 'Какие у вас есть предметы?')
    bot.register_next_step_handler(msg, subject_choice)


def subject_choice(message):
    """
    Предоставляет выбор количества предметов

    Args:
        message (str): Предметы пользователя

    Returns:
        Клавиатура InlineKeyboardMarkup с выбором количества предметов
        Направляет к функции "count_step"
    """
    chat_id = message.chat.id
    subject = message.text
    schedule = Schedule(subject)
    schedule_dict[chat_id] = schedule  
    keyboard_amount = InlineKeyboardMarkup(row_width=1)
    button_count_1 = InlineKeyboardButton(text='1', callback_data='1')
    button_count_2 = InlineKeyboardButton(text='2', callback_data='2')
    button_count_3 = InlineKeyboardButton(text='3', callback_data='3')
    button_count_4 = InlineKeyboardButton(text='4', callback_data='4')
    keyboard_amount.add(button_count_1, button_count_2, button_count_3, button_count_4,)
    bot.send_message(chat_id=chat_id, text='Сколько предметов в день вам комфортно изучать?', reply_markup=keyboard_amount)


@bot.callback_query_handler(func=lambda callback: callback.data in ['1', '2', '3', '4']) 
def amount_choice(callback):
    """
    Предоставляет выбор времени для начала обучения

    Args:
        callback (str): Количество предметов

    Returns:
        Клавиатура InlineKeyboardMarkup с выбором времени учебы
        Направляет к функции "time_step"
    """
    chat_id = callback.from_user.id
    amount = callback.data
    schedule = schedule_dict[chat_id]
    schedule.amount = amount
    keyboard_time = InlineKeyboardMarkup(row_width=1)
    button_time_1 = InlineKeyboardButton(text='8:30', callback_data='8:30')
    button_time_2 = InlineKeyboardButton(text='14:15', callback_data='14:15')
    button_time_3 = InlineKeyboardButton(text='16:00', callback_data='16:00')
    keyboard_time.add(button_time_1, button_time_2, button_time_3)
    bot.send_message(chat_id=chat_id, text='С какого времени будет начинаться учеба?', reply_markup=keyboard_time)


@bot.callback_query_handler(func=lambda callback: callback.data in ['8:30', '14:15', '16:00'])
def time_choice(callback):
    """
    Предоставляет возможность дополнить информацию для расписания

    Args:
        callback (str): Время выбора учебы

    Returns:
        Направляет к функции "extra_step"
    """
    chat_id = callback.from_user.id
    time = callback.data
    schedule = schedule_dict[chat_id]
    schedule.time = time
    msg = bot.send_message(chat_id=chat_id, text='Расскажите подробнее что вам нужно учесть при создании расписания')
    bot.register_next_step_handler(msg, extra_choice)


def extra_choice(message):
    """
    Подставляет атрибуты класса в промпт

    Args:
        message (str): Уточнения по расписанию

    Returns:
        Расписание
    """
    chat_id = message.chat.id
    extra = message.text
    schedule = schedule_dict[chat_id]
    schedule.extra = extra
    result = gpt4_free(textwrap.dedent(f'''\
                    Помоги мне сделать расписание для студента. В расписании у меня есть {schedule.subject}. 
                    Очень важно чтобы количество предметов в день в расписании не должно превышать {schedule.amount}. 
                    Учебный день должен начинаться с {schedule.time}. Перерыв между предметами должен быть 15 минут. 
                    Один предмет идет полтора часа. {schedule.extra}. 
                    Предметы в расписании не должны повторяться. 
                    Мне нужно только расписание без рекомендаций.
                    Расписание должно быть составлено на русском языке.
                    '''))
    bot.send_message(message.chat.id, result)


if __name__ == "__main__":   
    bot.infinity_polling()
