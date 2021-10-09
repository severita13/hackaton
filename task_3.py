import requests
from bs4 import BeautifulSoup as BS
import telebot
from MyToken import token
from telebot import types
import csv

bot = telebot.TeleBot(token)
responseHTML = ''
article_json = {}

def serializeList(jsonList):
    pairs = jsonList.items()
    res = ''
    for key, value in pairs:    
        res += '/' + str(value['number']) + ' ' + value['title'] +'\n\n'
    return res

def get_html():
    res = requests.get('https://kaktus.media/?lable=8&date=2021-10-08&order=time')
    # print(response)
    return res.text

def get_data(html):
    soup = BS(html, 'lxml')
    catalog = soup.find('div', class_='Tag')
    news_ = catalog.find_all('div', class_='Tag--article')

    n = 0
    for article in news_:
        n += 1
        if n > 20:
            break

        data =  {}
        data['number'] = n

        try:
            data['title'] = article.find('a', class_='ArticleItem--name').text.strip()
        except:
            data['title'] = ''

        try:
            data['image'] = article.find('a', class_='ArticleItem--image').find('img').get('src')
        except:
            data['image'] = ''

        article_json[n] = data
    return article_json


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(chat_id, serializeList(get_data(responseHTML)), parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def send_text(message):
    # убираем / у цифр:
    if message.text.lower().replace('/', '').isnumeric():
        # преобразуем строки в цифры:
        numericID = int(message.text.lower().replace('/', ''))
        # делаем кнопки кликабельными:
        bot.send_message(message.chat.id, 'You can see Description of this news and Photo' +'\n' + '/image' + str(numericID) +'\n' + '/title' + str(numericID) + '\n' + '/quit')

    if ('/image' in message.text.lower()):
        # получаем доступ к картинке по айди:
        numericID = int(message.text.lower().replace('/image',''))
        # в json хранится ссылка
        bot.send_message(message.chat.id, article_json[numericID]['image'])

    elif ('/title' in message.text.lower()):
        numericID = int(message.text.lower().replace('/title',''))
        bot.send_message(message.chat.id, article_json[numericID]['title'])

    elif message.text.lower() == '/quit':
        bot.send_message(message.chat.id, 'Good bye!')

    else:
        print('end')    

responseHTML = get_html()
bot.polling()