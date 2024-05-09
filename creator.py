from telegram import InlineKeyboardButton as ikb, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import classes
import datetime

def new_request(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.current_request = classes.Request()

    user.current_request.author_name = user.name
    user.current_request.author_level = user.level
    user.current_request.author_boss = user.boss
    user.current_request.author_id = user.id

    user.current_request.boss = user.boss

    keyboard = []
    i = 0
    for article in classes.articles:
        if i in user.articles:
            keyboard.append([ikb(article, callback_data=f'{i}')])
        i+=1

    query.answer()
    query.edit_message_text(text='Выбор статьи расхода:', reply_markup=InlineKeyboardMarkup(keyboard))


def amount_request(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.current_request.article = classes.articles[int(query.data)]
    user.status = 'article'
    query.answer()
    if user.level > 1:
        text = f'Статья: {classes.articles[int(query.data)]}\nТекущий остаток: {classes.count[int(query.data)]}\nУкажите сумму платежа:'
    else:
        text = f'Статья: {classes.articles[int(query.data)]}\nУкажите сумму платежа:'
    query.edit_message_text(text)


def rs(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.status = 'rs'
    user.current_request.bank_and_phone = '-'
    user.current_request.payment_type = 'р/с'
    query.answer()
    query.edit_message_text(text=f'Укажите юр.лицо для р/с:')


def sbp(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.status = 'sbp'
    user.current_request.check = '-'
    user.current_request.payment_type = 'перевод'
    query.answer()
    query.edit_message_text(text=f'Укажите физ лицо для перевода:')


def sent(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.status = None
    user.current_request.check = 'Отправлен'
    query.answer()
    keyboard = [[ikb('Да', callback_data='desy'), ikb('Нет', callback_data='des-')]]
    query.edit_message_text('Есть ли желаемая дата платежа?', reply_markup=InlineKeyboardMarkup(keyboard))


def not_sent(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = classes.User.users_dict[query.from_user.id]
    user.status = None
    user.current_request.check = 'Не отправлен'
    query.answer()
    keyboard = [[ikb('Да', callback_data='desy'), ikb('Нет', callback_data='des-')]]
    query.edit_message_text('Есть ли желаемая дата платежа?', reply_markup=InlineKeyboardMarkup(keyboard))


def desy(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    keyboard = [[ikb('пн',callback_data='-'), ikb('вт',callback_data='-'), ikb('ср',callback_data='-'),
    ikb('чт',callback_data='-'), ikb('пт',callback_data='-'), ikb('сб',callback_data='-'), ikb('вс',callback_data='-')]]
    today = datetime.date.today()
    tomorrow = today
    start_day = tomorrow - datetime.timedelta(days=tomorrow.weekday())

    for week in range(5):
        week_buttons = []
        for day in range(7):
            day_date = start_day + datetime.timedelta(days=week * 7 + day)
            if day_date >= tomorrow:
                d = day_date.strftime('%d.%m')
                week_buttons.append(ikb(d, callback_data=f'des{d}'))
            else: week_buttons.append(ikb(' ', callback_data='-'))
        if week_buttons:  keyboard.append(week_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text('Выберите дату:', reply_markup=reply_markup)


def des(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    desd = data[3:]
    user = classes.User.users_dict[query.from_user.id]
    user.status = 'сomment'
    user.current_request.desired_date = desd
    query.answer()
    query.edit_message_text(text=f'Добавьте комментарий:')