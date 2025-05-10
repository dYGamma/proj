import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, 
                             QFormLayout, QLineEdit, QDateTimeEdit, QComboBox, QCheckBox,
                             QFileDialog, QScrollArea, QSizePolicy, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtGui import QIntValidator
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from datetime import datetime, timedelta
import seaborn as sns

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        
    def clear(self):
        self.ax.clear()

class SalesAnalysisWindow(QWidget):
    def __init__(self, previous_window, login_window, username):
        super().__init__()
        self.previous_window = previous_window
        self.login_window = login_window
        self.username = username
        self.current_figure = None
        self.sales_data = []
        self.init_db()
        self.init_ui()
        
        self.populate_sales_table()
        self.setWindowTitle("Анализ продаж")
        self.showMaximized()

    def init_db(self):
        self.conn = sqlite3.connect("user_database.db")
        self.cursor = self.conn.cursor()
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
        main_layout = QVBoxLayout()
        
        # Top controls
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Назад")
        self.title_label = QLabel("Расширенный анализ продаж")
        self.user_label = QLabel(f"Пользователь: {self.username}")
        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.title_label)
        top_layout.addWidget(self.user_label)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Data and filters
        left_panel = QVBoxLayout()
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Продукт", "Продавец", "Регион", "Дата", "Цена"])
        left_panel.addWidget(self.sales_table)
        
        # Filter controls
        filter_group = QGroupBox("Фильтры")
        filter_layout = QGridLayout()
        
        self.analysis_type = QComboBox()
        self.analysis_type.addItems([
            "Распределение продуктов",
            "Продажи по регионам",
            "Динамика продаж",
            "Прогноз продаж",
            "Статистические показатели",
            "Тепловая карта продаж",
            "Сравнение периодов"
        ])
        
        self.region_filter = QComboBox()
        self.product_filter = QComboBox()
        self.date_start = QDateTimeEdit()
        self.date_start.setDateTime(QDateTime.currentDateTime().addMonths(-1))
        self.date_end = QDateTimeEdit()
        self.date_end.setDateTime(QDateTime.currentDateTime())
        self.compare_date_start = QDateTimeEdit()
        self.compare_date_end = QDateTimeEdit()
        self.forecast_method = QComboBox()
        self.forecast_method.addItems(["Скользящее среднее", "Линейная регрессия", "Экспоненциальное сглаживание"])
        
        filter_layout.addWidget(QLabel("Тип анализа:"), 0, 0)
        filter_layout.addWidget(self.analysis_type, 0, 1)
        filter_layout.addWidget(QLabel("Регион:"), 1, 0)
        filter_layout.addWidget(self.region_filter, 1, 1)
        filter_layout.addWidget(QLabel("Продукт:"), 2, 0)
        filter_layout.addWidget(self.product_filter, 2, 1)
        filter_layout.addWidget(QLabel("Начальная дата:"), 3, 0)
        filter_layout.addWidget(self.date_start, 3, 1)
        filter_layout.addWidget(QLabel("Конечная дата:"), 4, 0)
        filter_layout.addWidget(self.date_end, 4, 1)
        filter_layout.addWidget(QLabel("Метод прогноза:"), 5, 0)
        filter_layout.addWidget(self.forecast_method, 5, 1)
        filter_layout.addWidget(QLabel("Сравнить с периодом:"), 6, 0)
        filter_layout.addWidget(self.compare_date_start, 6, 1)
        filter_layout.addWidget(self.compare_date_end, 7, 1)
        
        filter_group.setLayout(filter_layout)
        left_panel.addWidget(filter_group)
        
        # Right panel - Visualization
        right_panel = QVBoxLayout()
        self.canvas = MplCanvas(self, width=10, height=8)
        self.toolbar = None  # Для совместимости с NavigationToolbar
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Анализировать")
        self.export_button = QPushButton("Экспорт графика")
        self.reset_button = QPushButton("Сбросить фильтры")
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.reset_button)
        
        right_panel.addWidget(self.canvas)
        right_panel.addLayout(button_layout)
        
        content_layout.addLayout(left_panel, 40)
        content_layout.addLayout(right_panel, 60)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        
        # Signals
        self.back_button.clicked.connect(self.go_back)
        self.analyze_button.clicked.connect(self.run_analysis)
        self.export_button.clicked.connect(self.export_chart)
        self.reset_button.clicked.connect(self.reset_filters)
        self.analysis_type.currentIndexChanged.connect(self.update_ui_controls)
        
        self.update_ui_controls()
        self.load_filters()

    def update_ui_controls(self):
        analysis_type = self.analysis_type.currentText()
        self.forecast_method.setVisible(analysis_type == "Прогноз продаж")
        self.compare_date_start.setVisible(analysis_type == "Сравнение периодов")
        self.compare_date_end.setVisible(analysis_type == "Сравнение периодов")

    def load_filters(self):
        self.cursor.execute("SELECT DISTINCT region FROM sales")
        regions = [row[0] for row in self.cursor.fetchall()]
        self.region_filter.addItems(regions)
        
        self.cursor.execute("SELECT DISTINCT product_name FROM sales")
        products = [row[0] for row in self.cursor.fetchall()]
        self.product_filter.addItems(products)

    def run_analysis(self):
        self.canvas.clear()
        analysis_type = self.analysis_type.currentText()
        
        # Get filtered data
        data = self.get_filtered_data()
        
        if analysis_type == "Распределение продуктов":
            self.show_product_distribution(data)
        elif analysis_type == "Продажи по регионам":
            self.show_region_sales(data)
        elif analysis_type == "Динамика продаж":
            self.show_time_series(data)
        elif analysis_type == "Прогноз продаж":
            self.show_forecast(data)
        elif analysis_type == "Статистические показатели":
            self.show_statistics(data)
        elif analysis_type == "Тепловая карта продаж":
            self.show_heatmap(data)
        elif analysis_type == "Сравнение периодов":
            self.compare_periods()
        
        self.canvas.draw()

    def get_filtered_data(self):
        query = '''SELECT * FROM sales 
                   WHERE date BETWEEN ? AND ?
                   AND region LIKE ?
                   AND product_name LIKE ?'''
        params = (
            self.date_start.dateTime().toString("dd.MM.yyyy"),
            self.date_end.dateTime().toString("dd.MM.yyyy"),
            '%' + self.region_filter.currentText() + '%',
            '%' + self.product_filter.currentText() + '%'
        )
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def show_product_distribution(self, data):
        products = defaultdict(float)
        for row in data:
            products[row[1]] += row[5]
        
        self.canvas.ax.pie(
            products.values(), 
            labels=products.keys(),
            autopct='%1.1f%%',
            startangle=90
        )
        self.canvas.ax.set_title('Распределение продаж по продуктам')

    def show_region_sales(self, data):
        regions = defaultdict(float)
        for row in data:
            regions[row[3]] += row[5]
        
        x = list(regions.keys())
        y = list(regions.values())
        
        self.canvas.ax.bar(x, y)
        self.canvas.ax.set_title('Продажи по регионам')
        self.canvas.ax.tick_params(axis='x', rotation=45)

    def show_time_series(self, data):
        dates = []
        amounts = []
        for row in data:
            date = datetime.strptime(row[4], "%d.%m.%Y")
            dates.append(date)
            amounts.append(row[5])
        
        self.canvas.ax.plot(dates, amounts, marker='o')
        self.canvas.ax.xaxis.set_major_formatter(DateFormatter("%d.%m.%Y"))
        self.canvas.ax.set_title('Динамика продаж')
        self.canvas.fig.autofmt_xdate()

    def show_forecast(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        df = df.resample('D', on='date').sum().reset_index()
        
        if len(df) < 5:
            self.canvas.ax.text(0.5, 0.5, 'Недостаточно данных для прогноза',
                             ha='center', va='center')
            return
        
        method = self.forecast_method.currentText()
        
        if method == "Скользящее среднее":
            window_size = 3
            df['forecast'] = df['price'].rolling(window_size).mean()
        elif method == "Линейная регрессия":
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['price'].values
            model = LinearRegression().fit(X, y)
            df['forecast'] = model.predict(X)
        elif method == "Экспоненциальное сглаживание":
            model = ExponentialSmoothing(df['price'], seasonal='add', seasonal_periods=7)
            model_fit = model.fit()
            df['forecast'] = model_fit.predict(start=0, end=len(df)-1)
        
        self.canvas.ax.plot(df['date'], df['price'], label='Фактические')
        self.canvas.ax.plot(df['date'], df['forecast'], label='Прогноз')
        self.canvas.ax.legend()
        self.canvas.ax.set_title(f'Прогноз продаж ({method})')
        self.canvas.ax.xaxis.set_major_formatter(DateFormatter("%d.%m.%Y"))
        self.canvas.fig.autofmt_xdate()

    def show_statistics(self, data):
        prices = [row[5] for row in data]
        stats = [
            ("Всего продаж", len(prices)),
            ("Средняя цена", np.mean(prices)),
            ("Максимальная цена", np.max(prices) if prices else 0),
            ("Минимальная цена", np.min(prices) if prices else 0),
            ("Общая выручка", sum(prices))
        ]
        
        self.canvas.ax.axis('off')
        table = self.canvas.ax.table(
            cellText=stats,
            loc='center',
            colLabels=('Показатель', 'Значение'),
            cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)

    def show_heatmap(self, data):
        # Исправленные названия колонок (добавлен недостающий столбец)
        df = pd.DataFrame(data, columns=['id','product_name','saler_name','region','date','price'])
        
        # Создаем сводную таблицу
        try:
            pivot = df.pivot_table(
                index='region', 
                columns='product_name', 
                values='price', 
                aggfunc='sum'
            ).fillna(0)
            
            # Отрисовываем тепловую карту
            sns.heatmap(pivot, ax=self.canvas.ax, cmap="YlGnBu", annot=True, fmt=".1f")
            self.canvas.ax.set_title('Тепловая карта продаж')
            plt.tight_layout()
            
        except Exception as e:
            print(f"Ошибка при создании тепловой карты: {e}")
            self.canvas.ax.clear()
            self.canvas.ax.text(0.5, 0.5, 'Ошибка визуализации', ha='center', va='center')

    def compare_periods(self):
        # Основной период
        main_data = self.get_filtered_data()
        main_dates = [datetime.strptime(row[4], "%d.%m.%Y") for row in main_data]
        main_prices = [row[5] for row in main_data]
        
        # Сравниваемый период
        query = '''SELECT * FROM sales 
                   WHERE date BETWEEN ? AND ?'''
        params = (
            self.compare_date_start.dateTime().toString("dd.MM.yyyy"),
            self.compare_date_end.dateTime().toString("dd.MM.yyyy")
        )
        self.cursor.execute(query, params)
        compare_data = self.cursor.fetchall()
        compare_dates = [datetime.strptime(row[4], "%d.%m.%Y") for row in compare_data]
        compare_prices = [row[5] for row in compare_data]
        
        self.canvas.ax.plot(main_dates, main_prices, label='Основной период')
        self.canvas.ax.plot(compare_dates, compare_prices, label='Сравниваемый период')
        self.canvas.ax.legend()
        self.canvas.ax.set_title('Сравнение периодов')
        self.canvas.ax.xaxis.set_major_formatter(DateFormatter("%d.%m.%Y"))
        self.canvas.fig.autofmt_xdate()

    def export_chart(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
            options=options
        )
        if filename:
            self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight')

    def reset_filters(self):
        self.date_start.setDateTime(QDateTime.currentDateTime().addMonths(-1))
        self.date_end.setDateTime(QDateTime.currentDateTime())
        self.region_filter.setCurrentIndex(0)
        self.product_filter.setCurrentIndex(0)

    def populate_sales_table(self):
        self.cursor.execute("SELECT * FROM sales")
        data = self.cursor.fetchall()
        self.sales_table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(row):
                item = QTableWidgetItem(str(col))
                self.sales_table.setItem(row_idx, col_idx, item)

    def go_back(self):
        self.previous_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SalesAnalysisWindow(None, None, "admin")
    window.show()
    sys.exit(app.exec_())