#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import mysql.connector
import telebot
from telebot import types

mysql_config = {
  'host': '<HOST>',
  'user': '<USER>',
  'password': '<PASS>',
  'database': '<DATABASE>',
  'charset': 'utf8',
  'use_unicode': True  
}

secret = "<SECRET>"
bot = telebot.TeleBot('<TOKEN>', threaded=False, parse_mode='HTML')

bot.set_webhook(url="<URL>/{}".format(secret))

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello!")
    post_user_info(message.chat.id, 'tolk')
    send_markup(message)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Text...")

@bot.message_handler(commands=['dict'])
def send_markup(message):
    bot.send_message(message.chat.id, "Selec dict:", reply_markup=gen_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "dict1":
        bot.send_message(call.message.chat.id, "DICT1")
    elif call.data == "dict1":
        bot.send_message(call.message.chat.id, "DICT2")
    bot.answer_callback_query(call.id, "Dict changed")
    update_user_info(call.message.chat.id, call.data)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):

    if len(message.text) > 1:

        """ Get user selected dict  """
        dict = get_user_info(message.chat.id)

        """ Find word from database """
        words = find_word(dict, message.text)

        if len(words) > 0:
            for word in words:
                bot.send_message(message.chat.id, '<b>' + word[0].upper() + '</b>' + '\n' + word[1])
        else:
            bot.send_message(message.chat.id, 'Not found...')
    else:
        bot.send_message(message.chat.id, 'Please, send word')


def gen_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    dict1 = types.InlineKeyboardButton(text='dict1', callback_data="dict1")
    dict2 = types.InlineKeyboardButton(text='dict2', callback_data="dict2")
    markup.add(dict1, dict2)
    return markup

def find_word(dict, word):
    if len(word):
        query = "SELECT word, value FROM `" + dict + "` WHERE word = %(word1)s OR word LIKE %(word2)s"
        return get_data(query, { 'word1':  word, 'word2':  word + '_'}) or []
    else:
        return []

def get_user_info(user_id):
    query = "SELECT `dict` FROM `users` WHERE `user_id` = %(user_id)s"
    return get_data(query, { 'user_id': user_id })[0][0]

def post_user_info(user_id, dict):
    query = "INSERT IGNORE INTO `users` (`user_id`, `dict`) VALUES (%(user_id)s, %(dict)s)"
    set_data(query, { 'user_id':user_id, 'dict':dict })

def update_user_info(user_id, dict):
    query ="UPDATE `users` SET `dict` = %(dict)s WHERE `user_id` = %(user_id)s"
    set_data(query, { 'user_id': user_id, 'dict': dict })

def get_data(query, input):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(query, input)
        result = cursor.fetchall()
        return result
        cursor.close()
        connection.close()
    except Exception as ex:
        pass

def set_data(query, input):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(query, input)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as ex:
        pass




