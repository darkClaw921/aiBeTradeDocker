import os
import random
import telebot
from datetime import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
from createKeyboard import create_menu_keyboard
import redis
import json
from analitic.workBinance import get_BTC_analit_for
from analitic.helper import *
load_dotenv()

gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
r = redis.Redis(host='localhost', port=6379, decode_responses=False)

PROMT_URL = 'https://docs.google.com/document/d/1YLkjaQPlAQASmuHDdHP43uBtxNOdt3eLZqHUH6YAff8/edit?usp=sharing'
#model_index=gpt.load_search_indexes('')
#model_index=sql.select_query('model', 'model=main')

@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id,
                     "Пришлите ссылку на google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing\nи подождите 20сек",)


@bot.message_handler(commands=['addpromt'])
def add_new_promt(message):
    sql.set_payload(message.chat.id, 'addpromt')
    bot.send_message(message.chat.id,
                     "Пришлите ссылку на google document и через пробел название промта (promt1). Не используйте уже существующие названия промта\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    username = message.from_user.username

    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    row = {'id': message.chat.id, 'model': '', 'promt': '','nicname':username}
    sql.replace_query('user', row)

    bot.send_message(message.chat.id, """Привет. Я Chat GPT-4, ИИ-аналитик по BTC""", reply_markup=create_menu_keyboard())
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')


@bot.message_handler(commands=['restart'])
def restart_modal_index(message):
    global model_index
    model_index = gpt.load_search_indexes(model_index)


@bot.message_handler(commands=['context'])
def send_button(message):
    try:
        payload = sql.get_payload(message.chat.id)
    except:
        payload = ' '
    #context = sql.get_context(message.chat.id, payload)
    #model = get_model_url(payload)
    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    try:
        sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
        sql.set_payload(message.chat.id, ' ')
    except:
        bot.send_message(message.chat.id,
                         "у вас небыло активного диалога контекст сброшен",)

    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id,
                     "Контекст сброшен",)
    


@bot.message_handler(commands=['model1'])
def dialog_model1(message):
    #payload = sql.get_payload(message.chat.id)
    sql.set_payload(message.chat.id, 'model1')
    model = sql.select_query('user', f'id={message.chat.id}')[0]['model']
    promt = sql.select_query('user', f'id={message.chat.id}')[0]['promt']

    bot.send_message(message.chat.id, f'вы работаете по моделе {model}',)
    bot.send_message(message.chat.id, f'вы работаете по промту {promt}',)
    bot.send_message(message.chat.id, 'Что вы хотите узнать?',)


@bot.message_handler(commands=['promt1'])
def work_promt1(message):
    #payload = sql.get_payload(message.chat.id)
    promt = sql.select_query('promt', f'promt="promt1"')[
        0]['url'].decode('utf-8')
    row = {'id': message.chat.id, 'promt': 'promt1'}
    sql.replace_query('user', row)
    sql.set_payload(message.chat.id, 'promt1')
    #promt = sql.select_query('user', f'id={message.chat.id}', row)
    bot.send_message(
        message.chat.id, f'вы работаете по промту {promt}', reply_markup=create_menu_keyboard())


@bot.message_handler(commands=['promt2'])
def work_promt2(message):
    #payload = sql.get_payload(message.chat.id)
    promt = sql.select_query('promt', f'promt="promt2"')[
        0]['url'].decode('utf-8')
    row = {'id': message.chat.id, 'promt': 'promt2'}
    sql.replace_query('user', row)
    sql.set_payload(message.chat.id, 'promt2')
    #promt = sql.select_query('user', f'id={message.chat.id}', row)
    bot.send_message(
        message.chat.id, f'вы работаете по промту {promt}', reply_markup=create_menu_keyboard())


@bot.message_handler(content_types=['text'])
def any_message(message):
    print('это сообщение', message)
    #text = message.text.lower()
    text = message.text
    userID = message.chat.id
    try:
        payload = sql.get_payload(userID)
    except:
        payload = 'a'
    
    if payload == 'addpromt':
        text = text.split(' ')
        rows = {'promt': text[1], 'url': text[0] }
        #sql.insert_query('model',rows)
        sql.replace_query('promt',rows)
        sql.set_payload(message.chat.id, '')
        return 0
    
    #promt = sql.select_query('promt', f'promt="promt1"')[0]['promt']
    promtUrl = sql.select_query('promt', f'promt="promt1"')[
        0]['url'].decode('utf-8')
    PROMT_URL = promtUrl 

    bot.send_message(message.chat.id,'Состaвляю аналитику')
    #promt = gpt.load_prompt(promptUrl)
    promt = gpt.load_prompt(PROMT_URL)
    #promt = 
    #print(f'{promptUrl=}')
    analitBTC = get_BTC_analit_for(text)
    #print(f'{analitBTC}')
    current, future = get_dates(int(text.split(' ')[3]))
    print("Текущая дата:", current)
    print(f"Дата через {text} дней:", future)
    promt = promt.replace('[analitict]', analitBTC)
    promt = promt.replace('[nextDate]', text.split(' ')[3])
    promt = promt.replace('[nowDate]', future)
    print(f'{PROMT_URL}')
    #print('#########################################', promt)
    try:
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': ' '}]
        answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
        
        row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
        sql.plus_query_user('user', row, f"id={userID}")
    
    except Exception as e:
        bot.send_message(message.chat.id, f'{e}')
        return 0
    

    bot.send_message(message.chat.id, answer)
    #add_message_to_history(userID, 'assistant', answer)
    return 0
    #context = sql.get_context(userID, payload)
    # if context is None or context == '' or context == []:
    #    context = text

    #print('context2', context + f'клиент: {text}')
    #model= gpt.load_prompt('https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing')
    # try:
    promt = sql.select_query('user', f'id={message.chat.id}')[
        0]['promt'].decode('utf-8')
    promtUrl = sql.select_query('promt', f'promt="{promt}"')[
        0]['url'].decode('utf-8')
    #    modelUrl = sql.select_query('user', f'id={message.chat.id}')['model']
    #    promt= gpt.load_prompt(get_model_url(promtUrl))
    #    answer = gpt.answer_index(promt, text, modelUrl)
    # except:
    #bot.send_message(message.chat.id, 'У вас не выбран пром, работа по стандартному')
    #promt= 'https://docs.google.com/document/d/1KbXMyyIbf4BKFkZeQfzKyzU8blCKoXmFl9du2UD0I7c/edit?usp=sharing'
    promt = gpt.load_prompt(promtUrl)
    try:
        answer = gpt.answer(promt, text, temp=1)
    except Exception as e:
        bot.send_message(message.chat.id, f'{e}')
        return 0
    #model= gpt.load_prompt(get_model_url(payload))
    #answer = gpt.answer(model, text, temp = 0.1)
    #answer = gpt.answer_index(promt, text, model_index,)
    print('answer', answer)
    bot.send_message(message.chat.id, answer)
    # if payload == 'model3':
    rows = {'id': time_epoch(), 'MODEL_DIALOG': payload,
            'TEXT': f'клиент: {text}'}
    sql.insert_query(userID,  rows)

    rows = {'id': time_epoch()+1, 'MODEL_DIALOG': payload,
            'TEXT': f'менеджер: {answer}'}
    sql.insert_query(userID,  rows)


bot.infinity_polling()
