from telegram import InlineKeyboardButton, InlineKeyboardMarkup,  Update
from telegram.ext import (
    CallbackContext,
)

from bot_dbhelper import DBHelper

db = DBHelper()

def view(update: Update, context: CallbackContext):
    update.message.reply_text("Enter a Telegram username to begin or use /exit to exit")
    return "USERNAME"

def view_user_menu(update: Update, context: CallbackContext):
    if "viewed_username" in context.user_data and context.user_data["viewed_username"] != None:
        username = context.user_data["viewed_username"]
    else:
        username = update.message.text
    
    user = db.get_profile(username)

    if len(user) == 0:
        update.message.reply_text("Oops user <b>{}</b> record is not found. Please enter a valid user or use /exit to exit".format(username), parse_mode= "HTML")
        return "USERNAME"

    user_particulars = user[0]
    message = "Found user <b>{}</b>'s record. Use the buttons to view the user particulars".format(username)

    keyboard = [
        [
            InlineKeyboardButton("Particulars", callback_data="view_particulars"),
            InlineKeyboardButton("Links", callback_data="view_links")
        ],
        [
            InlineKeyboardButton("Q&A", callback_data="view_qna"),
            InlineKeyboardButton("End", callback_data="end")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
    context.user_data["viewed_profile"] = user_particulars
    context.user_data["viewed_username"] = username
    return "DISPLAY"

def view_user_particulars(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    profile = context.user_data["viewed_profile"]
    message = 'Name: <b>' +profile['fullname'] + '</b>'

    if profile['contact_no'] != None:
        message += '\nPhone: <b>'+profile['contact_no']+'</b>'

    if profile['email'] != None:
        message += '\nEmail: <b>'+profile['email']+'</b>'
    
    keyboard = [
        [
            InlineKeyboardButton("Links", callback_data="view_links")
        ],
        [
            InlineKeyboardButton("Q&A", callback_data="view_qna"),
            InlineKeyboardButton("End", callback_data="end")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="HTML")
    return "DISPLAY"


def view_user_links(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_links = db.get_links(context.user_data["viewed_username"])
    
    if len(user_links) == 0:
        message = "The user has no recorded links."
    else:
        message = 'These are the user links:\n\n'
        for link in user_links:
            message+= "<b>{}</b>: {}\n\n".format(link["link_description"], link["link"])

    keyboard = [
        [
            InlineKeyboardButton("Particulars", callback_data="view_particulars")
        ],
        [
            InlineKeyboardButton("Q&A", callback_data="view_qna"),
            InlineKeyboardButton("End", callback_data="end")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="HTML")
    return "DISPLAY"


def view_user_qna(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_questions = db.get_question(context.user_data["viewed_username"])
    
    if len(user_questions) == 0:
        message = "The user has no recorded Q&A."
    else:
        message = ''
        for i in range(len(user_questions)):
            message += "<b>Q{} {}</b>:\n{}\n\n".format(i+1 ,user_questions[i]["question"], user_questions[i]["answer"])


    keyboard = [
        [
            InlineKeyboardButton("Particulars", callback_data="view_particulars"),
            InlineKeyboardButton("Links", callback_data="view_links")
        ],
        [
            InlineKeyboardButton("End", callback_data="end")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="HTML")
    return "DISPLAY"