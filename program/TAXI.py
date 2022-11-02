import sys
import sqlite3
import datetime as dt
import math
import hashlib
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QRadioButton, QButtonGroup, QLineEdit, QTableWidgetItem
from PyQt5 import uic


class Entrance(QMainWindow):  # Этот класс отвечает за окно авторизации
    def __init__(self):
        super().__init__()
        uic.loadUi(r'entrance_new.ui', self)
        self.hints()
        self.buttons()

    def hints(self):  # Генерирует подзказки в окне
        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.label_2.setToolTip("Login")
        self.label_3.setToolTip("Password")
        self.lineEdit.setToolTip("Здесь вводить имеющийся логин")
        self.lineEdit.setToolTipDuration(4000)
        self.lineEdit_2.setToolTip("Здесь вводить имеющийся пароль")
        self.lineEdit_2.setToolTipDuration(4000)
        self.pushButton.setToolTip("""Впервые пользуютесь нашим приложением?
                          Кликайте сюда!""")
        self.pushButton.setToolTipDuration(4000)
        self.pushButton_2.setToolTip("""  Ввели все данныe?  
    Кликайте сюда!  """)
        self.pushButton_2.setToolTipDuration(4000)

    def buttons(self):  # привязываем функционал кнопок
        self.pushButton.clicked.connect(self.open_registration_form)
        self.pushButton_2.clicked.connect(self.verification)

    def open_registration_form(self):  # Закрывает текущее оно открывает новое окно регистрации
        self.close()
        self.registration_form = Registration()
        self.registration_form.show()

    def verification(self):  # Проверка, и если все верно, то переходим к окну заказа
        id_user = self.check_base_to_login_and_password()
        if id_user:
            self.open_choice_form(id_user)

    def check_base_to_login_and_password(self):  # проверка на наличие указанного логина в базе данных
        if self.lineEdit.text() and self.lineEdit_2.text():
            con = sqlite3.connect("TAXI.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT id, salt, password FROM Users
                WHERE name = ?""", (self.lineEdit.text(),)).fetchone()
            con.close()
            if not result:
                self.label_4.setText("Неправильно введен логин. Попробуйте ввести данные снова.")
                return None
            else:
                salt = result[1]  # Получение соли
                key = result[2]  # Получение правильного ключа
                new_key = hashlib.pbkdf2_hmac('sha256', self.lineEdit_2.text().encode('utf-8'), salt, 100000)
                if key == new_key:
                    return result[0]
                else:
                    self.label_4.setText("Неправильно введен пароль. Попробуйте ввести данные снова.")
                    return None
        else:
            self.label_4.setText("Введите данные.")
            return None

    def open_choice_form(self, id_user):  # Закрывает текущее оно открывает новое окно выбора
        self.close()
        self.form = Information(id_user)
        self.form.show()


class Registration(QWidget):  # Этот класс отвечает за окно регистрации
    def __init__(self):
        super().__init__()
        uic.loadUi(r'registration_taxi.ui', self)
        self.hints()
        self.check()

    def hints(self):  # Генерирует подзказки в окне
        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.lineEdit_3.setEchoMode(QLineEdit.Password)
        self.label_2.setToolTip("Логин должен быть уникальным")
        self.label_2.setToolTipDuration(4000)
        self.label_3.setToolTip("""Пароль должен соответствовать следующим требованиям:
        1) Длинна больше 8 символов;
        2) В нем должны быть буквы разных регистров;
        3) В нем должны быть цифры;
        4) Не должно быть сочетаний рядомстоящих букв (йцу,qwe,...)""")
        self.label_4.setToolTip("""Этот пароль должен быть идентичен предыдущему""")
        self.lineEdit.setToolTip("Здесь вводить логин")
        self.lineEdit.setToolTipDuration(4000)
        self.lineEdit_2.setToolTip("Здесь вводить пароль")
        self.lineEdit_2.setToolTipDuration(4000)
        self.lineEdit_3.setToolTip("Здесь вводить пароль второй раз")
        self.lineEdit_3.setToolTipDuration(4000)
        self.pushButton.setToolTip("""  Ввели все данныe?  
    Кликайте сюда!  """)
        self.pushButton.setToolTipDuration(4000)

    def check(self):  # Привызывает функционал кнопок
        # self.lineEdit.editingFinished.connect(self.true_login())
        self.pushButton.clicked.connect(self.registration_and_entrance)

    def registration_and_entrance(self):  # Проверка правильности ввода данных
        if self.true_login() and self.true_passwords():
            id_user = self.add_user()
            self.open_choice_form(id_user)

    def true_login(self):  # Проверка правильности ввода логина
        if self.lineEdit.text() == '':
            self.label_6.setText('Напишите имя')
            return True
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        result = cur.execute(
            f"""SELECT id FROM Users WHERE Name = '{self.lineEdit.text()}'""").fetchall()
        con.close()
        if result:
            self.label_6.setText('К сожалению, такой логин уже существует')
            return False
        else:
            self.label_6.clear()
            return True

    def add_user(self):  # Добавляет аккаунт пользователя в бд
        self.hash()
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        cur.execute("""INSERT INTO Users(Name, password, salt) 
            VALUES(?, ?, ?)""", (self.lineEdit.text(), self.key, self.salt)).fetchone()
        con.commit()
        rez = cur.execute("SELECT id FROM Users WHERE name = ?", (self.lineEdit.text(),)).fetchone()
        con.close()
        return rez[0]

    def hash(self):  # Шифрует пароль
        self.salt = os.urandom(32)  # Новая соль для данного пользователя
        self.key = hashlib.pbkdf2_hmac('sha256', self.lineEdit_2.text().encode('utf-8'), self.salt, 100000)

    def true_passwords(self):  # Проверка правильности ввода пароля
        letter_3_list = [
            'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio', 'iop',
            'asd', 'sdf', 'dfg', 'fgh', 'ghj', 'hjk', 'jkl',
            'zxc', 'xcv', 'cvb', 'vbn', 'bnm',
            'йцу', 'цук', 'уке', 'кен', 'енг', 'нгш', 'гшщ', 'шщз', 'щзх', 'зхъ',
            'фыв', 'ыва', 'вап', 'апр', 'про', 'рол', 'олд', 'лдж', 'джэ',
            'ячс', 'чсм', 'сми', 'мит', 'ить', 'тьб', 'ьбю', 'жэё'
        ]
        if self.lineEdit_2.text() == '' or self.lineEdit_3.text() == '':
            self.label_5.setText('Напишите пароль')
            return False

        elif len(self.lineEdit_2.text()) <= 8:
            self.label_5.setText('Слишком короткий')
            return False

        elif self.lineEdit_2.text().lower() == self.lineEdit_2.text() or \
                self.lineEdit_2.text().upper() == self.lineEdit_2.text():
            self.label_5.setText('В пароле должны быть буквы разных регистров')
            return False

        elif not any(i in self.lineEdit_2.text() for i in list('0123456789')):
            self.label_5.setText('В пароле должны быть цифры')
            return False

        elif any([i in self.lineEdit_2.text().lower() for i in letter_3_list]):
            self.label_5.setText('В пароле не должно быть сочетаний рядомстоящих букв')
            return False

        elif self.lineEdit_2.text() != self.lineEdit_3.text():
            self.label_5.setText('Пароли различаются')
            return False
        self.label_5.clear()
        return True

    def open_choice_form(self, id_user):  # Закрывает текущее окно открывает новое окно информации о текущих заказах
        self.close()
        self.choice_form = Choice(id_user)
        self.choice_form.show()


class Information(QWidget):  # Этот класс отвечает за окно вывода таблицы заказов
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        uic.loadUi(r'info_order.ui', self)
        self.hints()
        self.creation()
        self.buttons()

    def hints(self):  # Генерирует подзказки в окне
        self.pushButton.setToolTip("""Хотите изменить статус заказа?
              Кликайте сюда!""")
        self.pushButton.setToolTipDuration(4000)
        self.pushButton_2.setToolTip("""  Хотите оформить новый заказ?  
              Кликайте сюда!  """)
        self.pushButton_2.setToolTipDuration(4000)
        self.tableWidget.setToolTip("""Чтобы изменить статус заказа выберите нужный(ые) заказ(ы).
        После чего нажмите соответствующую кнопку.""")

    def buttons(self):  # Привызывает функционал кнопок
        self.pushButton.clicked.connect(self.change)
        self.pushButton_2.clicked.connect(self.open)

    def open(self):  # Закрывает текущее окно открывает новое окно выбора условий заказа

        self.close()
        self.choice_form = Choice(self.id_user)
        self.choice_form.show()

    def change(self):  # При нажатии на кнопку изменяет статус выбранных заказов и вносит изменения в таблицу
        sp_index = []
        selected_id = []
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        if self.result:
            row_num = self.tableWidget.selectedItems()
            for j in row_num:
                sp_index.append(j.row())
            for i in sp_index:
                selected_id.append(self.result[i][0])
            for id in selected_id:
                cur.execute("""UPDATE Receipt SET status_id = (SELECT id FROM receipt_status WHERE name = "Завершен")
                WHERE id = ?""", (id,)).fetchone()
                cur.execute("""UPDATE Driver SET status_po_zakazy_id =
                (SELECT id FROM driver_status_in_receipt WHERE name = "Свободен")
                WHERE id = (SELECT driver_id FROM Receipt WHERE id = ?)""", (id,)).fetchone()
                con.commit()
            con.close()
            self.creation()

    def creation(self):  # Создает таблицу из заказов пользователя
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        self.result = cur.execute("""SELECT Receipt.id, Receipt.date_of_need_for_user, Driver.name, receipt_status.name,
        Receipt.cost
        FROM Receipt
        INNER JOIN Driver
        ON Receipt.driver_id = Driver.id
        INNER JOIN receipt_status
        ON receipt_status.id = Receipt.status_id
        WHERE Receipt.user_id = ? AND receipt_status.name = "В работе"
        ORDER BY Receipt.date_of_need_for_user DESC""", (self.id_user,)).fetchall()
        try:
            self.tableWidget.setRowCount(len(self.result))
            self.tableWidget.setColumnCount(len(self.result[0]))
            self.tableWidget.setHorizontalHeaderLabels(["Номер", "Дата", "Водитель", "Статус", "Стоимость(в рублях)"])
            for i, elem in enumerate(self.result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.tableWidget.resizeColumnsToContents()
        except Exception:
            pass
        finally:
            con.close()


class Choice(QWidget):  # Этот класс отвечает за окно выбора условий заказа
    def __init__(self, id_user):
        super().__init__()
        uic.loadUi(r'choice.ui', self)
        self.id_user = id_user
        self.con = sqlite3.connect("TAXI.db")
        self.run()

    def run(self):  # Запускает все необходимые методы
        self.hints()
        self.set_current_time()
        self.add_radio_button()
        self.select_city()
        self.select_house()
        self.select_house1()
        self.buttons()
        self.conditions()

    def hints(self):  # Генерирует подзказки в окне
        self.comboBox.setToolTip("""Здесь вам необходимо выбрать город в котором вы находитесь
                                      (Откуда вы поедете)""")
        self.comboBox.setToolTipDuration(4500)
        self.comboBox_2.setToolTip("""Здесь вам необходимо выбрать улицу на которой вы находитесь
                                        (Откуда вы поедете)""")
        self.comboBox_2.setToolTipDuration(4500)
        self.comboBox_3.setToolTip("""Здесь вам необходимо выбрать дом в кротором вы находитесь
                                        (Откуда поедете)""")
        self.comboBox_3.setToolTipDuration(4500)
        self.comboBox_4.setToolTip("""Здесь вам необходимо выбрать город в которы вы хотите поехать""")
        self.comboBox_4.setToolTipDuration(4500)
        self.comboBox_5.setToolTip("""Здесь вам необходимо выбрать улицу на которую вы хотите поехать""")
        self.comboBox_5.setToolTipDuration(4500)
        self.comboBox_6.setToolTip("""Здесь вам необходимо выбрать дом в кроторый вы хотите поехать""")
        self.comboBox_6.setToolTipDuration(4500)
        self.dateTimeEdit.setToolTip("""Здесь вы должны выбрать время на которое вам нужен автомобиль
                 (Когда водитель должен будет за вами подехать)""")
        self.dateTimeEdit.setToolTipDuration(5000)
        self.pushButton.setToolTip("""  Ввели все данныe?  
    Кликайте сюда!  """)
        self.pushButton.setToolTipDuration(4000)

    def conditions(self):  # Создает условия изменения выбора (города\улицы\дома)
        self.comboBox.currentIndexChanged[str].connect(self.select_street)
        self.comboBox_4.currentIndexChanged[str].connect(self.select_street1)
        self.comboBox_2.currentIndexChanged[str].connect(self.select_house)
        self.comboBox_5.currentIndexChanged[str].connect(self.select_house1)

    def set_current_time(self):  # Устанавливает текущее время
        current_time = dt.datetime.now()
        self.dateTimeEdit.setDateTime(current_time)

    def add_radio_button(self):  # Добавляет кнопри классов авто
        cur = self.con.cursor()
        classes = cur.execute(
            """SELECT name FROM class_car""").fetchall()
        row = 1
        self.group = QButtonGroup(self)
        for i in range(len(classes)):
            column = i % 3
            if i % 3 == 0:
                row += 1
            button = QRadioButton(classes[i][0])
            button.setChecked(True)
            self.group.addButton(button)
            self.gridLayout.addWidget(button, row, column)

    def check_class_car(self):  # Проверяет наличие выбранного класса авто у свободных водителей
        self.con = sqlite3.connect("TAXI.db")
        name_class_car = self.get_car()
        time = self.check_time_of_receipt()
        cur = self.con.cursor()
        rez = cur.execute("""SELECT id FROM Driver WHERE status_of_work_id = 
        (SELECT id FROM driver_status WHERE name = ?) AND class_car_id = 
        (SELECT id FROM class_car WHERE name = ?) AND status_po_zakazy_id = 
        (SELECT id FROM driver_status_in_receipt WHERE name = "Свободен")""",
                          (time, name_class_car)).fetchone()
        if rez:
            self.label_error.clear()
            return True
        else:
            self.label_error.setText('К сожалению в данных момент нет свободных авто данного класса. Выберите другой.')
            return False

    def check_time_of_receipt(self):  # Проверяет дату выставленную пользователем
        # чтобы определить в какой смене необходим водитель
        time = self.dateTimeEdit.time().toString("hh:mm:ss")
        if 18 > int(time.split(":")[0]) > 6:
            return "Дневная"
        else:
            return "Ночная"

    def get_car(self):  # Получает название выбранного класса авто
        return self.group.checkedButton().text()

    def buttons(self):  # Привязываем функционал кнопок
        self.pushButton.clicked.connect(self.verification)

    def verification(self):  # Проверка всех условий
        if not self.same_addresses() and self.correct_time() and self.check_class_car():
            self.add_receipt_to_db()
            id_receipt = self.give_id_receipt()
            self.open_pay_form(id_receipt)

    def same_addresses(self):  # Условия одинаковых адресов
        if self.comboBox.currentText() == self.comboBox_4.currentText() and \
                self.comboBox_2.currentText() == self.comboBox_5.currentText() and \
                self.comboBox_3.currentText() == self.comboBox_6.currentText():
            self.label_error.setText('Одинаковые адреса')
            return True
        else:
            return False

    def correct_time(self):  # Условия правильного времени
        delta_time = dt.timedelta(minutes=10)
        current_time = dt.datetime.now()
        q_date = self.dateTimeEdit.dateTime()
        time = dt.datetime(q_date.date().year(), q_date.date().month(), q_date.date().day(),
                           q_date.time().hour(), q_date.time().minute())
        if time < current_time + delta_time:
            self.label_error.setText('Неправильное время. Мы не можем приехать быстрее 10 минут')
            return False
        else:
            return True

    def select_city(self):  # Вытаскивает из бд города
        params_city = {}
        req = "SELECT id, name from City"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall():
            params_city[key] = value
        self.comboBox.addItems(list(params_city.keys()))
        self.comboBox_4.addItems(list(params_city.keys()))
        self.select_street()
        self.select_street1()

    def select_street(self):  # Вытаскивает из базы данных улицы  для (откуда), заполняет комбобоксы улицами
        params_street = {}
        cur = self.con.cursor()
        for value, key in cur.execute(
                """SELECT id, name from Street WHERE city_id = 
                (SELECT id FROM City WHERE name = ?)""", (self.comboBox.currentText(),)).fetchall():
            params_street[key] = value
        self.comboBox_2.clear()
        self.comboBox_2.addItems(list(params_street.keys()))

    def select_street1(self):  # Вытаскивает из базы данных улицы для (куда), заполняет комбобоксы улицами
        params_street = {}
        cur = self.con.cursor()
        for value, key in cur.execute(
                """SELECT id, name from Street WHERE city_id = 
                (SELECT id FROM City WHERE name = ?)""", (self.comboBox_4.currentText(),)).fetchall():
            params_street[key] = value
        self.comboBox_5.clear()
        self.comboBox_5.addItems(list(params_street.keys()))

    def select_house(self):  # Вытаскивает из базы данных дома для (откуда), заполняет комбобоксы домами
        params_house = {}
        cur = self.con.cursor()
        for value, key in cur.execute(
                """SELECT id, name from House WHERE street_id = 
                (SELECT id FROM Street WHERE name = ?)""",
                (self.comboBox_2.currentText(),)).fetchall():
            params_house[key] = value
        self.comboBox_3.clear()
        self.comboBox_3.addItems(list(params_house.keys()))

    def select_house1(self):  # Вытаскивает из базы данных дома для (куда), заполняет комбобоксы домами
        params_house = {}
        cur = self.con.cursor()
        for value, key in cur.execute(
                """SELECT id, name from House WHERE street_id = 
                (SELECT id FROM Street WHERE name = ?)""",
                (self.comboBox_5.currentText(),)).fetchall():
            params_house[key] = value
        self.comboBox_6.clear()
        self.comboBox_6.addItems(list(params_house.keys()))

    def add_receipt_to_db(self):  # Добавляет заказ в бд
        cur = self.con.cursor()
        self.house_a_id = cur.execute(
            """SELECT id FROM House WHERE name = ? and street_id = 
            (SELECT id FROM Street WHERE name = ? AND city_id = 
            (SELECT id FROM City WHERE name = ?))""", (self.comboBox_3.currentText(), self.comboBox_2.currentText(),
                                                       self.comboBox.currentText())).fetchone()
        self.house_b_id = cur.execute(
            """SELECT id FROM House WHERE name = ? and street_id =
            (SELECT id FROM street WHERE name = ? AND city_id = 
            (SELECT id FROM city WHERE name = ?))""", (self.comboBox_6.currentText(), self.comboBox_5.currentText(),
                                                       self.comboBox_4.currentText())).fetchone()
        a = cur.execute("""SELECT latitude, longitude FROM House WHERE id = ?""",
                        (self.house_a_id[0],)).fetchone()
        b = cur.execute("""SELECT latitude, longitude FROM House WHERE id = ?""",
                        (self.house_b_id[0],)).fetchone()
        self.driver = self.select_driver(a)
        cost = self.calculate_cost(a, b)
        need_time = self.dateTimeEdit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        status = cur.execute("""SELECT id FROM receipt_status WHERE name = 'Не взят'""").fetchone()
        cur.execute("""INSERT INTO Receipt(date_of_need_for_user, status_id, user_id,
             driver_id, cost, house_a_id, house_b_id) VALUES(?, ?, ?, ?, ?, ?, ?)""",
                    (need_time, status[0], self.id_user,
                     self.driver, cost, self.house_a_id[0], self.house_b_id[0])).fetchone()
        self.con.commit()
        self.con.close()

    def select_driver(self, a):  # Вытаскивает из бд водителя (его id)
        sp_drivers = []
        name_class_car = self.get_car()
        time = self.check_time_of_receipt()
        cur = self.con.cursor()
        rez = cur.execute("""SELECT id FROM Driver WHERE status_of_work_id = 
                (SELECT id FROM driver_status WHERE name = ?) AND class_car_id = 
                (SELECT id FROM class_car WHERE name = ?) AND status_po_zakazy_id = 
                (SELECT id FROM driver_status_in_receipt WHERE name = "Свободен")""",
                          (time, name_class_car)).fetchall()
        for i in rez:
            latitude_and_longitude = cur.execute("""SELECT latitude, longitude FROM House WHERE id = 
            (SELECT house_id FROM Driver WHERE id = ?)""",
                                                 (i[0],)).fetchone()
            long = self.calculate_len(latitude_and_longitude, a)
            sp_drivers.append((long, i[0]))
        driver_id = min(sp_drivers)
        return driver_id[1]

    def calculate_cost(self, a, b):  # Подсчитывает стоимость заказа
        min_cost = 40
        long = self.calculate_len(a, b)
        k = 10
        cost_class_car = self.con.cursor().execute("""SELECT cost FROM class_car WHERE id = 
        (SELECT class_car_id FROM Driver WHERE id = ?)""", (self.driver,)).fetchone()
        cost = float(long * (k + cost_class_car[0])) + min_cost
        cost = math.ceil(cost)
        return int(cost)

    def calculate_len(self, a, b):  # Вычисляет рассояние между двумя адресами
        r = 6371
        long = 2 * r * math.asin(math.sqrt(math.sin((math.radians(b[0]) - math.radians(a[0])) / 2) ** 2
                                           + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
                                           * math.sin((math.radians(b[1]) - math.radians(a[1])) / 2) ** 2))
        return long

    def give_id_receipt(self):  # Вытаскивает заказ из бд (его _id)
        self.con = sqlite3.connect("TAXI.db")
        cur = self.con.cursor()
        id = cur.execute("""SELECT MAX(id) FROM Receipt""").fetchone()
        return id[0]

    def open_pay_form(self, id_receipt):  # Закрывает текущее окно открывает новое окно оплаты

        self.close()
        self.pay_form = Pay(id_receipt)
        self.pay_form.show()


class Pay(QWidget):  # Этот класс отвечает за окно оплаты заказа
    def __init__(self, id_receipt):
        super().__init__()
        uic.loadUi(r'pay.ui', self)
        self.id_receipt = id_receipt
        self.hints()
        self.check_db()
        self.add_cost()
        self.button()

    def check_db(self):  # Проверяет налицие у этого пользователя такой же карты
        self.params_cards = {}
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        rez = cur.execute("""SELECT id, id FROM Cards_info WHERE user_id = 
        (SELECT user_id FROM Receipt WHERE id = ?)""", (self.id_receipt,)).fetchall()
        if rez:
            self.comboBox.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.comboBox.setToolTip("""Здесь вы можете выбрать одну из сохраненных карт""")
            self.pushButton.setToolTip("""Хотите внести информацию с выбранной карты?
                 Кликайте сюда!""")
            for value, key in enumerate(rez):
                self.params_cards[str(value + 1)] = key[0]
            self.comboBox.addItems(list(self.params_cards.keys()))
        con.close()

    def hints(self):  # Генерирует подзказки в окне
        self.line_cvv.setEchoMode(QLineEdit.Password)
        self.lineEdit.setToolTip("""Здесь указана стоимость поездки (в рублях)""")
        self.lineEdit.setToolTipDuration(4000)
        self.line_card.setToolTip("""Здесь вам необходимо ввести номер карты (без пробелов)""")
        self.line_card.setToolTipDuration(4000)
        self.line_month.setToolTip("""Здесь вам необходимо указать месяц с карты""")
        self.line_month.setToolTipDuration(4000)
        self.line_year.setToolTip("""Здесь вам необходимо указать год с карты""")
        self.line_year.setToolTipDuration(4000)
        self.line_cvv.setToolTip("""Здесь вам небходимо указать CVV с обратной стороны карты""")
        self.line_cvv.setToolTipDuration(4000)
        self.check_card.setToolTip("""Если вы установите голочку, то мы сохраним информацию о вашей карте
         для будующих покупок""")
        self.check_card.setToolTipDuration(4000)
        self.comboBox.setToolTip("""""")
        self.pushButton.setToolTip("""""")
        self.btn.setToolTip("""  Ввели все данныe?  
    Кликайте сюда!  """)
        self.btn.setToolTipDuration(4000)

    def add_cost(self):  # Вытягмвает из бд и добавляет в окно стоимость заказа
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        cost = cur.execute("""SELECT cost FROM Receipt WHERE id = ?""",
                           (self.id_receipt,)).fetchone()
        cost = math.ceil(cost[0])
        self.lineEdit.setText(str(cost))
        con.close()

    def button(self):  # привязываем функционал кнопок
        self.btn.clicked.connect(self.check)
        self.pushButton.clicked.connect(self.write_in)

    def write_in(self):  # Привязываем функционал кнопок
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        rez = cur.execute("""SELECT numbers, cvv, month, year FROM Cards_info WHERE id = ?""",
                          (self.params_cards[self.comboBox.currentText()],)).fetchone()
        self.line_card.setText(str(rez[0]))
        self.line_cvv.setText(str(rez[1]))
        self.line_month.setText(str(rez[2]))
        self.line_year.setText(str(rez[3]))
        con.close()

    def check(self):  # Проверяем правильность заполнения полей
        if self.true_card() and self.true_date() and self.true_cvv():
            if self.check_card.isChecked():
                self.add_card_data()
            self.update_driver_rec()
            self.open_receipt_form()

    def get_card_number(self):  # Получаем номер карты
        return self.line_card.text()

    def update_driver_rec(self):  # Если пользователь правильно ввел данные карты (т.е типо произошла оплата),
        # то статус водителя и заказа меняются
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        cur.execute("""UPDATE Driver SET status_po_zakazy_id =
         (SELECT id FROM driver_status_in_receipt WHERE name = "Занят") WHERE id = 
         (SELECT driver_id FROM Receipt WHERE id = ?)""",
                    (self.id_receipt,)).fetchone()
        cur.execute("""UPDATE Receipt SET status_id = (SELECT id FROM receipt_status WHERE name = 'В работе')
        WHERE id = ?""", (self.id_receipt,)).fetchone()
        con.commit()
        con.close()

    def double(self, x):
        res = x * 2
        if res > 9:
            res = res - 9
        return res

    def luhn_algorithm(self, card):  # Проверка алгоритмом луна
        odd = map(lambda x: self.double(int(x)), card[::2])
        even = map(int, card[1::2])
        return (sum(odd) + sum(even)) % 10 == 0

    def true_card(self):  # Проверка правильности ввода номера карты
        number = self.get_card_number()
        if number == "":
            self.label_error.setText('Введите номер карты')
            return False
        try:
            if not self.luhn_algorithm(number):
                self.label_error.setText('Неверно указан номер карты.')
                return False
            else:
                self.label_error.clear()
                return True
        except Exception:
            self.label_error.setText('Неверно указан номер карты.')

    def true_cvv(self):  # Проверка правильности ввода cvv
        cvv = self.line_cvv.text()
        if cvv.isdigit() and len(cvv) == 3:
            return True
        else:
            self.label_error.setText('CVV - это три цифры на обороте карты')
            return False

    def true_date(self):  # Проверка правильности ввода даты
        if self.true_month() and self.true_year():
            return True
        return False

    def true_month(self):  # Проверка правильности ввода месяца
        try:
            month = int(self.line_month.text())
            if month in range(1, 13):
                self.label_error.clear()
                return True
        except Exception:
            self.label_error.setText('Неверно указан месяц')
            return False

    def true_year(self):  # Проверка правильности ввода года
        try:
            year = int(self.line_year.text())
            if year > 100 or (2000 + year < dt.datetime.now().date().year):
                self.label_error.setText('Неверно указан год')
                return False
            self.label_error.clear()
            return True
        except Exception:
            self.label_error.setText('Неверно указан год')
            return False

    def add_card_data(self):  # Добавление информации карты в бд
        con = sqlite3.connect("TAXI.db")
        cur = con.cursor()
        line_month = str(int(self.line_month.text()))
        self.user_id = cur.execute("SELECT user_id FROM Receipt WHERE id = ?", (self.id_receipt,)).fetchone()
        user_2_id = cur.execute("""SELECT id FROM Cards_info WHERE numbers = ? AND cvv = ? AND
        month = ? AND year = ? AND user_id = ?""", (self.line_card.text(), self.line_cvv.text(),
                                    line_month, self.line_year.text(), self.user_id[0])).fetchone()
        if user_2_id:
            pass
        else:
            cur.execute("""INSERT INTO Cards_info(numbers, cvv, month, year, user_id) Values(?, ?, ?, ?, ?)""",
                        (self.line_card.text(), self.line_cvv.text(), self.line_month.text(),
                         self.line_year.text(), self.user_id[0])).fetchone()
            con.commit()
            con.close()

    def open_receipt_form(self):  # Закрывает текущее окно и открывает новое
        self.close()
        self.receipt_form = Receipt(self.id_receipt)
        self.receipt_form.show()


class Receipt(QWidget):  # Этот класс отвечает за окно чека заказа
    def __init__(self, id_receipt):
        super().__init__()
        uic.loadUi(r'info.ui', self)
        self.id_receipt = id_receipt
        self.button()
        self.run()

    def run(self):  # Запускает функции обавления информации о заказе
        self.add_hard_info()
        self.add_normal_info()

    def add_hard_info(self):  # Добавляет информацию
        con = sqlite3.connect('TAXI.db')
        cur = con.cursor()
        result = cur.execute(
            """SELECT d.name, cc.name, ca.name, sta.name, ha.name, cb.name, stb.name, hb.name
                FROM Receipt r
                JOIN Driver d ON d.id = r.driver_id
                JOIN class_car cc ON cc.id = d.class_car_id
                JOIN House ha ON ha.id = r.house_a_id
                JOIN Street sta ON sta.id = ha.street_id
                JOIN City ca ON ca.id = sta.city_id
                JOIN House hb ON hb.id = r.house_b_id
                JOIN Street stb ON stb.id = hb.street_id
                JOIN City cb ON cb.id = stb.city_id
                WHERE r.id = ?""", (self.id_receipt,)).fetchone()

        driver = result[0]
        self.line_driver.setText(driver)
        class_car = result[1]
        self.line_car.setText(class_car)

        address_a = ', '.join(result[2:5])
        self.line_from.setText(address_a)

        address_b = ', '.join(result[5:])
        self.line_to.setText(address_b)

    def add_normal_info(self):  # Добавляет информацию
        con = sqlite3.connect('TAXI.db')
        cur = con.cursor()
        result = cur.execute(
            """SELECT date_of_need_for_user, cost FROM Receipt WHERE id = ?""",
            (self.id_receipt,)).fetchone()

        cost = math.ceil(result[1])
        self.line_cost.setText(str(cost))
        date = result[0]
        self.line_when.setText(date)

    def button(self):  # Привязываем функционал кнопок
        self.btn.clicked.connect(self.exit)

    def exit(self):  # Выход
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Entrance()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
