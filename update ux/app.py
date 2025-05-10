import sys
import sqlite3
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QGroupBox, QHBoxLayout, QFormLayout, QDialog, QMessageBox, QDesktopWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import qdarkstyle

# Импорт окон, если они реализованы в отдельных файлах
from users_edit_window import UserManagementWindow
from sales_manager_window import SalesManagementWindow
from sales_analysis import SalesAnalysisWindow
from report_window import ReportAnalysisWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно входа")
        self.setGeometry(0, 0, 600, 400)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.init_db()
        self.init_ui()

        self.register_window = RegisterWindow()

        self.center_on_screen()

    def init_db(self):
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                permissions TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        # Шрифты
        font = QFont()
        font.setPointSize(16)

        # Виджеты
        self.label_username = QLabel("Логин:")
        self.label_username.setFont(font)
        self.input_username = QLineEdit()
        self.input_username.setFont(font)
        self.input_username.setMinimumWidth(300)
        self.input_username.setPlaceholderText("Введите логин")

        self.label_password = QLabel("Пароль:")
        self.label_password.setFont(font)
        self.input_password = QLineEdit()
        self.input_password.setFont(font)
        self.input_password.setMinimumWidth(300)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Введите пароль")

        self.warning_label = QLabel()
        self.warning_label.setFixedHeight(40)
        self.warning_label.setStyleSheet("color: red;")
        
        self.login_button = QPushButton("Вход")
        self.login_button.setFont(font)
        self.register_button = QPushButton("Регистрация")
        self.register_button.setFont(font)

        # Группа для аутентификации
        group_box = QGroupBox("Аутентификация пользователя")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)
        group_layout.addWidget(self.label_username)
        group_layout.addWidget(self.input_username)
        group_layout.addWidget(self.label_password)
        group_layout.addWidget(self.input_password)
        group_layout.addWidget(self.warning_label)
        group_layout.addWidget(self.login_button)
        group_layout.addWidget(self.register_button)
        group_box.setLayout(group_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addStretch(1)
        main_layout.addWidget(group_box, 0, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

        # Сигналы
        self.login_button.clicked.connect(self.authenticate)
        self.register_button.clicked.connect(self.show_register_window)

    def authenticate(self):
        username = self.input_username.text()
        password = self.input_password.text()

        query = "SELECT * FROM users WHERE username=? AND password=?"
        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()

        if user:
            self.warning_label.clear()
            self.info_page = InfoPage(self, username)
            self.info_page.show()
            self.hide()
        else:
            self.warning_label.setText("Неправильный логин пользователя или пароль.")

    def show_register_window(self):
        self.hide()
        self.register_window.show()

    def center_on_screen(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        center_point = screen_geometry.center()
        new_x = center_point.x() - self.width() // 2
        new_y = center_point.y() - self.height() // 2
        self.move(new_x, new_y)


class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно регистрации")
        self.setGeometry(0, 0, 600, 400)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.init_db()
        self.init_ui()
        self.center_on_screen()

    def init_db(self):
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                permissions TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        font = QFont()
        font.setPointSize(16)

        # Поля ввода с placeholder'ами
        self.full_name = QLineEdit()
        self.full_name.setFont(font)
        self.full_name.setPlaceholderText("Введите ФИО")

        self.username_input = QLineEdit()
        self.username_input.setFont(font)
        self.username_input.setPlaceholderText("Введите логин (англ.)")

        self.password_input = QLineEdit()
        self.password_input.setFont(font)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Введите пароль")

        self.pin_input = QLineEdit()
        self.pin_input.setFont(font)
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setPlaceholderText("Введите ПИН-код")

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.addRow("Полное имя:", self.full_name)
        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("ПИН-код:", self.pin_input)

        register_button = QPushButton("Регистрация", self)
        register_button.setFont(font)
        register_button.clicked.connect(self.register_user)

        back_button = QPushButton("Назад", self)
        back_button.setFont(font)
        back_button.clicked.connect(self.back_to_login)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red;")
        self.warning_label.setFont(font)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(register_button)
        main_layout.addWidget(back_button)
        main_layout.addWidget(self.warning_label)

        group_box = QGroupBox("Регистрация нового пользователя")
        group_box.setLayout(main_layout)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(group_box)
        self.setLayout(dialog_layout)

    def check_password_strength(self, password):
        return len(password) >= 8 and re.search(r'[A-Z]', password) and re.search(r'\d', password)

    def register_user(self):
        full_name = self.full_name.text()
        username = self.username_input.text()
        password = self.password_input.text()
        pin = self.pin_input.text()

        query = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        existing_user = self.cursor.fetchone()

        if pin != '1234':
            QMessageBox.warning(self, "Неверный ПИН-код", "Пожалуйста, введите правильный ПИН-код.", QMessageBox.Ok)
            return

        if existing_user:
            self.warning_label.setText("Такой логин уже существует. Пожалуйста, выберите другой.")
            return

        if not (1 <= len(full_name) <= 70):
            self.warning_label.setText("Ошибка, проверьте ФИО пользователя.")
            return

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.warning_label.setText("Логин может содержать только английские буквы и спецсимволы.")
            return

        if not self.check_password_strength(password):
            self.warning_label.setText("Слишком слабый пароль (минимум 8 символов, 1 заглавная буква, англ.).")
            return

        permissions = 'Average'
        query = "INSERT INTO users (full_name, username, password, permissions) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (full_name, username, password, permissions))
        self.conn.commit()

        QMessageBox.information(self, "Успешная регистрация", "Вы успешно зарегистрированы.", QMessageBox.Ok)
        self.hide()
        self.login_window = LoginWindow()
        self.login_window.show()

    def back_to_login(self):
        self.hide()
        self.login_window = LoginWindow()
        self.login_window.show()

    def center_on_screen(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        center_point = screen_geometry.center()
        new_x = center_point.x() - self.width() // 2
        new_y = center_point.y() - self.height() // 2
        self.move(new_x, new_y)


class InfoPage(QWidget):
    def __init__(self, login_window, username):
        super().__init__()

        self.setWindowTitle("Страница информации")
        self.setGeometry(0, 0, 800, 600)
        self.username = username
        self.login_window = login_window

        self.init_db()
        self.init_ui()
        self.center_on_screen()

    def init_db(self):
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                permissions TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        font = QFont()
        font.setPointSize(16)

        welcome_label = QLabel(f"Добро пожаловать, {self.username}!")
        welcome_label.setFont(font)

        exit_button = QPushButton("Выход")
        exit_button.setFont(font)
        main_menu_button = QPushButton("Управление продажами")
        main_menu_button.setFont(font)
        manager_button = QPushButton("Управление персоналом")
        manager_button.setFont(font)
        analysis_button = QPushButton("Анализ продаж")
        analysis_button.setFont(font)
        report_button = QPushButton("Отчет")
        report_button.setFont(font)
        logout_button = QPushButton("Выйти из аккаунта")
        logout_button.setFont(font)

        # Верхняя панель
        top_layout = QHBoxLayout()
        top_layout.addWidget(exit_button, 10)
        top_layout.addWidget(welcome_label, 90)
        top_groupbox = QGroupBox("SYS-SELL")
        top_groupbox.setLayout(top_layout)

        # Средняя панель
        left_groupbox = QGroupBox("Инструкция и правила")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.addWidget(QLabel("Правила использования:"))
        left_layout.addWidget(QLabel("1. Не передавайте свои учетные\nданные другим лицам."))
        left_layout.addWidget(QLabel("2. Используйте приложение только\nв рамках предназначенных целей."))
        left_layout.addWidget(QLabel("3. При возникновении проблем\nобращайтесь к администратору."))
        left_groupbox.setLayout(left_layout)

        center_groupbox = QGroupBox("Главное меню")
        center_layout = QVBoxLayout()
        center_layout.setSpacing(15)
        center_layout.addWidget(main_menu_button)
        center_layout.addWidget(manager_button)
        center_layout.addWidget(analysis_button)
        center_layout.addWidget(report_button)
        center_groupbox.setLayout(center_layout)

        right_groupbox = QGroupBox("Мини-справочник")
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(QLabel("Добро пожаловать!"))
        right_layout.addWidget(QLabel("Для выхода нажмите\n'Выход'."))
        right_layout.addWidget(QLabel("Навигируйтесь по разделам\nс помощью кнопок в центре."))
        right_layout.addWidget(QLabel("Если забыли пароль,\nобратитесь к администратору."))
        right_groupbox.setLayout(right_layout)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(left_groupbox, 35)
        middle_layout.addWidget(center_groupbox, 30)
        middle_layout.addWidget(right_groupbox, 35)

        # Нижняя панель
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(logout_button, 10)
        bottom_groupbox = QGroupBox("Сменить аккаунт?")
        bottom_groupbox.setLayout(bottom_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addWidget(top_groupbox, 10)
        main_layout.addLayout(middle_layout, 80)
        main_layout.addWidget(bottom_groupbox, 10)

        self.setLayout(main_layout)

        # Сигналы
        exit_button.clicked.connect(self.exit_program)
        main_menu_button.clicked.connect(self.go_to_main_menu)
        manager_button.clicked.connect(self.go_to_management)
        analysis_button.clicked.connect(self.go_to_analysis)
        report_button.clicked.connect(self.go_to_report)
        logout_button.clicked.connect(self.logout)

    def exit_program(self):
        sys.exit(app.exec_())

    def go_to_main_menu(self):
        permissions = self.get_permissions()
        if permissions in ["Full", "Limited", "Average", "Полный доступ", "Средний доступ"]:
            self.info_page = SalesManagementWindow(self, self.login_window, self.username)
            self.info_page.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Отказано в доступе", "У вас недостаточно прав, обратитесь к администратору.", QMessageBox.Ok)

    def go_to_analysis(self):
        self.info_page = SalesAnalysisWindow(self, self.login_window, self.username)
        self.info_page.show()
        self.hide()

    def go_to_report(self):
        self.info_page = ReportAnalysisWindow(self, self.login_window, self.username)
        self.info_page.show()
        self.hide()

    def go_to_management(self):
        permissions = self.get_permissions()
        if permissions in ["Full", "Полный доступ"]:
            self.info_page = UserManagementWindow(self, self.login_window, self.username)
            self.info_page.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Отказано в доступе", "У вас недостаточно прав, обратитесь к администратору.", QMessageBox.Ok)

    def logout(self):
        self.login_page = LoginWindow()
        self.login_page.show()
        self.hide()

    def get_permissions(self):
        query = "SELECT permissions FROM users WHERE username = ?"
        self.cursor.execute(query, (self.username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def center_on_screen(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        center_point = screen_geometry.center()
        new_x = center_point.x() - self.width() // 2
        new_y = center_point.y() - self.height() // 2
        self.move(new_x, new_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Загрузка базового стиля qdarkstyle и добавление пользовательских стилей
    custom_styles = """
        QWidget {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            border-radius: 8px;
        }
        QLineEdit {
            border: 2px solid #3c3f41;
            border-radius: 8px;
            padding: 6px;
            background-color: #2b2b2b;
        }
        QPushButton {
            border: none;
            background-color: #3c3f41;
            padding: 10px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #4c5052;
        }
        QPushButton:pressed {
            background-color: #5c6062;
        }
        QGroupBox {
            border: 1px solid #3c3f41;
            border-radius: 8px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
    """
    base_style = qdarkstyle.load_stylesheet_from_environment()
    app.setStyleSheet(base_style + custom_styles)

    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
