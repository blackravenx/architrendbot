import telebot
import gspread
import os
import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials
from telebot import types
DIRNAME = os.path.dirname(__file__)
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name( os.path.join(DIRNAME, 'google.json'), scope)

client = gspread.authorize(creds)

sheet = client.open("architrend").sheet1  # Open the spreadhseet


bot = telebot.TeleBot("1573688795:AAFaG7a_cMLihEFF7qExPN1k4cHj85LDccs")
bot.delete_webhook()
name = ''
jobname = ''
count = 0
cost = 0
slojnost = 0
quality = 0
plan = 0
avans_1 = 0
avans_2 = 0

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name) #следующий шаг – функция get_name
    else:
        bot.send_message(message.chat.id, 'Напиши Привет')

def get_name(message): #получаем имя
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Наименование продукции или детали')
    bot.register_next_step_handler(message, get_jobname)

def get_jobname(message): #Наименование продукции
    global jobname
    jobname = message.text
    bot.send_message(message.chat.id, 'Количество деталей:')
    bot.register_next_step_handler(message, get_count)

def get_count(message): #Ввод кол-ва 
    global count
    try:
        count = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, 'Цена за ед. (в тг):')
    bot.register_next_step_handler(message, get_cost)

def get_cost(message): #Ввод цены за ед. 
    global cost
    try:
        cost = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, 'Сложность: ')
    bot.register_next_step_handler(message, get_slojnost)

def get_slojnost(message): #Ввод сложности 
    global slojnost
    try:
        slojnost = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, 'Качество: ')
    bot.register_next_step_handler(message, get_quality)

def get_quality(message): #Ввод качества 
    global quality
    try:
        quality=int(message.text)
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) #наша клавиатура
        plan_y = types.KeyboardButton(text='Да') #кнопка «Да»
        plan_n= types.KeyboardButton(text='Нет')
        keyboard.add(plan_y,plan_n)
        bot.send_message(message.chat.id, 'Выполнен ли план? ',reply_markup=keyboard)
        bot.register_next_step_handler(message, get_plan)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')

def get_plan(message): #Ввод плана 
    global plan
    if message.text == 'Да':
        plan  = 1
    else:
        plan  = 0
    avans_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True) #наша клавиатура
    plan_y = types.KeyboardButton('Брал') #кнопка «Да»
    plan_n= types.KeyboardButton('Не брал')
    avans_keyboard.add(plan_y,plan_n)
    bot.send_message(message.chat.id, 'Брали ли Вы аванс(-ы)? ',reply_markup=avans_keyboard)
    bot.register_next_step_handler(message, get_avans)

@bot.message_handler(content_types=['text'])
def get_avans(message): #Ввод аванса
    if message.text == "Брал":
        bot.send_message(message.chat.id, 'Аванс 1: ')
        bot.register_next_step_handler(message, get_avans_1)
    elif message.text == "Не брал":
        show(message)
        #bot.register_next_step_handler(message, show)

def get_avans_1(message):
    global avans_1
    while avans_1 == 0:
        try:
            avans_1 = int(message.text)
        except Exception:
            bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, 'Аванс 2: ')
    bot.register_next_step_handler(message, get_avans_2)
def get_avans_2(message): #Ввод значений аванса
    global avans_2
    while avans_2 == 0:
        try:
            avans_2 = int(message.text)
        except Exception:
            bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    show(message)

def show(message): #Показываем полное сообщение
    now = datetime.datetime.now()
    dt_string = now.astimezone('Asia/Almaty').strftime("%d/%m/%Y %H:%M")
    clear_cost = int(count * cost)
    f_slojnost = int(clear_cost/100*slojnost)
    f_quality = int(clear_cost/100*quality)
    f_plan = int(clear_cost/100*plan)
    total = int(clear_cost+f_slojnost+f_quality+f_plan-avans_2)
    bonus_total=int(total - clear_cost+avans_2)
    bot.send_message(message.chat.id, 'Время: '+str(dt_string)+
    '\nФИО: '+str(name)+
    '\nНаименование продукции или детали: '+str(jobname)+
    '\nКоличество: '+str(count)+
    '\nЦена за ед.: '+str(cost)+
    '\nСложность: '+str(slojnost)+
    '\nКачество: '+str(quality)+
    '\nПлан: '+str(plan)+
    '\nАванс: '+str(avans_1) + '+'+str(avans_2)+
    '\n----------------------------'+
    '\nИтого: '+str(total)+
    '\nБонусы итого: '+str(bonus_total)+
    '\nЧистая цена: '+str(clear_cost)
    )
    add_rows(dt_string, name,jobname, count,cost, slojnost, quality, plan, avans_1, avans_2, total, bonus_total, clear_cost)
def add_rows(dt_string, name, jobname, count, cost, slojnost, quality, plan, avans_1,avans_2, total, bonus_total, clear_cost):
    row = [dt_string,name, jobname, count, cost, slojnost, quality, plan, avans_1, avans_2, total, bonus_total, clear_cost]
    sheet.append_row(row)
bot.polling(none_stop=True, interval=0)        