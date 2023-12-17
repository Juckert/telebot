import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from settings import settings
from gpt import gpt4_free
import textwrap


token = settings['Token']
bot = telebot.TeleBot(token)
schedule_dict = {}


class Schedule:
    def __init__(self, subject):
        self.subject = subject
        self.count = None
        self.time = None
        self.extra = None


@bot.message_handler(commands=['start'])
def greetings(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_schedule = InlineKeyboardButton('Создать расписание', callback_data='Создать расписание')
    button_recommendations = InlineKeyboardButton('Получить рекомендации', callback_data='Получить рекомендации')
    button_questions = InlineKeyboardButton('Задать вопрос', callback_data='Задать вопрос')
    button_reminder = InlineKeyboardButton('Установить/отключить напоминания', callback_data='Установить/отключить напоминания')
    button_ChatGPT = InlineKeyboardButton('Свободная генерация текста', callback_data='ChatGPT')
    markup.add(button_schedule, button_recommendations, button_questions, button_reminder, button_ChatGPT)
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Создать расписание")
def schedule_step(message):
    msg = bot.send_message(message.chat.id, 'Какие у вас есть предметы?')
    bot.register_next_step_handler(msg, subject_step)


def subject_step(message):
    chat_id = message.chat.id
    subject = message.text
    schedule = Schedule(subject)
    schedule_dict[chat_id] = schedule  
    keyboard_count = InlineKeyboardMarkup(row_width=1)
    batton_count_1 = InlineKeyboardButton(text='1', callback_data='1')
    batton_count_2 = InlineKeyboardButton(text='2', callback_data='2')
    batton_count_3 = InlineKeyboardButton(text='3', callback_data='3')
    batton_count_4 = InlineKeyboardButton(text='4', callback_data='4')    
    keyboard_count.add(batton_count_1, batton_count_2, batton_count_3, batton_count_4,)
    bot.send_message(chat_id=message.chat.id, text='Сколько предметов в день вам комофртно изучать?', reply_markup=keyboard_count)


@bot.callback_query_handler(func=lambda callback: callback.data in ['1', '2', '3', '4']) 
def count_step(callback):
    chat_id = callback.from_user.id
    count = callback.data
    schedule = schedule_dict[chat_id]
    schedule.count = count
    keyboard_time = InlineKeyboardMarkup(row_width=1)
    batton_time_1 = InlineKeyboardButton(text='8:30', callback_data='8:30')
    batton_time_2 = InlineKeyboardButton(text='14:15', callback_data='14:15')
    batton_time_3 = InlineKeyboardButton(text='16:00', callback_data='16:00')
    keyboard_time.add(batton_time_1, batton_time_2, batton_time_3)
    bot.send_message(chat_id=callback.from_user.id, text='С какого времени будет начинаться учеба?', reply_markup=keyboard_time)


@bot.callback_query_handler(func=lambda callback: callback.data in ['8:30', '14:15', '16:00'])
def time_step(callback):
    chat_id = callback.from_user.id
    time = callback.data
    schedule = schedule_dict[chat_id]
    schedule.time = time
    msg = bot.send_message(chat_id=callback.from_user.id, text='Расскажите подробнее что вам нужно еще учесть при создании расписания')
    bot.register_next_step_handler(msg, extra_step)


def extra_step(message):
    chat_id = message.chat.id
    extra = message.text
    schedule = schedule_dict[chat_id]
    schedule.extra = extra
    result = gpt4_free(textwrap.dedent(f'''\
                            Помоги мне сделать расписание для студента. В расписании у меня есть {schedule.subject}. 
                            Очень важно чтобы количество предметов в день в расписании не должно превышать {schedule.count}. 
                            Учебный день должен начинаться с {schedule.time}. Перерыв между предметами должен быть 15 минут. 
                            Один предмет идет полтора часа. {schedule.extra}. 
                            Предметы в расписании не должны повторяться. 
                            Мне нужно только расписание без рекомендаций.
                            Расписание должно быть составлено на русском языке.
                            '''))
    bot.send_message(message.chat.id, result)


if __name__ == "__main__":   
    bot.infinity_polling()
