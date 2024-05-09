from creator import *
import datetime
from main import upd2, from_sheet_to_dict

def for_approval(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user = classes.User.users_dict[user_id]
    query.edit_message_text(text='Заявки на согласование:')
    no_request = True

    if user.level == 2: ok = 'rok'
    else: ok = 'dok'

    for request in from_sheet_to_dict().values():
        if (request.status == 'У руководителя' or request.status == '💼У директора') and request.boss == user_id:
            no_request = False
            keyboard = [[ikb('✅', callback_data=f'{ok}{request.id}'),
                         ikb('🕑', callback_data=f'rlt{request.id}'),
                         ikb('❌', callback_data=f'rno{request.id}')]]
            text = request.to_string()
            if user.level > 1:  text = f'Остаток: {classes.count[classes.articles.index(request.article)]}\n' + text
            context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    if no_request: context.bot.send_message(chat_id=user_id, text='Нет актуальных заявок.\n\nНажмите /start для перехода в меню.')
    else: context.bot.send_message(chat_id=user_id, text='Нажмите /start для перехода в меню.')


def history_approved(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user = classes.User.users_dict[user_id]
    query.edit_message_text(text='История согласованных заявок:')
    no_request = True

    if user.level == 2:
        for request in from_sheet_to_dict().values():
            if request.status == '💼У директора' and request.boss == user_id:
                no_request = False
                context.bot.send_message(chat_id=user_id, text=request.to_string())

    elif user.level == 3:
        for request in from_sheet_to_dict().values():
            if request.status == '✅Оплачено':
                no_request = False
                context.bot.send_message(chat_id=user_id, text=request.to_string())

    if no_request: context.bot.send_message(chat_id=user_id, text='Нет актуальных заявок.\n\nНажмите /start для перехода в меню.')
    else: context.bot.send_message(chat_id=user_id, text='Нажмите /start для перехода в меню.')


def scheduled(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user = classes.User.users_dict[user_id]
    query.edit_message_text(text='Запланированные заявки:')
    no_request = True

    if user.level == 2: ok = 'rok'
    else: ok = 'dok'

    for request in from_sheet_to_dict().values():
        if request.status == '🕑Запланировано' and request.boss == user_id:
            no_request = False
            keyboard = [[ikb('✅', callback_data=f'{ok}{request.id}'),
                         ikb('🕑', callback_data=f'rlt{request.id}'),
                         ikb('❌', callback_data=f'rno{request.id}')]]
            text = request.to_string()
            if user.level > 1:  text = f'Остаток: {classes.count[classes.articles.index(request.article)]}\n' + text
            context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    if no_request: context.bot.send_message(chat_id=user_id, text='Нет актуальных заявок.\n\nНажмите /start для перехода в меню.')
    else: context.bot.send_message(chat_id=user_id, text='Нажмите /start для перехода в меню.')


def rlt(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = int(data[3:])

    keyboard = [[ikb('пн',callback_data='-'), ikb('вт',callback_data='-'), ikb('ср',callback_data='-'),
    ikb('чт',callback_data='-'), ikb('пт',callback_data='-'), ikb('сб',callback_data='-'), ikb('вс',callback_data='-')]]
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_day = tomorrow - datetime.timedelta(days=tomorrow.weekday())

    for week in range(5):
        week_buttons = []
        for day in range(7):
            day_date = start_day + datetime.timedelta(days=week * 7 + day)
            if day_date >= tomorrow:
                d = day_date.strftime('%d.%m')
                week_buttons.append(ikb(d, callback_data=f'date${d}${request_id}'))
            else: week_buttons.append(ikb(' ', callback_data='-'))
        if week_buttons:  keyboard.append(week_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text('Выберите дату:', reply_markup=reply_markup)


def date(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data.split('$')
    mydate = data[1]
    request_id = data[2]
    request = from_sheet_to_dict()[int(request_id)]
    request.hidden_status = request.status
    request.status = '🕑Запланировано'
    request.planned_date = f'{mydate}'

    user = classes.User.users_dict[query.from_user.id]
    user.status = 'status_comment2'
    user.current_request = request
    query.edit_message_text(text=f'🕑Запланировано на {mydate}. Добавьте комментарий:')


def rok(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = int(data[3:])
    user = classes.User.users_dict[query.from_user.id]
    request = from_sheet_to_dict()[int(request_id)]
    request.status_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    request.status = '💼У директора'
    request.hiiden_status = '💼У директора'
    request.boss = user.boss
    query.edit_message_text(text='Заявка отправлена директору.\n\nНажмите /start для перехода в меню.')
    upd2(request.to_list())
    if user.id != request.author_id:
        context.bot.send_message(chat_id=request.author_id, text=f'Статус заявки изменён на "💼У директора":\n\n{request.to_string()}')
        context.bot.send_message(chat_id=request.author_id, text=f'Нажмите /start для перехода в меню.')


def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = int(data[4:])
    request = from_sheet_to_dict()[int(request_id)]
    request.status = '❌Отозвано'
    upd2(request.to_list())
    query.edit_message_text(text='Заявка отозвана.')


def newc(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = int(data[4:])
    user = classes.User.users_dict[query.from_user.id]
    user.status = 'newc'
    request = from_sheet_to_dict()[int(request_id)]
    user.current_request = request
    query.edit_message_text(text='Дополните комментарий:')

def ping(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    keyboard = [[ikb('пн',callback_data='-'), ikb('вт',callback_data='-'), ikb('ср',callback_data='-'),
    ikb('чт',callback_data='-'), ikb('пт',callback_data='-'), ikb('сб',callback_data='-'), ikb('вс',callback_data='-')]]
    today = datetime.date.today()
    tomorrow = today
    start_day = tomorrow - datetime.timedelta(days=tomorrow.weekday())
    request_id = query.data[4:]
    for week in range(5):
        week_buttons = []
        for day in range(7):
            day_date = start_day + datetime.timedelta(days=week * 7 + day)
            if day_date >= tomorrow:
                d = day_date.strftime('%d.%m')
                week_buttons.append(ikb(d, callback_data=f'pim${d}${request_id}'))
            else: week_buttons.append(ikb(' ', callback_data='-'))
        if week_buttons:  keyboard.append(week_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text('Выберите дату:', reply_markup=reply_markup)


def pim(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    info = query.data.split('$')
    request = from_sheet_to_dict()[int(info[2])]
    request.desired_date = info[1]
    upd2(request.to_list())
    query.answer()
    query.edit_message_text(text='Желаемая дата оплаты обновлена.')

    user_id = query.from_user.id
    text=f'Желаемая дата оплаты обновлена:\n\n{request.to_string()}\n\nНажмите /start для перехода в меню.'
    if user_id != request.author_boss: context.bot.send_message(chat_id=request.author_boss, text=text)
    if request.boss != request.author_boss: context.bot.send_message(chat_id=request.boss, text=text)

def rno(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = data[3:]
    user = classes.User.users_dict[query.from_user.id]
    user.status = 'status_comment1'
    request = from_sheet_to_dict()[int(request_id)]
    user.current_request = request
    request.hidden_status = request.status
    request.status = '❌Отказано'
    query.edit_message_text(text='Заявка отклонена. Добавьте комментарий:')


def dok(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    request_id = int(data[3:])
    classes.User.users_dict[query.from_user.id].current_request = from_sheet_to_dict()[int(request_id)]

    keyboard = [[ikb('Сбер', callback_data='Сбер'), ikb('Райф', callback_data=f'Райф'),
                 ikb('Альфа', callback_data='Альфа'), ikb('Точка', callback_data='Точка'), ikb('Другой', callback_data=f'drug')]]

    query.edit_message_text(text='Укажите банк:', reply_markup=InlineKeyboardMarkup(keyboard))


def drug(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    classes.User.users_dict[query.from_user.id].status = 'drug'
    query.edit_message_text(text='Укажите название:')


def bank(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user = classes.User.users_dict[user_id]

    request = user.current_request
    request.status_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    request.status = '✅Оплачено'
    request.payment_bank = query.data
    request.hiiden_status = '💼У директора'
    classes.count[classes.articles.index(request.article)] -= request.amount

    query.edit_message_text(text='✅Оплачено')
    upd2(request.to_list())
    text = f'Статус заявки изменён на "✅Оплачено":\n\n{request.to_string()}\n\nНажмите /start для перехода в меню.'
    if user_id != request.author_id: context.bot.send_message(chat_id=request.author_id, text=text)
    if user_id != request.author_boss: context.bot.send_message(chat_id=request.author_boss, text=text)