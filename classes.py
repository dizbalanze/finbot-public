class User:
    users_dict = {}
    def __init__(self, user_id, level, name, boss, articles_str):
        self.id = user_id
        self.level = level
        self.name = name
        self.boss = boss
        self.articles = [int(num) - 2 for num in articles_str.split(',')]
        self.status = None
        self.current_request = None
        self.requests = []
        User.users_dict[user_id] = self

class Request:
    def __init__(self, values=None):
        if values is None:
            values = [None, None, None, None, None, None, None, None, '💼У руководителя', None, None, '-', '-', None, '-',
            1, '💼У руководителя', None, None, None, None]

        (self.start_date, self.author_name, self.amount, self.article, self.comment, self.payment_type, self.recipient, self.bank_and_phone,
         self.status, self.status_date, self.check, self.planned_date, self.status_comment, self.desired_date, self.payment_bank,

         self.id, self.hidden_status, self.boss, self.author_level, self.author_boss, self.author_id) = values

    def to_list(self):
        return [self.start_date, self.author_name, self.amount, self.article, self.comment, self.payment_type, self.recipient, self.bank_and_phone,
                self.status, self.status_date, self.check, self.planned_date, self.status_comment, self.desired_date, self.payment_bank,

                self.id, self.hidden_status, self.boss, self.author_level, self.author_boss, self.author_id]

    #Остаток: {count[articles.index(self.article)]}
    def to_string(self):
        result = f'Автор: #{self.author_name}\nСтатья: #{self.article}\nСумма: {self.amount}\n\
Тип: {self.payment_type}\nПолучатель: {self.recipient}\nКомментарий: {self.comment}\nЖелаемая дата платежа: {self.desired_date}\n\
Планируемая дата: {self.planned_date}\nСтатус: {self.status}\nКомментарий статуса: {self.status_comment}\n'

        if self.payment_type == 'перевод': result += f'Реквизиты: {self.bank_and_phone}'
        else: result += f'Статус счёта: {self.check}'
        return result


articles = ["Затраты на закупку молока и сливок",
    "Расходы на электроэнергию",
    "Издержки на хранение мороженого",
    "Производственные расходы",
    "Затраты на упаковку мороженого",
    "Транспортные расходы",]

count = [57483, 32578, 87643, 48712, 65291, 74569]

def cupd(art, cnt):
    global articles
    global  count
    articles = art
    count = cnt
