import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QFormLayout, QComboBox, QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import sqlite3
import csv
import pandas as pd


class UserManagementWindow(QWidget):
    def import_users(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Users", "", "Excel Files (*.xls *.xlsx)", options=options)  # Update file filter
        if file_name:
            try:
                users_df = pd.read_excel(file_name)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при импорте пользователей: {str(e)}")
                return
            
            if users_df.empty:
                QMessageBox.warning(self, "Внимание", "Файл с пользователями пуст.")
                return

            users_data = users_df.values.tolist()
            for user_data in users_data:
                if len(user_data) == 4:
                    full_name, username, password, permissions = user_data
                    self.cursor.execute("INSERT INTO users (full_name, username, password, permissions) VALUES (?, ?, ?, ?)",
                                        (full_name, username, password, permissions))
            self.conn.commit()
            self.load_user_data()
    def export_users(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Users", "", "Excel Files (*.xlsx)", options=options)  # Update file filter
        if file_name:
            query = "SELECT full_name, username, password, permissions FROM users"
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            users_df = pd.DataFrame(users, columns=["Full Name", "Username", "Password", "Permissions"])
            users_df.to_excel(file_name, index=False)  # Export to xlsx format


    def __init__(self, previous_window, login_window, username):
        super().__init__()

        self.setWindowTitle("Управление пользователями")
        self.showFullScreen()
        
        self.previous_window = previous_window
        self.login_window = login_window
        self.username = username
        self.init_db()
        self.init_ui()

    def setFullScreen(self):
        desktop = QApplication.desktop()
        screen_geometry = desktop.screenGeometry()
        self.setGeometry(screen_geometry)

    def init_db(self):
        # Connect to SQLite database (create a new one if it doesn't exist)
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()

        # Create a table to store user information if it doesn't exist
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
        user_table_label = QLabel("База данных пользователей:")
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["ID", "Full Name", "Username", "Password", "Permissions"])

        # back_button = QPushButton("Back")
        # logout_button = QPushButton("Logout")
        # clear_db_button = QPushButton("Clear Database")

        add_user_label = QLabel("Добавить нового пользователя:")
        self.full_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.permissions_combo = QComboBox()
        # self.permissions_combo.setGeometry(10, 10, 200, 30)
        self.permissions_combo.addItems(["Полный доступ", "Средний доступ", "Ограниченный доступ"])

        add_button = QPushButton("Добавить пользователя")
        import_button = QPushButton("Импортировать пользователей")
        export_button = QPushButton("Экспортировать пользователей")
        search_label = QLabel("Поиск пользователя по ID:")
        self.search_id_input = QLineEdit()
        search_button = QPushButton("Найти")
        delete_button = QPushButton("Удалить пользователя")

        edit_label = QLabel("Редактировать пользователя:")
        self.edit_id_input = QLineEdit()
        self.edit_full_name_input = QLineEdit()
        self.edit_username_input = QLineEdit()
        self.edit_password_input = QLineEdit()
        self.edit_permissions_combo = QComboBox()
        self.edit_permissions_combo.addItems(["Полный доступ", "Средний доступ", "Ограниченный доступ"])
        save_edit_button = QPushButton("Сохранить изменения")


        # Left Half: User Table Section
        user_table_layout = QVBoxLayout()
        user_table_layout.addWidget(user_table_label)
        user_table_layout.addWidget(self.user_table)
        # user_table_layout.addWidget(back_button)
        # user_table_layout.addWidget(logout_button)
        # user_table_layout.addWidget(clear_db_button)

        # Right Half: Divided Vertically
        right_half_layout = QVBoxLayout()

        # GroupBox 1: User Info
        user_info_groupbox = QGroupBox("Информация о пользователях")
        user_info_layout = QVBoxLayout()
        user_info_label = QLabel(
            "Этот раздел предоставляет возможность просматривать, добавлять, редактировать и удалять информацию о пользователях в системе.\n\n"
            "Для просмотра данных пользователей, таблица отображает полные имена, имена пользователя, пароли и разрешения доступа к системе.\n\n"
            "Для добавления нового пользователя, заполните поля 'Полное имя', 'Имя пользователя', 'Пароль' и выберите разрешения доступа из выпадающего списка, "
            "затем нажмите кнопку 'Добавить пользователя'.\n\n"
            "Для редактирования существующих пользователей, введите их ID, затем внесите необходимые изменения в соответствующие поля и нажмите кнопку 'Сохранить изменения'.\n\n"
            "Для удаления одного или нескольких пользователей, введите их ID через запятую, затем нажмите кнопку 'Удалить пользователя'.\n\n"
            "Кроме того, вы можете импортировать и экспортировать данные о пользователях в формате Excel, используя кнопки 'Импортировать пользователей' и 'Экспортировать пользователей' соответственно."
        )
        user_info_layout.addWidget(user_info_label)
        user_info_layout.addWidget(user_table_label)
        user_info_layout.addWidget(self.user_table)
        # user_info_layout.addWidget(back_button)
        # user_info_layout.addWidget(logout_button)
        # user_info_layout.addWidget(clear_db_button)
        
        user_info_groupbox.setLayout(user_info_layout)

        # GroupBox 2: Adding Users
        add_users_groupbox = QGroupBox("Добавление пользователей")
        add_users_layout = QFormLayout()
        add_users_layout.addRow(add_user_label)
        add_users_layout.addRow("Полное имя:", self.full_name_input)
        add_users_layout.addRow("Имя пользователя:", self.username_input)
        add_users_layout.addRow("Пароль:", self.password_input)
        add_users_layout.addRow("Разрешения доступа:", self.permissions_combo)
        add_users_layout.addRow(add_button)
        add_users_layout.addRow(import_button)  # Add import button
        
        # add_users_layout.addRow(load_button)
        # add_users_layout.addRow(save_button)
        add_users_groupbox.setLayout(add_users_layout)

        # GroupBox 3: Editing Users
        edit_users_groupbox = QGroupBox("Редактирование пользователей")
        edit_users_layout = QFormLayout()
        edit_users_layout.addRow(edit_label)
        edit_users_layout.addRow("ID пользователя:", self.edit_id_input)
        edit_users_layout.addRow("Полное имя:", self.edit_full_name_input)
        edit_users_layout.addRow("Имя пользователя:", self.edit_username_input)
        edit_users_layout.addRow("Пароль:", self.edit_password_input)
        edit_users_layout.addRow("Разрешения доступа:", self.edit_permissions_combo)
        edit_users_layout.addRow(save_edit_button)
        edit_users_groupbox.setLayout(edit_users_layout)

        # GroupBox 4: Load/Save Database
        # load_save_groupbox = QGroupBox("Load/Save Database")
        # load_save_layout = QVBoxLayout()
        # load_save_layout.addWidget(load_button)
        # load_save_layout.addWidget(save_button)
        # load_save_groupbox.setLayout(load_save_layout)

        # GroupBox 5: Search/Delete Users
        search_delete_groupbox = QGroupBox("Поиск/Удаление пользователей")
        search_delete_layout = QVBoxLayout()
        search_delete_layout.addWidget(search_label)
        search_delete_layout.addWidget(self.search_id_input)
        search_delete_layout.addWidget(search_button)
        search_delete_layout.addWidget(delete_button)
        search_delete_layout.addWidget(export_button)  # Add export button
        search_delete_groupbox.setLayout(search_delete_layout)

        # Add GroupBoxes to Right Half Layout
        right_half_layout.addWidget(user_info_groupbox)
        right_half_layout.addWidget(add_users_groupbox)
        right_half_layout.addWidget(edit_users_groupbox)
        # right_half_layout.addWidget(load_save_groupbox)
        right_half_layout.addWidget(search_delete_groupbox)


        # Top Layout: Back, Logout, and Username
        top_layout = QHBoxLayout()
        back_button = QPushButton("Назад")
        logout_button = QPushButton("Выход из аккаунта")
        username_label = QLabel(f"Username: {self.username}")

        top_layout.addWidget(back_button)
        top_layout.addWidget(logout_button)
        top_layout.addWidget(username_label)

        # Signals and slots
        back_button.clicked.connect(self.back_function)
        add_button.clicked.connect(self.add_user)

        logout_button.clicked.connect(self.logout)
        search_button.clicked.connect(self.search_user)
        delete_button.clicked.connect(self.delete_user)
        save_edit_button.clicked.connect(self.save_edit_user)
        import_button.clicked.connect(self.import_users)
        export_button.clicked.connect(self.export_users)
        # Layout
        main_layout = QHBoxLayout()
        # main_layout.addLayout(top_layout)
        main_layout.addLayout(user_table_layout)
        main_layout.addLayout(right_half_layout)

        full_window_layout = QVBoxLayout()
        full_window_layout.addLayout(top_layout)
        full_window_layout.addLayout(main_layout)


        self.setLayout(full_window_layout)
        
        # Reload user data
        self.load_user_data()

    def logout(self):
        self.login_window.show()
        self.hide()

    def back_function(self):

        self.previous_window.show()
        self.hide()

    def load_user_data(self):
        # Load user data from the database and update the table
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        users = self.cursor.fetchall()

        self.user_table.setRowCount(0)
        for user in users:
            row_position = self.user_table.rowCount()
            self.user_table.insertRow(row_position)
            for column, data in enumerate(user):
                self.user_table.setItem(row_position, column, QTableWidgetItem(str(data)))

        # self.edit_permissions_combo.addItems(["Full", "Average", "Limited"])

    def add_user(self):
        # Get input values
        full_name = self.full_name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        permissions = self.permissions_combo.currentText()
         # Проверяем, что все поля ввода заполнены
        if not full_name or not username or not password:
            QMessageBox.warning(self, "Пустые поля", "Пожалуйста, заполните все поля для добавления пользователя.")
            return
            # Проверяем уникальность имени пользователя
        query = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        existing_user = self.cursor.fetchone()
        if existing_user:
            QMessageBox.warning(self, "Пользователь уже существует", "Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя пользователя.")
            return
        # Insert the new user into the database
        query = "INSERT INTO users (full_name, username, password, permissions) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (full_name, username, password, permissions))
        self.conn.commit()

        # Clear input fields
        self.full_name_input.clear()
        self.username_input.clear()
        self.password_input.clear()

        # Reload user data
        self.load_user_data()

    def save_user_data(self):
        # Save user data to a file (or take any other necessary action)
        pass
    

    


    def search_user(self):

        # self.edit_full_name_input.clear()
        # self.edit_username_input.clear()
        # self.edit_password_input.clear()
        # self.edit_permissions_combo.clear()
        # Search for a user by ID and populate the edit fields
        user_id = self.search_id_input.text()
        print(user_id)
        query = "SELECT * FROM users WHERE id = ?"
        self.cursor.execute(query, (user_id,))
        user = self.cursor.fetchall()
        if user:
            self.user_table.setRowCount(len(user))
            for row, result in enumerate(user):
                for col, value in enumerate(result):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsEnabled)  
                    self.user_table.setItem(row, col, item)
        else:
            # No search criteria provided
            # Display a message or handle it as needed
            query = "SELECT * FROM users"
            self.cursor.execute(query)
            user = self.cursor.fetchall()

            self.user_table.setRowCount(len(user))
            for row, result in enumerate(user):
                for col, value in enumerate(result):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsEnabled)  
                    self.user_table.setItem(row, col, item)


    def delete_user(self):
        # Delete user(s) by ID(s)
        input_ids = self.search_id_input.text()
        if not input_ids:
            QMessageBox.warning(self, "Пустой ввод", "Пожалуйста, введите ID(-ы) пользователя(-ей) для удаления.")
            return
        # Remove extra spaces before splitting IDs
        input_ids = input_ids.replace(" ", "")
        user_ids = input_ids.split(',')
        query = "DELETE FROM users WHERE id IN ({})".format(','.join(['?'] * len(user_ids)))
        self.cursor.execute(query, user_ids)
        self.conn.commit()

        # Reload user data
        self.load_user_data()

    def save_edit_user(self):
        # Save edited user data to the database
        user_id = self.edit_id_input.text()
        full_name = self.edit_full_name_input.text()
        username = self.edit_username_input.text()
        password = self.edit_password_input.text()
        permissions = self.edit_permissions_combo.currentText()
        # Проверяем, что все поля ввода заполнены
        if not full_name or not username or not password:
            QMessageBox.warning(self, "Пустые поля", "Пожалуйста, заполните все поля для сохранения изменений.")
            return



        query = """
        UPDATE users 
        SET 
            full_name = CASE WHEN ? != '' THEN ? ELSE full_name END,
            username = CASE WHEN ? != '' THEN ? ELSE username END,
            password = CASE WHEN ? != '' THEN ? ELSE password END,
            permissions = CASE WHEN ? != '' THEN ? ELSE permissions END
        WHERE id=?
        """
    
        self.cursor.execute(query, (full_name, full_name,
                                    username, username,
                                    password, password,
                                    permissions, permissions,
                                    user_id))        
        self.conn.commit()

        # Clear edit fields
        self.edit_id_input.clear()
        self.edit_full_name_input.clear()
        self.edit_username_input.clear()
        self.edit_password_input.clear()

        # Reload user data
        self.load_user_data()  # Load user data again without clearing permissions combo

if __name__ == '__main__':
    app = QApplication(sys.argv)
    username = "YourUsername"  # Replace with the actual username
    user_management_window = UserManagementWindow(username)
    user_management_window.show()
    sys.exit(app.exec_())