import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGroupBox, QHBoxLayout, QFormLayout, QDialog, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


import qdarkstyle
import re

from users_edit_window import UserManagementWindow
from sales_manager_window import SalesManagementWindow
from sales_analysis import SalesAnalysisWindow
from report_window import ReportAnalysisWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно входа")
        self.setGeometry(0, 0, 600, 400)  # Increase initial size
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        # Initialize the database connection
        self.init_db()

        self.init_ui()

        self.register_window = RegisterWindow()

        # Center the window after all widgets are added
        self.center_on_screen()

    def show_register_window(self):
        self.hide()  # Hide the login window
        self.register_window.show()

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
        self.label_username = QLabel("Логин:")
        self.label_password = QLabel("Пароль:")
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.warning_label = QLabel()
        self.login_button = QPushButton("Вход")
        self.register_button = QPushButton("Регистрация")

        

        # Increase font size for labels and buttons
        font = QFont()
        font.setPointSize(16)  # Set font size to 16

        self.label_username.setFont(font)
        self.label_password.setFont(font)
        self.login_button.setFont(font)
        self.register_button.setFont(font)

        self.input_username.setFont(font)
        self.input_password.setFont(font)

        # Increase size of input fields
        self.input_username.setMinimumWidth(300)
        self.input_password.setMinimumWidth(300)

        # Increase size of the warning label
        self.warning_label.setFixedHeight(40)

        self.input_password.setEchoMode(QLineEdit.Password)

        group_box = QGroupBox("Аутентификация пользователя")
        group_layout = QVBoxLayout()

        group_layout.addWidget(self.label_username)
        group_layout.addWidget(self.input_username)
        group_layout.addWidget(self.label_password)
        group_layout.addWidget(self.input_password)
        group_layout.addWidget(self.warning_label)

        group_layout.addWidget(self.login_button)
        group_layout.addWidget(self.register_button)

        group_box.setLayout(group_layout)

        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addWidget(group_box, 2, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

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
            self.warning_label.setStyleSheet("color: red;")

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
        self.setGeometry(0, 0, 600, 400)  # Set initial size, will be adjusted later
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        # Create input widgets
        self.username_input = QLineEdit(self)
        self.full_name = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.pin_input = QLineEdit(self)

        # Set up the layout
        self.init_ui()
        self.init_db()

        # Center the window after all widgets are added
        self.center_on_screen()

    def init_db(self):
        # Connect to SQLite database (create a new one if it doesn't exist)
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()

        # Create a table to store user credentials if it doesn't exist
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
        # Set up the layout for the register window
        form_layout = QFormLayout()
        form_layout.addRow("Полное имя:", self.full_name)
        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("ПИН-код:", self.pin_input)

        # Create register button
        register_button = QPushButton("Регистрация", self)
        register_button.clicked.connect(self.register_user)

        # Create back button
        back_button = QPushButton("Назад", self)
        back_button.clicked.connect(self.back_to_login)

        # Apply same font style
        font = QFont()
        font.setPointSize(16)  # Set font size to 16
        register_button.setFont(font)
        back_button.setFont(font)
        self.full_name.setFont(font)
        self.username_input.setFont(font)
        self.password_input.setFont(font)
        self.pin_input.setFont(font)

        # Add widgets to the layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(register_button)
        main_layout.addWidget(back_button)

        # Add QLabel for warning message
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.warning_label)

        # Create a group box and add the main layout to it
        group_box = QGroupBox("Регистрация нового пользователя")
        group_box.setLayout(main_layout)

        # Create a main layout for the dialog and add the group box to it
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(group_box)

        # Set the layout for the dialog
        self.setLayout(dialog_layout)

    def check_password_strength(self, password):
        # Check if password contains at least one uppercase letter and one digit
        return len(password) >= 8 and re.search(r'[A-Z]', password) and re.search(r'\d', password)

    def register_user(self):
        full_name = self.full_name.text()
        username = self.username_input.text()
        password = self.password_input.text()
        pin = self.pin_input.text()

        # Проверяем, существует ли уже такой логин
        query = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        existing_user = self.cursor.fetchone()

        

        if pin != '1234':
            QMessageBox.warning(self, "Неверный ПИН-код", "Пожалуйста, введите правильный ПИН-код.", QMessageBox.Ok)
            return
        
        if existing_user:
            self.warning_label.setText("Такой логин уже существует. Пожалуйста, выберите другой.")
            return
        
        # Check if full name length is between 1 and 70 characters
        if not (1 <= len(full_name) <= 70):
            self.warning_label.setText("Ошибка, проверьть ФИО пользователя")
            return
        
        # Проверяем, содержит ли логин только английские буквы и спецсимволы
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.warning_label.setText("Логин может содержать только английские буквы и спецсимволы.")
            return

        # Check if password meets strength requirements
        if not self.check_password_strength(password):
            self.warning_label.setText("Слишком слабый пароль (минимум 8 символов и 1 заглаваная буква, язык - анг-й).")
            return

        permissions = 'Average'

        # Insert new user data into the database
        query = "INSERT INTO users (full_name, username, password, permissions) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (full_name, username, password, permissions))
        self.conn.commit()

        # Show success message
        QMessageBox.information(self, "Успешная регистрация", "Вы успешно зарегистрированы.", QMessageBox.Ok)

        # Hide the dialog after registration
        self.hide()

        # Show the login window
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
        self.setGeometry(0, 0, 800, 600)  # Set initial size, will be adjusted later

        self.username = username
        self.login_window = login_window

        self.init_ui()
        self.init_db()

        # Center the window after all widgets are added
        self.center_on_screen()

    def init_db(self):
        # Connect to SQLite database (create a new one if it doesn't exist)
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()

        # Create a table to store user credentials if it doesn't exist
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
        # Widgets
        welcome_label = QLabel(f"Добро пожаловать, {self.username}!")

        exit_button = QPushButton("Выход")
        main_menu_button = QPushButton("Управление продажами")
        manager_button = QPushButton("Управление персоналом")
        analysis_button = QPushButton("Анализ продаж")
        report_button = QPushButton("Отчет")
        patterns_button = QPushButton("Паттерн")
        logout_button = QPushButton("Выйти из аккаунта")

        # Increase font size for labels and buttons
        font = QFont()
        font.setPointSize(16)  # Set font size to 16

        welcome_label.setFont(font)
        exit_button.setFont(font)
        main_menu_button.setFont(font)
        manager_button.setFont(font)
        analysis_button.setFont(font)
        report_button.setFont(font)
        patterns_button.setFont(font)
        logout_button.setFont(font)

        # Layouts
        main_layout = QVBoxLayout()

        # Top Section
        top_layout = QHBoxLayout()
        top_layout.addWidget(exit_button, 10)
        top_layout.addWidget(welcome_label, 90)

        top_groupbox = QGroupBox("SYS-SELL")
        top_groupbox.setLayout(top_layout)
        main_layout.addWidget(top_groupbox, 10)


        # Middle Section
        middle_layout = QHBoxLayout()

        left_groupbox = QGroupBox("Инструкция и правила")
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Правила использования:"))
        left_layout.addWidget(QLabel("1. Не передавайте свои учетные \nданные другим лицам."))
        left_layout.addWidget(QLabel("2. Используйте приложение только в \nрамках предназначенных целей."))
        left_layout.addWidget(QLabel("3. При возникновении проблем или \nвопросов обращайтесь к администратору."))
        left_groupbox.setLayout(left_layout)

        center_groupbox = QGroupBox("Главное меню")
        center_layout = QVBoxLayout()
        center_layout.addWidget(main_menu_button)
        center_layout.addWidget(manager_button)
        center_layout.addWidget(analysis_button)
        center_layout.addWidget(report_button)
        center_groupbox.setLayout(center_layout)

        right_groupbox = QGroupBox("Мини-справочник")
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Добро пожаловать!"))
        right_layout.addWidget(QLabel("Выйдите из аккаунта, нажав кнопку \n'Выход'."))
        right_layout.addWidget(QLabel("Навигируйтесь по разделам, \nиспользуя кнопки в центре."))
        right_layout.addWidget(QLabel("Если вы забыли пароль, \nобратитесь к администратору."))
        right_groupbox.setLayout(right_layout)

        middle_layout.addWidget(left_groupbox, 35)
        middle_layout.addWidget(center_groupbox, 30)
        middle_layout.addWidget(right_groupbox, 35)

        # Set overall layout
        main_layout.addLayout(middle_layout, 80)

        # Bottom Section
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(logout_button, 10)

        bottom_groupbox = QGroupBox("Желаете сменить аккаунт?")
        bottom_groupbox.setLayout(bottom_layout)
        main_layout.addWidget(bottom_groupbox, 10)

        # Signals and slots
        exit_button.clicked.connect(self.exit_program)
        main_menu_button.clicked.connect(self.go_to_main_menu)
        manager_button.clicked.connect(self.go_to_management)
        analysis_button.clicked.connect(self.go_to_analysis)
        report_button.clicked.connect(self.go_to_report)
        # patterns_button.clicked.connect(self.go_to_patterns)
        logout_button.clicked.connect(self.logout)

        self.setLayout(main_layout)

    def exit_program(self):
        sys.exit(app.exec_())

    def go_to_main_menu(self):
        permissions = self.get_permissions()

        if permissions == "Full" or permissions == "Limited" or permissions == "Average" or permissions == "Полный доступ" or permissions == "Средний доступ":
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

    # def go_to_patterns(self):
    #     self.info_page = SalesAnalysisWindow(self, self.username)
    #     self.info_page.show()
    #     self.hide()

    def go_to_management(self):
        permissions = self.get_permissions()

        if permissions == "Full" or permissions == "Полный доступ":
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
    login_window = LoginWindow()
    login_window.show()

    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    sys.exit(app.exec_())
