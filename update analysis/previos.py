import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QLineEdit, QDateTimeEdit, QDoubleSpinBox, QDesktopWidget, QFileDialog
from PyQt5.QtCore import Qt  
from PyQt5.QtCore import QDateTime

import sqlite3
import matplotlib.pyplot as plt


class SalesAnalysisWindow(QWidget):
    def __init__(self, previous_window, login_window, username):
        super().__init__()

        self.setWindowTitle("Анализ продаж")
        self.showFullScreen()

        self.previous_window = previous_window
        self.login_window = login_window
        self.username = username
        self.init_ui()
        self.init_db()
        self.populate_sales_table()

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
        window_name_label = QLabel("Анализ продаж")
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

        left_layout.addWidget(table_label)
        left_layout.addWidget(self.sales_table)

        left_groupbox = QGroupBox()
        left_groupbox.setLayout(left_layout)

        # Right GroupBox: Form with inputs and buttons for analysis
        right_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.input_id = QLineEdit()
        self.input_region = QLineEdit()
        self.input_start_date = QDateTimeEdit()
        self.input_start_date.setDisplayFormat("dd.MM.yyyy")
        self.input_start_date.setDateTime(QDateTime())
        self.input_end_date = QDateTimeEdit()
        self.input_end_date.setDisplayFormat("dd.MM.yyyy")
        self.input_end_date.setDateTime(QDateTime())
        
        form_layout.addRow("ID товара:", self.input_id)
        form_layout.addRow("Регион :", self.input_region)
        form_layout.addRow("Начальная дата анализа:", self.input_start_date)
        form_layout.addRow("Конечная дата анализа:", self.input_end_date)

        button_run_analysis = QPushButton("Запуск")
        button_clear = QPushButton("Очистить")

        right_layout.addLayout(form_layout)
        right_layout.addWidget(button_run_analysis)
        right_layout.addWidget(button_clear)

        right_groupbox = QGroupBox()
        right_groupbox.setLayout(right_layout)

        # Main Layout: Horizontal arrangement of left and right GroupBoxes
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_groupbox, 5)  # 50%
        main_layout.addWidget(right_groupbox, 5)  # 50%

        # Overall Layout: Vertical arrangement of top and main layouts
        overall_layout = QVBoxLayout()
        overall_layout.addWidget(top_groupbox)
        overall_layout.addLayout(main_layout)

        self.setLayout(overall_layout)

        # Signals and slots for buttons (placeholder functions)
        back_button.clicked.connect(self.go_back)
        button_run_analysis.clicked.connect(self.run_analysis)
        button_clear.clicked.connect(self.clear_form)

    def go_back(self):
        self.previous_window.show()
        self.hide() 


    def run_analysis(self):
        # Get the search criteria from the input fields
        search_id = self.input_id.text()
        start_date = self.input_start_date.dateTime().toString("dd.MM.yyyy")
        end_date = self.input_end_date.dateTime().toString("dd.MM.yyyy")
        search_region = self.input_region.text()

        # Construct the query based on the search criteria
        query = "SELECT * FROM sales WHERE "
        params = []

        if search_id:
            query += "id = ?"
            params.append(search_id)
        if start_date and end_date:
            if search_id:
                query += " AND "
            query += "date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        if search_region:
            if search_id or start_date or end_date:
                query += " AND "
            query += "region = ?"
            params.append(search_region)

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
            pass

        self.generate_pie_chart(search_results)

    def generate_pie_chart(self, sales_data):
        # Extract product names and their frequencies from the sales data
        product_counts = {}
        for sale in sales_data:
            product_name = sale[1]
            if product_name in product_counts:
                product_counts[product_name] += 1
            else:
                product_counts[product_name] = 1

        # Plot the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(product_counts.values(), labels=product_counts.keys(), autopct='%1.1f%%')
        plt.title('Product Distribution')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.show()

        
    def clear_form(self):

        query = "SELECT * FROM sales"
        self.cursor.execute(query)
        search_results = self.cursor.fetchall()

        self.sales_table.setRowCount(len(search_results))
        for row, result in enumerate(search_results):
            for col, value in enumerate(result):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)  
                self.sales_table.setItem(row, col, item)


    def populate_sales_table(self):
        query = "SELECT * FROM sales"
        self.cursor.execute(query)
        sales_data = self.cursor.fetchall()

        self.sales_table.setRowCount(len(sales_data))
        for row, sale in enumerate(sales_data):
            for col, value in enumerate(sale):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)  
                self.sales_table.setItem(row, col, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    username = "YourUsername"  
    sales_analysis_window = SalesAnalysisWindow(username)
    sales_analysis_window.show()
    sys.exit(app.exec_())
