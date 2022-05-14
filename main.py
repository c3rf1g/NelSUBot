import time
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

users_state = {}
# token =
bot = telebot.TeleBot(config.TOKEN)

report_list = InlineKeyboardMarkup()
report_list.row_width = 1
report_list.add(InlineKeyboardButton("Отчет в пдф формате", callback_data="pdf"))
report_list.add(InlineKeyboardButton("Графики из лабораторной работы", callback_data="graph"))
report_list.add(InlineKeyboardButton("Назад", callback_data="back_to_select_lab"))
lab_list = ["1", "2", "3"]


scroll_keyboard = InlineKeyboardMarkup()
scroll_keyboard.row_width = 2
scroll_keyboard.add(InlineKeyboardButton("<", callback_data="scroll_left"),
                    InlineKeyboardButton(">", callback_data="scroll_right"),
                    InlineKeyboardButton("Назад", callback_data="back_to_select_type"))

back_keyboard = InlineKeyboardMarkup()
back_keyboard.row_width = 1
back_keyboard.add(InlineKeyboardButton("Назад", callback_data="back_to_select_lab"))


def gen_markup():
    markup_labs_list = InlineKeyboardMarkup()
    markup_labs_list.row_width = 1
    for lab in lab_list:
        markup_labs_list.add(InlineKeyboardButton(lab, callback_data=lab + " лаба"))
    return markup_labs_list


def get_images_by_user(user_id):
    lab_images = []
    lab_number = users_state[user_id]["лаба"]
    path = f"./lab_{lab_number}"
    for root, dirs, files in os.walk(path):
        for file in files:
            lab_images.append(file)
    print(lab_images)
    return lab_images


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)
    if call.message.chat.id not in users_state:
        users_state[call.message.chat.id] = {
            "лаба": 0,
            "index": 0
        }
    if "лаба" in call.data or "back_to_select_type" in call.data:
        print()

        cb_dict = {
        }
        for lab in lab_list:
            cb_dict[lab + " лаба"] = lab + " лаба"
        if "back_to_select_type" != call.data:
            bot.answer_callback_query(call.id, cb_dict[call.data])
            users_state[call.message.chat.id]["index"] = 0
            users_state[call.message.chat.id]["лаба"] = call.data[0]
        else:
            bot.answer_callback_query(call.id, "Назад")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите что вы хотите увидеть из " +
                         str(users_state[call.message.chat.id]["лаба"]) + " лабы",
                         reply_markup=report_list)
    elif "graph" in call.data:
        bot.answer_callback_query(call.id, "Загрузка фото")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lab_images = get_images_by_user(call.message.chat.id)
        lab_number = users_state[call.message.chat.id]["лаба"]
        print(lab_images)
        try:
            bot.send_photo(call.message.chat.id, photo=open(f"./lab_{lab_number}/" +
                                                            lab_images[users_state[call.message.chat.id]["index"]], "rb"),
                           reply_markup=scroll_keyboard)
        except:
            bot.send_message(call.message.chat.id, 'Такой лабы ещё нет')

    elif "scroll_left" == call.data:

        time.sleep(0.7)
        bot.answer_callback_query(call.id, "Загрузка фото")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lab_images = get_images_by_user(call.message.chat.id)
        users_state[call.message.chat.id]["index"] -= 1
        if users_state[call.message.chat.id]["index"] * -1 >= len(lab_images):
            users_state[call.message.chat.id]["index"] = 0
        bot.send_photo(call.message.chat.id, photo=open(f"./lab_{users_state[call.message.chat.id]['лаба']}/" +
                                                        lab_images[users_state[call.message.chat.id]["index"]], "rb"),
                       reply_markup=scroll_keyboard)
    elif "scroll_right" == call.data:

        time.sleep(0.7)
        bot.answer_callback_query(call.id, "Загрузка фото")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lab_images = get_images_by_user(call.message.chat.id)
        users_state[call.message.chat.id]["index"] += 1
        if users_state[call.message.chat.id]["index"] >= len(lab_images):
            users_state[call.message.chat.id]["index"] = 0
        bot.send_photo(call.message.chat.id, photo=open(f"./lab_{users_state[call.message.chat.id]['лаба']}/" +
                                                        lab_images[users_state[call.message.chat.id]["index"]], "rb"),
                       reply_markup=scroll_keyboard)
    elif "back_to_select_lab" == call.data:
        bot.answer_callback_query(call.id, "Переход назад")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите лабораторную работу, которую выхотите увидеть:",
                         reply_markup=gen_markup())
    elif "pdf" == call.data:
        bot.answer_callback_query(call.id, "Загрузка файла")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # print(open(f"./{users_state[call.message.chat.id]['лаба']}.pdf"))
        bot.send_document(call.message.chat.id, open(f"./{users_state[call.message.chat.id]['лаба']}.pdf", 'rb'),
                          reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Назад", callback_data="back_to_select_type")))

    else:
        pass
    print(users_state)
#
#
# @bot.message_handler(func=lambda message: True)
# def message_handler(message):



@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️\n"
                                      "Мы студенты группы 9491 - Масинович Артем и Горобец Андрей\n"
                                      "подготовили уникальный вариант защиты лабораторных работ\n")
    # time.sleep(2000)
    bot.send_message(message.chat.id, "Выберите лабораторную работу, которую выхотите увидеть:",
                     reply_markup=gen_markup())


if __name__ == '__main__':


    bot.polling(none_stop=True)
