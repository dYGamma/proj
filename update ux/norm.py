import sys
import sqlite3
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGroupBox,
    QHBoxLayout, QFormLayout, QDialog, QMessageBox, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont, QPixmap
import qdarkstyle
import qtawesome

from users_edit_window import UserManagementWindow
from sales_manager_window import SalesManagementWindow
from sales_analysis import SalesAnalysisWindow
from report_window import ReportAnalysisWindow
from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication

# Глобальная переменная для хранения текущей темы
current_theme = 'dark'



def toggle_theme():
    global current_theme
    app = QApplication.instance()
    if current_theme == 'dark':
        # Применяем светлую тему (цветовую палитру light_cyan_500)
        apply_stylesheet(app, theme='light_cyan_500.xml')
        current_theme = 'light'
    else:
        # Применяем тёмную тему (например, dark_teal)
        apply_stylesheet(app, theme='dark_teal.xml')
        current_theme = 'dark'

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно входа")
        self.setGeometry(0, 0, 600, 500)
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
        # Логотип
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)

        # Элементы формы
        self.label_username = QLabel("Логин:")
        self.label_password = QLabel("Пароль:")
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.warning_label = QLabel()
        self.login_button = QPushButton("Вход")
        self.register_button = QPushButton("Регистрация")
        # Кнопка переключения темы
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setToolTip("Переключить тему")
        self.theme_toggle_button.setIcon(qtawesome.icon('fa5s.adjust', color='white'))
        self.theme_toggle_button.setFixedSize(40, 40)

        # Задаём шрифт
        font = QFont("Segoe UI", 16)
        self.label_username.setFont(font)
        self.label_password.setFont(font)
        self.input_username.setFont(font)
        self.input_password.setFont(font)
        self.login_button.setFont(font)
        self.register_button.setFont(font)
        self.warning_label.setFont(font)

        # Настройки полей ввода
        self.input_username.setMinimumWidth(300)
        self.input_password.setMinimumWidth(300)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.warning_label.setFixedHeight(40)

        # Установка иконок FontAwesome
        self.login_button.setIcon(qtawesome.icon('fa5s.sign-in-alt', color='white'))
        self.register_button.setIcon(qtawesome.icon('fa5s.user-plus', color='white'))

        # Подключаем переключатель темы
        self.theme_toggle_button.clicked.connect(toggle_theme)

        # Группа для формы
        form_group = QGroupBox("Аутентификация пользователя")
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.label_username)
        form_layout.addWidget(self.input_username)
        form_layout.addWidget(self.label_password)
        form_layout.addWidget(self.input_password)
        form_layout.addWidget(self.warning_label)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.register_button)
        form_group.setLayout(form_layout)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(self.theme_toggle_button, alignment=Qt.AlignRight)
        main_layout.addStretch(1)
        main_layout.addWidget(form_group, alignment=Qt.AlignCenter)
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

    def fade_in(self):
        """Анимация плавного появления окна."""
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def showEvent(self, event):
        self.fade_in()
        super().showEvent(event)

    def show_register_window(self):
        self.hide()
        self.register_window.show()

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно регистрации")
        self.setGeometry(0, 0, 600, 400)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.username_input = QLineEdit(self)
        self.full_name = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.pin_input = QLineEdit(self)
        self.init_ui()
        self.init_db()
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
        form_layout = QFormLayout()
        form_layout.addRow("Полное имя:", self.full_name)
        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("ПИН-код:", self.pin_input)

        register_button = QPushButton("Регистрация", self)
        register_button.setIcon(qtawesome.icon('fa5s.check', color='white'))
        register_button.clicked.connect(self.register_user)

        back_button = QPushButton("Назад", self)
        back_button.setIcon(qtawesome.icon('fa5s.arrow-left', color='white'))
        back_button.clicked.connect(self.back_to_login)

        # Задаём шрифт
        font = QFont("Segoe UI", 16)
        register_button.setFont(font)
        back_button.setFont(font)
        self.full_name.setFont(font)
        self.username_input.setFont(font)
        self.password_input.setFont(font)
        self.pin_input.setFont(font)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red;")
        self.warning_label.setFont(font)

        # Реализуем валидацию полей в реальном времени
        self.username_input.textChanged.connect(self.validate_username)
        self.password_input.textChanged.connect(self.validate_password)
        self.full_name.textChanged.connect(self.validate_fullname)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(register_button)
        main_layout.addWidget(back_button)
        main_layout.addWidget(self.warning_label)

        group_box = QGroupBox("Регистрация нового пользователя")
        group_box.setLayout(main_layout)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(group_box)
        self.setLayout(dialog_layout)

    def validate_username(self):
        text = self.username_input.text()
        if re.match(r'^[a-zA-Z0-9_]+$', text):
            self.username_input.setStyleSheet("border: 2px solid green;")
        else:
            self.username_input.setStyleSheet("border: 2px solid red;")

    def validate_password(self):
        password = self.password_input.text()
        if self.check_password_strength(password):
            self.password_input.setStyleSheet("border: 2px solid green;")
        else:
            self.password_input.setStyleSheet("border: 2px solid red;")

    def validate_fullname(self):
        name = self.full_name.text()
        if 1 <= len(name) <= 70:
            self.full_name.setStyleSheet("border: 2px solid green;")
        else:
            self.full_name.setStyleSheet("border: 2px solid red;")

    def check_password_strength(self, password):
        # Минимум 8 символов, хотя бы 1 заглавная буква и 1 цифра
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
            self.warning_label.setText("Ошибка, проверьте ФИО пользователя")
            return
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.warning_label.setText("Логин может содержать только английские буквы и спецсимволы.")
            return

        if not self.check_password_strength(password):
            self.warning_label.setText("Слишком слабый пароль (минимум 8 символов, 1 заглавная буква, цифра).")
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

    def fade_in(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def showEvent(self, event):
        self.fade_in()
        super().showEvent(event)

class InfoPage(QWidget):
    def __init__(self, login_window, username):
        super().__init__()
        self.setWindowTitle("Страница информации")
        self.setGeometry(0, 0, 800, 600)
        self.username = username
        self.login_window = login_window
        self.init_ui()
        self.init_db()
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
        welcome_label = QLabel(f"Добро пожаловать, {self.username}!")
        welcome_label.setFont(QFont("Segoe UI", 16))
        
        exit_button = QPushButton("Выход")
        exit_button.setIcon(qtawesome.icon('fa5s.power-off', color='white'))
        main_menu_button = QPushButton("Управление продажами")
        main_menu_button.setIcon(qtawesome.icon('fa5s.shopping-cart', color='white'))
        manager_button = QPushButton("Управление персоналом")
        manager_button.setIcon(qtawesome.icon('fa5s.users', color='white'))
        analysis_button = QPushButton("Анализ продаж")
        analysis_button.setIcon(qtawesome.icon('fa5s.chart-bar', color='white'))
        report_button = QPushButton("Отчет")
        report_button.setIcon(qtawesome.icon('fa5s.file-alt', color='white'))
        logout_button = QPushButton("Выйти из аккаунта")
        logout_button.setIcon(qtawesome.icon('fa5s.sign-out-alt', color='white'))
        theme_toggle_button = QPushButton()
        theme_toggle_button.setToolTip("Переключить тему")
        theme_toggle_button.setIcon(qtawesome.icon('fa5s.adjust', color='white'))
        theme_toggle_button.setFixedSize(40, 40)
        theme_toggle_button.clicked.connect(toggle_theme)

        font = QFont("Segoe UI", 16)
        welcome_label.setFont(font)
        exit_button.setFont(font)
        main_menu_button.setFont(font)
        manager_button.setFont(font)
        analysis_button.setFont(font)
        report_button.setFont(font)
        logout_button.setFont(font)

        main_layout = QVBoxLayout()

        # Верхняя секция с логотипом, приветствием и переключателем темы
        top_layout = QHBoxLayout()
        top_layout.addWidget(exit_button, 10)
        top_layout.addWidget(welcome_label, 70)
        top_layout.addWidget(theme_toggle_button, 10)
        top_groupbox = QGroupBox("SYS-SELL")
        top_groupbox.setLayout(top_layout)
        main_layout.addWidget(top_groupbox, 10)

        # Средняя секция – три колонки
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
        main_layout.addLayout(middle_layout, 80)

        # Нижняя секция
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(logout_button, 10)
        bottom_groupbox = QGroupBox("Желаете сменить аккаунт?")
        bottom_groupbox.setLayout(bottom_layout)
        main_layout.addWidget(bottom_groupbox, 10)

        exit_button.clicked.connect(self.exit_program)
        main_menu_button.clicked.connect(self.go_to_main_menu)
        manager_button.clicked.connect(self.go_to_management)
        analysis_button.clicked.connect(self.go_to_analysis)
        report_button.clicked.connect(self.go_to_report)
        logout_button.clicked.connect(self.logout)

        self.setLayout(main_layout)

    def exit_program(self):
        sys.exit(QApplication.instance().exec_())

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

    def fade_in(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def showEvent(self, event):
        self.fade_in()
        super().showEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Применяем начальную тему – тёмную (по умолчанию)
    from qt_material import apply_stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
