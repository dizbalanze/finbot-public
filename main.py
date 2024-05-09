from telegram import Bot, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from classes import *
from approve import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

def daily_task():
    mydate = datetime.datetime.now().strftime('%d.%m')
    for request in from_sheet_to_dict().values():
        if request.status == '🕑Запланировано' and request.planned_date == mydate:
            request.status = request.hidden_status
            upd2(request.to_list())

scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)
scheduler.add_job(daily_task, 'cron', hour=0, minute=1)


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret2.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Заявки").sheet1


def from_sheet_to_dict():
    values = sheet.get_all_values()[1:]
    filtered_values = [row for row in values if any(row)]
    requests = {}
    for v in filtered_values:
        v[2] = float(v[2].replace(",", ".")); v[15] = int(v[15]); v[17] = int(v[17]); v[18] = int(v[18]); v[19] = int(v[19]); v[20] = int(v[20])
        r = Request(v)
        requests[v[15]] = r

    return requests

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in User.users_dict:
        update.message.reply_text('Нет доступа')
    elif User.users_dict[user_id].level == 1:
        keyboard = [[ikb('Заявка на расход средств', callback_data='new_request')],
                    [ikb('Мои заявки', callback_data='my_requests')],]
        update.message.reply_text('Пожалуйста, выберите:', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[ikb('Заявка на расход средств', callback_data='new_request')],
                    [ikb('Мои заявки', callback_data='my_requests')],
                    [ikb('Заявки на согласование', callback_data='for_approval')],
                    [ikb('История согласованных заявок', callback_data='history_approved')],
                    [ikb('Запланированные заявки', callback_data='scheduled')]]
        update.message.reply_text('Пожалуйста, выберите:', reply_markup=InlineKeyboardMarkup(keyboard))


def my_requests(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    no_request = True
    query.edit_message_text(text='Ваши заявки:')
    for r in from_sheet_to_dict().values():
        if r.author_id == user_id and r.status != '❌Отозвано':
            no_request = False
            keyboard = [[ikb('❌', callback_data=f'back{r.id}'), ikb('📆', callback_data=f'ping{r.id}'), ikb('💬', callback_data=f'newc{r.id}')]]
            context.bot.send_message(chat_id=user_id, text=r.to_string(), reply_markup=InlineKeyboardMarkup(keyboard))
    if no_request: context.bot.send_message(chat_id=user_id, text='Нет актуальных заявок\n\nНажмите /start для перехода в меню.')
    else:  context.bot.send_message(chat_id=user_id, text='Нажмите /start для перехода в меню.')


def upd(row, value_list):
    myrange = f"A{row}:U{row}"
    sheet.update(range_name=myrange, values=[value_list])

def upd2(value_list):
    myid = value_list[15]
    strids = sheet.col_values(16)[1:]
    ids = []
    for s in strids:
        ids.append(int(s))
    row = ids.index(myid)+2
    myrange = f"A{row}:U{row}"
    sheet.update(range_name=myrange, values=[value_list])

def registration(update: Update, context: CallbackContext) -> None:
    User.users_dict = {}
    mysheet = client.open("Пользователи").sheet1
    values = mysheet.get_all_values()
    filtered_values = [row for row in values if any(row)]
    for v in filtered_values[1:]:
        User.users_dict[v[0]] = User(int(v[0]), int(v[1]), v[2], int(v[3]), v[4])
    update.message.reply_text('Регистрация завершена')


def money(update: Update, context: CallbackContext) -> None:
    mysheet = client.open("Бюджеты").sheet1
    current_month = datetime.datetime.now().month
    art = mysheet.col_values(1)[1:]
    moneys = mysheet.col_values(current_month+1)[1:]
    coun = []
    for m in moneys: coun.append(int(m))
    cupd(art, coun)
    update.message.reply_text('Обновлено')

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    user = User.users_dict[user_id]
    status = user.status
    if status is None: update.message.reply_text('Неизвестная команда')
    if status == 'article':
        try:
            amount = float(user_message.replace(",", "."))
            if amount < 1:
                update.message.reply_text('Сумма не может быть меньше 1')
            else:
                user.current_request.amount = amount
                keyboard = [[ikb('р/с', callback_data='rs'), ikb('перевод СБП', callback_data='sbp')]]
                update.message.reply_text('Выбор типа оплаты:', reply_markup=InlineKeyboardMarkup(keyboard))

        except ValueError: update.message.reply_text('Ошибка ввода. Укажите сумму ещё раз:')

    elif status == 'rs':
        user.current_request.recipient =  user_message
        keyboard = [[ikb('Отправлен', callback_data='sent'), ikb('Не отправлен', callback_data='not_sent')]]
        text = 'Укажите отправлен ли был текущий счёт на почту Бухгалтера Екатерины Гордеевой gordeevaevekaterina@yandex.ru\n(WA +7 921 757-63-50):'
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif status == 'sbp':
        user.current_request.recipient = user_message
        user.current_request.check = '-'
        user.status = 'phone'
        update.message.reply_text('Укажите телефон получателя и банк:')

    elif status == 'phone':
        user.current_request.bank_and_phone = user_message
        keyboard = [[ikb('Да', callback_data='desy'), ikb('Нет', callback_data='desn')]]
        update.message.reply_text('Есть ли желаемая дата платежа?', reply_markup=InlineKeyboardMarkup(keyboard))

    elif status == 'newc':
        user.status = None
        user.current_request.comment += f' | {user_message}'
        upd2(user.current_request.to_list())
        update.message.reply_text('Комментарий дополнен')

    elif status == 'сomment':
        user.status = None
        user.current_request.comment = user_message
        mydate = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        user.current_request.start_date = mydate
        user.current_request.status_date = mydate
        success = True
        for element in user.current_request.to_list():
            if element is None:
                print(user.current_request.to_list())
                update.message.reply_text('Ошибка заполенения данных')
                success = False
                break
        if success:
            mydict = from_sheet_to_dict()
            if mydict: user.current_request.id = max(mydict.keys())+1
            else: user.current_request.id = 2
            if user.level > 1: user.current_request.status = '💼У директора'
            upd(len(from_sheet_to_dict())+2, user.current_request.to_list())
            user.current_request.boss = user.boss
            if user.boss != user.id:
                context.bot.send_message(chat_id=user.boss, text=f'Получена заявка:\n\n{user.current_request.to_string()}\n\nНажмите /start для перехода в меню.')
            user.current_request = None
            update.message.reply_text('Заявка создана.\n\nНажмите /start для перехода в меню.')

    elif status == 'drug':
        user.status = None
        request = user.current_request
        request.status_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        request.payment_bank = user_message
        request.status = '✅Оплачено'
        request.hiiden_status = '💼У директора'
        classes.count[classes.articles.index(request.article)] -= request.amount
        upd2(user.current_request.to_list())

        text = f'Статус заявки изменён на "✅Оплачено":\n\n{request.to_string()}\n\nНажмите /start для перехода в меню.'
        if user_id != request.author_id: context.bot.send_message(chat_id=request.author_id, text=text)
        if user_id != request.author_boss: context.bot.send_message(chat_id=request.author_boss, text=text)
        update.message.reply_text('✅Оплачено')

    elif status.startswith("status_comment"):
        user.status = None
        user.current_request.status_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        user.current_request.status_comment = user_message
        upd2(user.current_request.to_list())

        if status[-1] == '2': stat = '🕑Запланировано'
        else: stat = '❌Отказано'

        text = f'Статус заявки изменён на "{stat}":\n\n{user.current_request.to_string()}\n\nНажмите /start для перехода в меню.'

        if user.id != user.current_request.author_id: context.bot.send_message(chat_id=user.current_request.author_id, text=text)
        if user.level == 3 and user.current_request.author_level == 1: context.bot.send_message(chat_id=user.current_request.author_boss, text=text)

        user.current_request = None
        update.message.reply_text('Комментарий добавлен.\n\nНажмите /start для перехода в меню.')


if __name__ == '__main__':
    print('Input token:')
    bot_token = input()
    scheduler.start()
    print('start')

    menu_commands = [('start', 'Главное меню'),('registration', 'Проверить доступ'),('money', 'Обновить бюджеты статей')]
    command_handlers = {'start': start, 'registration': registration, 'money': money}
    callback_query_handlers = {'^\d+$': amount_request, 'new_request': new_request, 'rs': rs, 'sbp': sbp, 'sent': sent, 'not_sent': not_sent,
    'desy': desy, 'my_requests': my_requests, 'for_approval': for_approval, 'history_approved': history_approved, 'scheduled': scheduled,
    '^back.*': back, '^newc.*': newc, '^des.*': des, '^rok.*': rok, '^(Сбер|Райф|Альфа|Точка)': bank, 'drug': drug, '^rlt.*': rlt, '^date.*': date,
    '^rno.*': rno, '^dok.*': dok, '^ping.*': ping, '^pim.*': pim}

    bot = Bot(bot_token)
    bot.set_my_commands([BotCommand(command, description) for command, description in menu_commands])

    updater = Updater(bot_token, use_context=True)
    for command, handler in command_handlers.items(): updater.dispatcher.add_handler(CommandHandler(command, handler))
    for pattern, handler in callback_query_handlers.items(): updater.dispatcher.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()
