import sys
import pandas as pd

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QLineEdit, QDateTimeEdit, QDoubleSpinBox, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt  # Add this import
from PyQt5.QtWidgets import QPushButton

import sqlite3

class SalesManagementWindow(QWidget):
    def __init__(self, previous_window,login_window, username):
        super().__init__()

        self.setWindowTitle("Управление продажами")
        self.showFullScreen()
        
        self.previous_window = previous_window
        self.login_window = login_window
        self.username = username
        self.search_warning_label = QLabel()

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

        # Create a table to store sales information if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                saler_name TEXT NOT NULL,
                region TEXT NOT NULL,
                date TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        # Top GroupBox with buttons and labels
        top_layout = QHBoxLayout()
        back_button = QPushButton("Назад")
        # logout_button = QPushButton("Назад")
        window_name_label = QLabel("Управление продажами")
        username_label = QLabel(f"Username: {self.username}")

        top_layout.addWidget(back_button)
        top_layout.addWidget(window_name_label)
        top_layout.addWidget(username_label)

        top_groupbox = QGroupBox()
        top_groupbox.setLayout(top_layout)

        # Left GroupBox: Table from DB (including sales information)
        left_layout = QVBoxLayout()
        table_label = QLabel("Таблица из базы данных (Продажи):")
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Product Name", "Saler Name", "Region", "Date", "Price"])

        # Fetch and display sales information
        query = "SELECT * FROM sales"
        self.cursor.execute(query)
        sales_data = self.cursor.fetchall()

        self.sales_table.setRowCount(len(sales_data))
        for row, sale in enumerate(sales_data):
            for col, value in enumerate(sale):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)  # Make cells read-only
                self.sales_table.setItem(row, col, item)

        left_layout.addWidget(table_label)
        left_layout.addWidget(self.sales_table)

        left_groupbox = QGroupBox()
        left_groupbox.setLayout(left_layout)

        # Center GroupBox: Buttons only
        center_layout = QVBoxLayout()
        button_add = QPushButton("Добавить товар")
        button_search = QPushButton("Поиск товара")
        button_edit = QPushButton("Редактирование")
        button_export = QPushButton("Экспорт в Excel")
        button_import = QPushButton("Импорт из Excel")
        button_clear_all = QPushButton("Полная очистка проданных товаров")

        center_layout.addWidget(button_add)
        center_layout.addWidget(button_search)
        center_layout.addWidget(button_edit)
        center_layout.addWidget(button_export)  # Add export button
        center_layout.addWidget(button_import)  # Add import button
        center_layout.addWidget(button_clear_all)

        center_groupbox = QGroupBox()
        center_groupbox.setLayout(center_layout)

        # Right GroupBox: Form with inputs and buttons
        self.right_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        # input_product_name = QLineEdit()
        # input_saler_name = QLineEdit()
        # input_region = QLineEdit()
        # input_date = QDateTimeEdit()
        # input_date.setDisplayFormat("dd.MM.yyyy")
        # input_price = QDoubleSpinBox()
        # input_price.setMaximum(999999)  

        # self.form_layout.addRow("Название товара:", input_product_name)
        # self.form_layout.addRow("ФИО:", input_saler_name)
        # self.form_layout.addRow("Регион:", input_region)
        # self.form_layout.addRow("Дата:", input_date)
        # self.form_layout.addRow("Стоимость товара:", input_price)

        self.button_save = QPushButton("Сохранить")
        self.button_clear = QPushButton("Очистить")
        
        # self.button_load = QPushButton("Загрузить")

        # self.right_layout.addLayout(self.form_layout)
        # self.right_layout.addWidget(self.button_save)
        # self.right_layout.addWidget(self.button_clear)
        # self.right_layout.addWidget(self.button_load)

        self.right_groupbox = QGroupBox()
        self.right_groupbox.setLayout(self.right_layout)

        # Main Layout: Horizontal arrangement of left, center, and right GroupBoxes
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(left_groupbox, 6)  # 60%
        self.main_layout.addWidget(center_groupbox, 2)  # 20%
        self.main_layout.addWidget(self.right_groupbox, 2)  # 20%

        # Overall Layout: Vertical arrangement of top and main layouts
        self.overall_layout = QVBoxLayout()
        self.overall_layout.addWidget(top_groupbox)
        self.overall_layout.addLayout(self.main_layout)

        self.setLayout(self.overall_layout)

        # Signals and slots for buttons (placeholder functions)
        back_button.clicked.connect(self.go_back)
        # logout_button.clicked.connect(self.logout)
        # self.button_save.clicked.connect(self.save_data)
        # self.button_clear.clicked.connect(self.clear_form)
        # self.button_load.clicked.connect(load_data)

        button_add.clicked.connect(self.add_product)
        button_search.clicked.connect(self.search_product)
        button_edit.clicked.connect(self.edit_product)
        button_export.clicked.connect(self.export_to_excel)
        button_import.clicked.connect(self.import_from_excel)
        button_clear_all.clicked.connect(self.clear_all_sales)



    def clear_all_sales(self):
        # Ask for confirmation
        confirmation = QMessageBox.question(self, "Подтверждение",
                                            "Вы уверены, что хотите очистить все продажи?",
                                            QMessageBox.Yes | QMessageBox.No)

        if confirmation == QMessageBox.Yes:
            # Clear all sales records from the database
            query = "DELETE FROM sales"
            self.cursor.execute(query)
            self.conn.commit()

            # Refresh the sales table to reflect the changes
            self.refresh_sales_table()

    # Placeholder functions for button actions
    def save_data(self):
        print('SAVING')
        product_name = self.input_product_name.text()
        saler_name = self.input_saler_name.text()
        region = self.input_region.text()
        date = self.input_date.text()
        price = self.input_price.value()

        # Validate the input data if needed

        # Insert new sale data into the database
        query = "INSERT INTO sales (product_name, saler_name, region, date, price) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(query, (product_name, saler_name, region, date, price))
        self.conn.commit()

        # Refresh the sales table
        self.refresh_sales_table()

        # Clear the input fields
        self.clear_form()

    def clear_form(self):
        self.input_product_name.clear()
        self.input_saler_name.clear()
        self.input_region.clear()
        self.input_date.clear()
        self.input_price.clear()

    # def load_data():
    #     # Placeholder for loading data from Excel
    #     file_dialog = QFileDialog()
    #     file_path, _ = file_dialog.getOpenFileName(self, "Выберите файл Excel", "", "Excel Files (*.xlsx *.xls)")
    #     if file_path:
    #         # Implement loading logic from Excel here
    #         pass

    def add_product(self):

        self.main_layout.removeWidget(self.right_groupbox)
        self.right_groupbox.deleteLater()
        
        right_layout = QVBoxLayout()
        form_layout = QFormLayout()
    

        self.input_product_name = QLineEdit()
        self.input_saler_name = QLineEdit()
        self.input_region = QLineEdit()
        self.input_date = QDateTimeEdit()
        self.input_date.setDisplayFormat("dd.MM.yyyy")
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(999999)  

        form_layout.addRow("Название товара:", self.input_product_name)
        form_layout.addRow("ФИО:", self.input_saler_name)
        form_layout.addRow("Регион:", self.input_region)
        form_layout.addRow("Дата:", self.input_date)
        form_layout.addRow("Стоимость товара:", self.input_price)

        self.button_save = QPushButton("Сохранить")
        self.button_clear = QPushButton("Очистить")

        self.button_save.clicked.connect(self.save_data)
        self.button_clear.clicked.connect(self.clear_form)

        # self.button_load = QPushButton("Загрузить")
        
        form_layout.addWidget(self.button_save)
        right_layout.addWidget(self.button_clear)


        right_layout.addLayout(form_layout)
        
        # right_layout.addWidget(self.button_load)

        self.right_groupbox = QGroupBox()
        self.right_groupbox.setLayout(right_layout)
        self.main_layout.addWidget(self.right_groupbox)


    def search_product(self):

        # print('Pressed search')
        self.main_layout.removeWidget(self.right_groupbox)
        self.right_groupbox.deleteLater()

        # Create a new layout for the search form
        new_layout = QVBoxLayout()

        # Form with inputs
        form_layout = QFormLayout()
        self.input_search_id = QLineEdit()
        self.input_search_product_name = QLineEdit()
        self.input_search_saler_name = QLineEdit()

        form_layout.addRow("ID:", self.input_search_id)
        form_layout.addRow("Название товара:", self.input_search_product_name)
        form_layout.addRow("ФИО:", self.input_search_saler_name)

        new_layout.addLayout(form_layout)

        # Buttons
        self.button_search_product = QPushButton("Поиск")
        self.button_clear_search = QPushButton("Очистить")
        new_layout.addWidget(self.button_search_product)
        new_layout.addWidget(self.button_clear_search)

        self.search_warning_label = QLabel()
        new_layout.addWidget(self.search_warning_label)


        self.right_groupbox = QGroupBox()
        self.right_groupbox.setLayout(new_layout)
        self.main_layout.addWidget(self.right_groupbox)

        self.button_search_product.clicked.connect(self.search_submit)
        self.button_clear_search.clicked.connect(self.search_clear)


    def edit_product(self):

        self.main_layout.removeWidget(self.right_groupbox)
        self.right_groupbox.deleteLater()

        edit_layout = QVBoxLayout()
        form_edit_layout = QFormLayout()

        self.input_edit_id = QLineEdit()
        self.input_edit_product_name = QLineEdit()
        self.input_edit_saler_name = QLineEdit()
        self.input_edit_region = QLineEdit()
        self.input_edit_date = QDateTimeEdit()
        self.input_edit_date.setDisplayFormat("dd.MM.yyyy")
        self.input_edit_price = QDoubleSpinBox()
        self.input_edit_price.setMaximum(999999)  

        form_edit_layout.addRow("ID:", self.input_edit_id)
        label_below_id = QLabel("Введите новые данные:")
        form_edit_layout.addRow(label_below_id)
        form_edit_layout.addRow("Название товара:", self.input_edit_product_name)
        form_edit_layout.addRow("ФИО:", self.input_edit_saler_name)
        form_edit_layout.addRow("Регион:", self.input_edit_region)
        form_edit_layout.addRow("Дата:", self.input_edit_date)
        form_edit_layout.addRow("Стоимость товара:", self.input_edit_price)

        button_edit_save = QPushButton("Сохранить")
        button_edit_search = QPushButton("Поиск")
        button_edit_del = QPushButton("Удалить")

        edit_layout.addLayout(form_edit_layout)
        edit_layout.addWidget(button_edit_save)
        edit_layout.addWidget(button_edit_search)
        edit_layout.addWidget(button_edit_del)
        # Add the warning label
        self.edit_warning_label = QLabel()
        edit_layout.addWidget(self.edit_warning_label)

        # Set the new layout to the right group box
        self.right_groupbox = QGroupBox()
        self.right_groupbox.setLayout(edit_layout)

        self.main_layout.addWidget(self.right_groupbox)

        button_edit_save.clicked.connect(self.edit_save)
        button_edit_search.clicked.connect(self.edit_search)
        button_edit_del.clicked.connect(self.edit_delete)



    def edit_delete(self):
        # Placeholder function for deleting a row by ID
        edit_id = self.input_edit_id.text()

        # Check if the ID is provided
        if not edit_id:
            self.edit_warning_label.setText("Please enter ID for deletion.")
            self.edit_warning_label.setStyleSheet("color: red;")
            return

        # Confirm deletion with user
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setText("Вы действительно хотите удалить информацию о товаре?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = confirm_dialog.exec_()

        if result == QMessageBox.Yes:
            # Delete the row from the database
            query = "DELETE FROM sales WHERE id=?"
            self.cursor.execute(query, (edit_id,))
            self.conn.commit()

            # Display a success message or handle errors
            self.edit_warning_label.setText("Record deleted successfully.")
            self.edit_warning_label.setStyleSheet("color: green;")

            # Clear the input fields after deletion
            self.clear_edit_form()
            self.refresh_sales_table()
        else:
            # User canceled the deletion
            self.edit_warning_label.setText("Deletion canceled.")
            self.edit_warning_label.setStyleSheet("color: orange;")

    def clear_edit_form(self):
        # Clear the input fields in the edit form
        self.input_edit_id.clear()
        self.input_edit_product_name.clear()
        self.input_edit_saler_name.clear()
        self.input_edit_region.clear()
        self.input_edit_date.clear()
        self.input_edit_price.clear()


    def edit_search(self):
        edit_id = self.input_edit_id.text()

        # Validate input (you can customize the validation logic)
        if not edit_id.isdigit():
            # Display error message in red text
            self.search_warning_label.setText("Invalid ID. Please enter a valid numeric ID.")
            self.search_warning_label.setStyleSheet("color: red;")
            return

        # Fetch data from the database based on the search criteria
        query = "SELECT * FROM sales WHERE id=?"
        self.cursor.execute(query, (edit_id,))
        search_result = self.cursor.fetchall()

        # Display the search result in the table
        self.sales_table.setRowCount(len(search_result))
        for row, result in enumerate(search_result):
            for col, value in enumerate(result):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)  # Make cells read-only
                self.sales_table.setItem(row, col, item)

        # Clear the input fields
        self.clear_edit_form()


    def edit_save(self):
        # Placeholder function for saving edited data
        edit_id = self.input_edit_id.text()
        new_product_name = self.input_edit_product_name.text()
        new_saler_name = self.input_edit_saler_name.text()
        new_region = self.input_edit_region.text()
        new_date = self.input_edit_date.text()
        new_price = self.input_edit_price.value()

        # Validate the input data if needed

        # Update the existing sale data in the database
        query = """
        UPDATE sales
        SET 
            product_name = CASE WHEN ? != '' THEN ? ELSE product_name END,
            saler_name = CASE WHEN ? != '' THEN ? ELSE saler_name END,
            region = CASE WHEN ? != '' THEN ? ELSE region END,
            date = CASE WHEN ? != '' THEN ? ELSE date END,
            price = CASE WHEN ? != '' THEN ? ELSE price END
        WHERE id=?
    """
        self.cursor.execute(query, (new_product_name, new_product_name,
                                    new_saler_name, new_saler_name,
                                    new_region, new_region,
                                    new_date, new_date,
                                    new_price, new_price,
                                    edit_id))
        self.conn.commit()

        # Display a success message or handle errors
        self.edit_warning_label.setText("Changes saved successfully.")
        self.edit_warning_label.setStyleSheet("color: green;")

        # Refresh the sales table
        self.refresh_sales_table()

        # Clear the input fields
        # clear_form()

    def search_submit(self):
        # Get the input values
        search_id = self.input_search_id.text()
        search_product_name = self.input_search_product_name.text()
        search_saler_name = self.input_search_saler_name.text()

        # Clear the warning label
        self.search_warning_label.clear()

        # # Validate input (you can customize the validation logic)
        # if not search_id.isdigit():
        #     self.search_warning_label.setText("Invalid ID. Please enter a valid numeric ID.")
        #     self.search_warning_label.setStyleSheet("color: red;")
        #     return
        # Construct the query based on the search criteria
        query = "SELECT * FROM sales WHERE "
        params = []

        if search_id:
            query += "id = ?"
            params.append(search_id)
        if search_product_name:
            if search_id:
                query += " AND "
            query += "product_name = ?"
            params.append(search_product_name)
        if search_saler_name:
            if search_id or search_product_name:
                query += " AND "
            query += "saler_name = ?"
            params.append(search_saler_name)

        # Execute the query and fetch the results
        if params:
            self.cursor.execute(query, params)
            search_results = self.cursor.fetchall()
            # Populate the table with the search results
            self.sales_table.setRowCount(len(search_results))
            for row, result in enumerate(search_results):
                for col, value in enumerate(result):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsEnabled)  
                    self.sales_table.setItem(row, col, item)
        else:
            # No search criteria provided
            # Display a message or handle it as needed
            query = "SELECT * FROM sales"
            self.cursor.execute(query)
            search_results = self.cursor.fetchall()

            self.sales_table.setRowCount(len(search_results))
            for row, result in enumerate(search_results):
                for col, value in enumerate(result):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsEnabled)  
                    self.sales_table.setItem(row, col, item)

        # self.refresh_sales_table()
        # Clear the input fields
        self.search_clear()

    def search_clear(self):
        print('clear')
        # Implement clear search form logic here
        self.input_search_id.clear()
        self.input_search_product_name.clear()
        self.input_search_saler_name.clear()


    def refresh_sales_table(self):
        # Fetch and display sales information
        query = "SELECT * FROM sales"
        self.cursor.execute(query)
        sales_data = self.cursor.fetchall()

        self.sales_table.setRowCount(len(sales_data))
        for row, sale in enumerate(sales_data):
            for col, value in enumerate(sale):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)  # Make cells read-only
                self.sales_table.setItem(row, col, item)



    def logout(self):
        self.login_window.show()
        self.hide()


    # Placeholder functions for button actions
    def go_back(self):
        self.previous_window.show()
        self.hide()  # Replace with actual logic
    
    def export_to_excel(self):
    # Fetch data from the database
        query = "SELECT * FROM sales"
        self.cursor.execute(query)
        sales_data = self.cursor.fetchall()

        # Convert data to pandas DataFrame
        df = pd.DataFrame(sales_data, columns=["ID", "Product Name", "Saler Name", "Region", "Date", "Price"])

        # Choose file path for saving the Excel file
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить в Excel", "", "Excel Files (*.xlsx)")

        # Check if user selected a file path
        if file_path:
            # Export DataFrame to Excel
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Экспорт завершен", "Данные успешно экспортированы в Excel.")

    
    def import_from_excel(self):
        # Choose file path for importing the Excel file
        file_path, _ = QFileDialog.getOpenFileName(self, "Импорт из Excel", "", "Excel Files (*.xls *.xlsx)")

        # Check if user selected a file path
        if file_path:
            try:
                # Read Excel file into pandas DataFrame
                df = pd.read_excel(file_path)

                # Convert date column to the desired format
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d.%m.%Y')

                # Insert DataFrame records into the database
                for index, row in df.iterrows():
                    query = "INSERT INTO sales (product_name, saler_name, region, date, price) VALUES (?, ?, ?, ?, ?)"
                    self.cursor.execute(query, (row["Product Name"], row["Saler Name"], row["Region"], row["Date"], row["Price"]))
            
                self.conn.commit()
                self.refresh_sales_table()  # Refresh table after import
                QMessageBox.information(self, "Импорт завершен", "Данные успешно импортированы из Excel.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка импорта", f"Произошла ошибка при импорте данных из Excel: {str(e)}")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    username = "YourUsername"  # Replace with the actual username
    sales_management_window = SalesManagementWindow(username)
    sales_management_window.show()
    sys.exit(app.exec_())
