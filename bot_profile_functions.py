from telegram import InlineKeyboardButton, InlineKeyboardMarkup,  Update
from telegram.ext import (
    CallbackContext,
)
import logging
import os
import re 

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' 

from bot_dbhelper import DBHelper
from dotenv import load_dotenv

db = DBHelper()
logger = logging.getLogger(__name__)
load_dotenv("./.env")
TOKEN = os.getenv("token")

# Check user is recorded, if not recorded then create profile, if created show main menu
def profile(update: Update, context: CallbackContext):
    """Enter details """
    username = update.message.chat.username

    fullname = db.get_fullname(username)
    
    if fullname == None:
        update.message.reply_text("Let's get started on that!")
        update.message.reply_text("What is your fullname?\n\n<i>Use /exit to exit</i>", parse_mode="HTML")
        return "CREATE_PROFILE"

    else:
        update.message.reply_text("Welcome back " + fullname + "!")
        return main_menu(update, context)

# Create the user profile + add preset questions into the database
def create_profile(update: Update, context: CallbackContext) -> int:
    fullname = update.message.text
    update.message.reply_text("Great " + fullname + ", we've added to our database.")
    db.create_fullname(update.message.chat.username, fullname)
    update.message.reply_text("Next, add your phone number\n\n<i>Use /exit to exit</i>", parse_mode="HTML")
    db.createquestions(update.message.chat.username)
    return "ADD_PHONE"

### add error handler if someone stops half way

def add_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    db.add_phone(update.message.chat.username, phone)
    update.message.reply_text("Next, add your email\n\n<i>Use /exit to exit</i>", parse_mode="HTML")
    return "ADD_EMAIL"

### add error handler if someone stops half way

def add_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    db.add_email(update.message.chat.username, email)
    update.message.reply_text("We're all done setting up your profile.\n")
    return main_menu(update, context)

### add error handler if someone stops half way

### FOR MAIN MENU FUNCTIONS ###
def main_menu(update: Update, context: CallbackContext):
    if update.callback_query != None:
        query = update.callback_query
        query.answer()
        user = query.message.from_user
    else:
        user = update.message.from_user

    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Particulars", callback_data="PARTICULARS"),
            InlineKeyboardButton("Links", callback_data="LINKS"),
        ],
        [
            InlineKeyboardButton("Q&A", callback_data="QNA"),
            InlineKeyboardButton("End", callback_data="QUIT")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "What would you like to view?"
    # Send message with text and appended InlineKeyboard
    if update.callback_query != None:
        query.edit_message_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text(message, reply_markup=reply_markup)
    return "MAIN_MENU"

############################ Edit Particulars Functions ###############################
# Displays the user's prticulars and the necessary edit buttons
def particulars(update: Update, context: CallbackContext):
    if update.callback_query != None:
        query = update.callback_query
        query.answer()
        username = query.message.chat.username
    else:
        username = update.message.chat.username
    
    user_particulars = db.get_profile(username)[0]
    fullname = user_particulars['fullname']
    contact_no = user_particulars['contact_no']
    email = user_particulars['email']
    msg = 'Name: <b>' +fullname + '</b>'

    if contact_no != None:
        msg += '\nPhone: <b>'+contact_no+'</b>'

    if email != None:
        msg += '\nEmail: <b>'+email+'</b>'
    # msg = 'Name: <b>'+fullname+'</b>\nPhone: <b>'+contact_no+'</b>\nEmail: <b>'+email+'</b>'
    keyboard = [
        [
            InlineKeyboardButton("Name", callback_data="EDIT_NAME"),
            InlineKeyboardButton("Mobile Number", callback_data="EDIT_NUMBER"),
            InlineKeyboardButton("Email", callback_data="EDIT_EMAIL")
        ],
        [
            InlineKeyboardButton("Back", callback_data="BACK"),
            InlineKeyboardButton("End", callback_data="QUIT"),
        ]
    ]
    msg += '\n\nClick on the buttons to edit your particulars.'
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query != None: #trigger when button is pressed 
        query.edit_message_text(
            text=msg, reply_markup=reply_markup, parse_mode='html'
        )
    else:
        update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='html')

    context.user_data["user_particulars"] = user_particulars
    return "PARTICULARS_MENU"

# Displays the user's fullname and prompts them to edit if they wish
def edit_name(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_particulars = context.user_data["user_particulars"]
    fullname = user_particulars['fullname']
    msg = "You currently have your fullname stored as <b>" + fullname +"</b>\n" + \
    "If you would like to change it, type your name in and press enter"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="PARTICULARS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=msg, reply_markup=reply_markup, parse_mode='html'
    )
    return "EDIT_NAME"

def save_name(update: Update, context: CallbackContext):
    fullname = update.message.text
    username = update.message.chat.username
    db.update_name_profile(username, fullname)

    msg = "You have updated your name. You new name is " + fullname
    update.message.reply_text(text=msg, parse_mode= 'html')

    return particulars(update, context)

def edit_mobile(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_particulars = context.user_data["user_particulars"]
    contact_no = user_particulars['contact_no']
    if contact_no == None:
        msg = "You have not stored your contact number. Type your contact number and press enter"
    else:
        msg = "You currently have your contact number stored as <b>" + contact_no +"</b>\n" + \
        "If you would like to change it, type your contact number in and press enter"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="PARTICULARS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=msg, reply_markup=reply_markup, parse_mode='html'
    )
    return "EDIT_MOBILE"

def save_mobile(update: Update, context: CallbackContext):
    contact_no = update.message.text
    username = update.message.chat.username
    db.update_number_profile(username, contact_no)


    if len(contact_no) != 8:
        msg = "You have entered a wrong number. Please enter your 8-digit phone number"
        update.message.reply_text(text=msg, parse_mode= 'html')
        return "EDIT_MOBILE" #if you want display msg, copy the function itself not the state 

    else:
        msg = "You have updated your mobile number. You new mobile number is " + contact_no

    update.message.reply_text(text=msg, parse_mode= 'html')

    return particulars(update, context)

def edit_email(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_particulars = context.user_data["user_particulars"]
    email = user_particulars['email']
    
    if email == None:
        msg = "You have not stored your email. Type your email in and press enter"
    else:
        msg = "You currently have your email stored as <b>" + email + "</b>\n" + \
            "If you would like to change it, type your name in and press enter"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="PARTICULARS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text( #callback query handler when we using a button
        text=msg, reply_markup=reply_markup, parse_mode='html'
    )

    return "EDIT_EMAIL"

def validate_email(email):

    if (re.search(regex,email)):
        return True 
    else:
       return False

def save_email(update: Update, context: CallbackContext):
    email = update.message.text
    username = update.message.chat.username

    check_email = validate_email(email)

    if check_email == False:
        msg = "You have entered an invalid email. Please re-enter a valid email"
        update.message.reply_text(text=msg, parse_mode= 'html')
        return "EDIT_EMAIL"
    else:
    
        db.update_email_profile(username, email)
        msg = "You have updated your email. Your new email is " + email
        update.message.reply_text(text=msg, parse_mode= 'html')

    return particulars(update, context)

############################ Edit Links Functions #####################################
def links(update: Update, context: CallbackContext):
    if update.callback_query != None:
        query = update.callback_query
        query.answer()
        username = query.message.chat.username
    else:
        username = update.message.chat.username

    user_links = db.get_links(username)
    msg = 'Add new links or edit your existing links here (maximum 4):\n\n'
    for link in user_links:
        msg += "<b>"+link["link_description"]+"</b>: "
        msg += link["link"] + "\n\n"

    # InlineKeyboardButtons will be created for each existing link with the tag "Edit [Link_Description]"
    # There will be an 'Add a New Link' button to create new links
    # [{link_description: Github, link:},{})
    keyboard = [[]]
    num_links = len(user_links)
    for i in range(num_links):
        keyboard[0].append(InlineKeyboardButton("Edit " + user_links[i]["link_description"], callback_data="LINK_"+user_links[i]["link_description"])) #user_links[i] refers to one dictonary #user_links[i][link_description] gets the name of the description
    keyboard.append([InlineKeyboardButton("Add a New Link", callback_data="NEWLINK")])
    keyboard.append(
        [
            InlineKeyboardButton("Back", callback_data="BACK"),
            InlineKeyboardButton("Delete", callback_data="DELETE"),
            InlineKeyboardButton("End", callback_data="QUIT"),
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query != None:
        query.edit_message_text(
            text=msg, reply_markup=reply_markup, parse_mode='html',disable_web_page_preview=True
        )
    else:
        update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="html",disable_web_page_preview=True)
    return "LINKS_MENU"

# This function creates a new link and enters into the add link description state
def new_link(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    msg = "To create a new link, first send in a short description of the link.\n" + \
        "(for example, 'Github') or press 'Back' to return to view your existing links"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="LINKS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=msg, reply_markup=reply_markup
    )
    return "ADD_LINK_DESC"

# This function retrieves the new link desciption
def add_link_desc(update: Update, context: CallbackContext):
    new_link_desc = update.message.text
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="LINKS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "Next, please enter the URL for your given link description or press 'Back' to return to view your existing links"
    update.message.reply_text(text=msg, reply_markup=reply_markup)
    
    context.user_data["link_description"] = new_link_desc
    return "ADD_LINK_URL"

# This function retrieves the new link url and inserts a new row into the database
def add_link_url(update: Update, context: CallbackContext):
    link_url = update.message.text
    username = update.message.chat.username
    link_description = context.user_data['link_description']
    logger.info(link_description)
    db.add_link(username, link_description, link_url)
    msg = "Your link for <b>" + link_description + "</b> has been added."
    update.message.reply_text(text=msg,  parse_mode='html')

    return links(update, context)

# This function edits an existing link 
def edit_link(update: Update, context: CallbackContext):
    data = update.callback_query.data
    query = update.callback_query
    query.answer()
    link_description_old = data[5:] #LINK_doggo pic - get doggo pic

    username = query.message.chat.username
    link_url = db.get_link_url(username, link_description_old)
    msg = "Your current link description is <b>" + link_description_old + "</b>\n" + \
        "If you would like to change the link description, you can key a new one or use /next to move on"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="LINKS")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=msg, reply_markup=reply_markup, parse_mode='html') #edit own text 

    context.user_data['link_description_old'] = link_description_old #saving into telegram bot memory 
    context.user_data['link_url'] = link_url
    context.user_data['message_id'] = [query.message.message_id]

    return "EDIT_LINK_DESC"

# This function retrieves the new link description
def edit_link_desc(update: Update, context: CallbackContext):
    new_link_desc = update.message.text
    if new_link_desc == '/next':
        new_link_desc = ''
    # if the user does not send anything, the link description is not edited
    if new_link_desc != '':
        context.user_data['link_description_new'] = new_link_desc #saving new link description to telegram memory state
    else:
        context.user_data['link_description_new'] = context.user_data["link_description_old"]

    msg = "Next, please enter the URL for your given link description"
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="LINKS"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reply_message = update.message.reply_text(text=msg, reply_markup=reply_markup)
    context.user_data['message_id'].append(reply_message.message_id)

    return "EDIT_LINK_URL"

def edit_link_url(update: Update, context: CallbackContext):
    link_url = update.message.text
    if link_url == '':
        link_url = context.user_data['link_url']
    username = update.message.chat.username
    link_description_old = context.user_data['link_description_old']
    link_description_new = context.user_data['link_description_new']

    db.edit_link(username, link_description_old, link_description_new, link_url)
    
    old_msg1 = "Your link for <b>" + link_description_new + "</b> has been added."
    update.message.reply_text(text=old_msg1,  parse_mode='html')

    old_msg2 = "Your new link is " + link_url
    update.message.reply_text(text=old_msg2,  parse_mode='html')

    for i in context.user_data['message_id']:
        context.bot.delete_message(chat_id = update.message.chat.id, message_id = i)

    return links(update, context)

def delete_link_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    username = query.message.chat.username
    user_links = db.get_links(username)
    for link in user_links:
        msg = "<b>"+link["link_description"]+"</b>: "
        msg += link["link"] + "\n\n"
    keyboard = [[]]
    num_links = len(user_links)
    for i in range(num_links):
        keyboard[0].append(InlineKeyboardButton("Delete " + user_links[i]["link_description"], callback_data="LINK_"+user_links[i]["link_description"])) 
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=msg, reply_markup=reply_markup, parse_mode='html',disable_web_page_preview=True
    )
    return "DELETE_LINK"

def delete_link(update: Update, context: CallbackContext):
    logger.info("we are in this state")
    data = update.callback_query.data
    query = update.callback_query
    query.answer()
    username = query.message.chat.username
    link_description_old = data[5:]
    db.delete_link(username,link_description_old)
    query.message.reply_text("Link description and url has been deleted")
    
    return links(update, context)

########################### Edit Question Functions ###################################
### FOR QNA FUNCTIONS ###
def qna(update: Update, context: CallbackContext):
    if update.callback_query != None:
        query = update.callback_query
        query.answer()
        username = query.message.chat.username
    else:
        username = update.message.chat.username
    
    user_questions = db.get_question(username)
    msg = "Answer any of the following questions" + "\n\n"
    for q in user_questions:
        msg += "<b>"+q["question"]+"</b>: \n"
        msg += q["answer"] + "\n\n"
    context.user_data["all_questions"] = [q["question"] for q in user_questions] # to store the order of the questions 
    context.user_data["all_answers"] = [q["answer"] for q in user_questions] # to store the order of the answers
    keyboard = [[]]
    num_answers = len(user_questions)
    for a in range(num_answers):
        keyboard[0].append(InlineKeyboardButton("Edit Q" + str(a+1), callback_data="qna_"+str(a)))
    keyboard.append(
        [
            InlineKeyboardButton("Back", callback_data="BACK"),
            InlineKeyboardButton("Delete", callback_data="DELETE"),
            InlineKeyboardButton("End", callback_data="QUIT"),
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query != None:
        query.edit_message_text(
            text=msg, reply_markup=reply_markup, parse_mode='html',disable_web_page_preview=True
        )
    else:
        update.message.reply_text(msg, reply_markup=reply_markup, parse_mode = 'html', disable_web_page_preview=True)
    # goes to fourth state
    return "QNA_MENU"

# this function edits an existing answer
def edit_answer(update: Update, context: CallbackContext):
    data = update.callback_query.data
    query = update.callback_query
    query.answer()
    qna_number = int(data[4:])
    qna_answer = context.user_data["all_answers"][qna_number]
    context.user_data["current_answer"] = qna_answer
    context.user_data["current_question"] = context.user_data["all_questions"][qna_number]
    logger.info(context.user_data["current_question"])
    msg = "Your current answer is <b>" + qna_answer + "</b>\n" + \
        "If you would like to change your answer, you can key in a new one and press enter"
    logger.info(msg)
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data="QNA"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=msg, reply_markup=reply_markup, parse_mode='html')
    return "EDIT_ANSWER"

# this function retrieves the new answer
def user_answer(update: Update, context: CallbackContext):
    qna_answer = update.message.text
    if qna_answer == '':
        qna_answer == context.user_data['current_answer']
    username = update.message.chat.username
    qna_question = context.user_data['current_question']
    db.edit_answer(username,qna_question,qna_answer)
    msg = "Your answer for <b>" + qna_question + "</b> has been added"
    update.message.reply_text(text=msg, parse_mode='html')

    return qna(update, context)

# users can select which answer to delete
def delete_user_answer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    username = query.message.chat.username
    user_questions = db.get_question(username)
    msg = "Answer any of the following questions" + "\n\n"
    for q in user_questions:
        msg += "<b>"+q["question"]+"</b>: \n"
        msg += q["answer"] + "\n\n"
    context.user_data["all_questions"] = [q["question"] for q in user_questions] # to store the order of the questions 
    context.user_data["all_answers"] = [q["answer"] for q in user_questions] # to store the order of the answers
    keyboard = [[]]
    num_answers = len(user_questions)
    for a in range(num_answers):
        keyboard[0].append(InlineKeyboardButton("Q" + str(a+1) + " Answer", callback_data="qna_"+str(a)))
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=msg, reply_markup=reply_markup, parse_mode='html',disable_web_page_preview=True
    )
    return "DELETE_ANSWER"

# this function deletes the answer
def delete_user_answer(update: Update, context: CallbackContext):
    data = update.callback_query.data
    query = update.callback_query
    query.answer()
    username = query.message.chat.username
    qna_number = int(data[4:])
    qna_question = context.user_data["all_questions"][qna_number]
    db.delete_answer(username,qna_question)
    query.message.reply_text("Answer has been deleted")
    
    return qna(update, context)