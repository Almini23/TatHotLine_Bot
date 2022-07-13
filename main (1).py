from telebot import types
import threading
import telebot
import random
import text
import time

bot = telebot.TeleBot('5052917948:AAFPg3FIPWllF8Kz0X5Bl5XRzRFOP6WUQmM')
wait_text = wait_file = ''
forms = {}


def comp_form(chat_id, form):
    global wait_text, wait_file
    for i in range(10):
        if not form[i]['answered']:
            if form[i]['ans_type'] == 'str':
                bot.send_message(chat_id, form[i]['text'])
                wait_text = str(i)

            if form[i]['ans_type'] == 'bool':
                kb = types.InlineKeyboardMarkup()
                if i == 9:
                    form[i]['text'] += f'\nТема: {text.topics[int(form[0]["answer"])]} \n' \
                                       f'Сообщение: {form[1]["answer"]}\n'
                    if form[3]["answer"] == '0':
                        form[i]['text'] += f'ФИО: {form[4]["answer"]}\n'
                    if form[5]["answer"] == '1':
                        form[i]['text'] += f'Телефон: {form[6]["answer"]}\n' \
                                           f'E-mail: {"" if form[7]["answer"] == "0" else form[7]["answer"]}\n'
                    kb.add(types.InlineKeyboardButton(text='Отправить', callback_data='end'))
                    bot.send_message(chat_id, form[i]['text'], reply_markup=kb)
                else:
                    kb.add(types.InlineKeyboardButton(text='Да', callback_data=str(i) + '_1'))
                    kb.add(types.InlineKeyboardButton(text='Нет', callback_data=str(i) + '_0'))
                    bot.send_message(chat_id, form[i]['text'], reply_markup=kb)

            if form[i]['ans_type'] == 'topic':
                kb = types.InlineKeyboardMarkup()
                for i1, topic in enumerate(text.topics):
                    kb.add(types.InlineKeyboardButton(text=topic, callback_data=str(i) + '_' + str(i1)))
                bot.send_message(chat_id, form[i]['text'], reply_markup=kb)

            if form[i]['ans_type'] == 'file':
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(text='Пропустить', callback_data=str(i) + '_0'))
                bot.send_message(chat_id, form[i]['text'], reply_markup=kb)
                wait_file = str(i)

            if form[i]['ans_type'] == 'vrb_str':
                if i == 4:
                    if form[3]['answer'] == '1':
                        form[4]['answered'] = True
                    else:
                        bot.send_message(chat_id, form[i]['text'])
                        wait_text = str(i)
                else:
                    if form[5]['answer'] == '0':
                        form[6]['answered'] = True
                        form[7]['answered'] = True
                    elif i == 6:
                        bot.send_message(chat_id, form[i]['text'])
                        wait_text = str(i)
                    else:
                        kb = types.InlineKeyboardMarkup()
                        kb.add(types.InlineKeyboardButton(text='Пропустить', callback_data=str(i) + '_0'))
                        bot.send_message(chat_id, form[i]['text'], reply_markup=kb)
                        wait_text = str(i)

        while not form[i]['answered']:
            time.sleep(0.3)


# СТАРТ
@bot.message_handler(commands=['start'])
def start_message(message: types.Message):

    message_form = []
    for i in range(10):
        mes = {'text': text.mes[i],
               'answered': False,
               'answer': None,
               'ans_type': text.ans_types[i]}
        message_form.append(mes)
    forms[message.chat.id] = message_form

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Написать обращение', callback_data='start'))
    bot.send_message(message.chat.id, text.start_text, reply_markup=kb)


@bot.message_handler(commands=['info'])
def start_message(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Правила приема обращений', callback_data='info_1'))
    kb.add(types.InlineKeyboardButton(text='Контакты', callback_data='info_2'))
    kb.add(types.InlineKeyboardButton(text='Документы', callback_data='info_3'))
    bot.send_message(message.chat.id, 'Информация', reply_markup=kb)


# КНОПКИ
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    global wait_text, wait_file

    if call.data == 'start':
        form = threading.Thread(target=comp_form, args=[call.message.chat.id, forms[call.message.chat.id]])
        form.start()
        return 0

    if call.data == 'end':
        if forms[call.message.chat.id][-2]['answer'] == '1':
            res = f'Обращение №{random.randint(1000, 9999)} было отправлено на рассмотрение!'
        else:
            res = 'Обращение не принят, так как Вы не дали согласие на использование Ваших персональных данных'
        bot.send_message(call.message.chat.id, res, reply_markup=types.ReplyKeyboardRemove())
        return 0

    if call.data[:4] == 'info':
        if call.data[5] == '1':
            bot.send_message(call.message.chat.id, text.rules)
        if call.data[5] == '2':
            bot.send_message(call.message.chat.id, text.contacts)
        if call.data[5] == '3':
            with open('doc_1.pdf', 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption='ПАМЯТКА по сохранению анонимности')
            with open('doc_2.pdf', 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption='Отчёт о работе ГЛ за 2021 год')
            with open('doc_3.pdf', 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption='Отчёт о работе ГЛ за полугодие 2022 года')
        bot.answer_callback_query(call.id)
        return 0

    index, ans = call.data.split('_')
    if not forms[call.message.chat.id][int(index)]['answered']:
        wait_text = wait_file = ''
        forms[call.message.chat.id][int(index)]['answer'] = ans
        forms[call.message.chat.id][int(index)]['answered'] = True
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, 'Ответ уже принят')


# ТЕКСТ
@bot.message_handler(content_types=['text'])
def after_text(message: types.Message):
    global wait_text
    if wait_text:
        forms[message.chat.id][int(wait_text)]['answer'] = message.text
        forms[message.chat.id][int(wait_text)]['answered'] = True
        wait_text = ''


# ФАЙЛ
@bot.message_handler(content_types=['document'])
def after_text(message: types.Message):
    global wait_file
    if wait_file:
        forms[message.chat.id][int(wait_file)]['answer'] = message.document
        forms[message.chat.id][int(wait_file)]['answered'] = True
        wait_file = ''


print('Bot is started')
if __name__ == '__main__':
    bot.polling()
