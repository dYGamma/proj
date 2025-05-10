import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, 
                             QFormLayout, QLineEdit, QDateEdit, QComboBox, QCheckBox,
                             QFileDialog, QScrollArea, QSizePolicy, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sqlite3
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from datetime import datetime, timedelta
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Для красивого оформления можно установить тему Plotly
px.defaults.template = "plotly_white"

# Виджет для отображения Plotly графиков через QWebEngineView
class PlotlyWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def update_plot(self, fig):
        html = fig.to_html(include_plotlyjs='cdn')
        self.setHtml(html)

class SalesAnalysisWindow(QWidget):
    def __init__(self, previous_window, login_window, username):
        super().__init__()
        self.previous_window = previous_window
        self.login_window = login_window
        self.username = username
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
        
        # Верхняя панель с кнопками и информацией
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Назад")
        self.title_label = QLabel("Расширенный анализ продаж")
        self.user_label = QLabel(f"Пользователь: {self.username}")
        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.title_label)
        top_layout.addWidget(self.user_label)
        
        # Основное содержимое окна
        content_layout = QHBoxLayout()
        
        # Левая панель – таблица и фильтры
        left_panel = QVBoxLayout()
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Продукт", "Продавец", "Регион", "Дата", "Цена"])
        left_panel.addWidget(self.sales_table)
        
        # Панель фильтров
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
            "Сравнение периодов",
            "Сезонное разложение",
            "Анализ выбросов",
            "Кластерный анализ",
            "Корреляционный анализ",
            "Прогноз (ARIMA/Prophet)",
            "Кумулятивные продажи",
            "Распределение цен"
        ])
        
        self.region_filter = QComboBox()
        self.product_filter = QComboBox()
        
        # Настройка элементов выбора даты без времени, с календарем и заданным форматом
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd.MM.yyyy")
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd.MM.yyyy")
        self.date_end.setDate(QDate.currentDate())
        
        self.compare_date_start = QDateEdit()
        self.compare_date_start.setCalendarPopup(True)
        self.compare_date_start.setDisplayFormat("dd.MM.yyyy")
        
        self.compare_date_end = QDateEdit()
        self.compare_date_end.setCalendarPopup(True)
        self.compare_date_end.setDisplayFormat("dd.MM.yyyy")
        
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
        
        # Правая панель – область визуализации с Plotly
        right_panel = QVBoxLayout()
        self.plotlyWidget = PlotlyWidget(self)
        
        # Панель с кнопками управления
        button_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Анализировать")
        self.export_button = QPushButton("Экспорт графика")
        self.reset_button = QPushButton("Сбросить фильтры")
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.reset_button)
        
        right_panel.addWidget(self.plotlyWidget)
        right_panel.addLayout(button_layout)
        
        content_layout.addLayout(left_panel, 40)
        content_layout.addLayout(right_panel, 60)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        
        # Подключение сигналов
        self.back_button.clicked.connect(self.go_back)
        self.analyze_button.clicked.connect(self.run_analysis)
        self.export_button.clicked.connect(self.export_chart)
        self.reset_button.clicked.connect(self.reset_filters)
        self.analysis_type.currentIndexChanged.connect(self.update_ui_controls)
        
        self.update_ui_controls()
        self.load_filters()

    def update_ui_controls(self):
        analysis_type = self.analysis_type.currentText()
        forecast_visible = analysis_type in ["Прогноз продаж", "Прогноз (ARIMA/Prophet)"]
        self.forecast_method.setVisible(forecast_visible)
        if analysis_type == "Прогноз (ARIMA/Prophet)":
            self.forecast_method.clear()
            self.forecast_method.addItems(["ARIMA", "Prophet"])
        elif analysis_type == "Прогноз продаж":
            self.forecast_method.clear()
            self.forecast_method.addItems(["Скользящее среднее", "Линейная регрессия", "Экспоненциальное сглаживание"])
        self.compare_date_start.setVisible(analysis_type == "Сравнение периодов")
        self.compare_date_end.setVisible(analysis_type == "Сравнение периодов")

    def load_filters(self):
        self.region_filter.clear()
        self.region_filter.addItem("Все регионы")
        self.cursor.execute("SELECT DISTINCT region FROM sales")
        regions = [row[0] for row in self.cursor.fetchall()]
        self.region_filter.addItems(regions)
        
        self.product_filter.clear()
        self.product_filter.addItem("Все товары")
        self.cursor.execute("SELECT DISTINCT product_name FROM sales")
        products = [row[0] for row in self.cursor.fetchall()]
        self.product_filter.addItems(products)

    def run_analysis(self):
        analysis_type = self.analysis_type.currentText()
        data = self.get_filtered_data()
        # В зависимости от выбранного типа анализа вызывается соответствующий метод,
        # который генерирует Plotly-объект и обновляет виджет
        if analysis_type == "Распределение продуктов":
            fig = self.show_product_distribution(data)
        elif analysis_type == "Продажи по регионам":
            fig = self.show_region_sales(data)
        elif analysis_type == "Динамика продаж":
            fig = self.show_time_series(data)
        elif analysis_type == "Прогноз продаж":
            fig = self.show_forecast(data)
        elif analysis_type == "Статистические показатели":
            fig = self.show_statistics(data)
        elif analysis_type == "Тепловая карта продаж":
            fig = self.show_heatmap(data)
        elif analysis_type == "Сравнение периодов":
            fig = self.compare_periods(data)
        elif analysis_type == "Сезонное разложение":
            fig = self.show_seasonal_decomposition(data)
        elif analysis_type == "Анализ выбросов":
            fig = self.show_outliers(data)
        elif analysis_type == "Кластерный анализ":
            fig = self.show_cluster_analysis(data)
        elif analysis_type == "Корреляционный анализ":
            fig = self.show_correlation_analysis(data)
        elif analysis_type == "Прогноз (ARIMA/Prophet)":
            fig = self.show_arima_prophet_forecast(data)
        elif analysis_type == "Кумулятивные продажи":
            fig = self.show_cumulative_sales(data)
        elif analysis_type == "Распределение цен":
            fig = self.show_price_distribution(data)
        else:
            fig = go.Figure()
        self.plotlyWidget.update_plot(fig)

    def get_filtered_data(self):
        region = self.region_filter.currentText()
        region_param = '%' if region == "Все регионы" else f'%{region}%'
        product = self.product_filter.currentText()
        product_param = '%' if product == "Все товары" else f'%{product}%'
        query = '''SELECT * FROM sales 
                   WHERE date BETWEEN ? AND ?
                   AND region LIKE ?
                   AND product_name LIKE ?'''
        params = (
            self.date_start.date().toString("dd.MM.yyyy"),
            self.date_end.date().toString("dd.MM.yyyy"),
            region_param,
            product_param
        )
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def show_product_distribution(self, data):
        products = defaultdict(float)
        for row in data:
            products[row[1]] += row[5]
        df = pd.DataFrame({
            'Продукт': list(products.keys()),
            'Продажи': list(products.values())
        })
        fig = px.pie(df, values='Продажи', names='Продукт',
                     title="Распределение продаж по продуктам",
                     hole=0.3)
        return fig

    def show_region_sales(self, data):
        regions = defaultdict(float)
        for row in data:
            regions[row[3]] += row[5]
        df = pd.DataFrame({
            'Регион': list(regions.keys()),
            'Продажи': list(regions.values())
        })
        fig = px.bar(df, x='Регион', y='Продажи', title="Продажи по регионам")
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def show_time_series(self, data):
        dates = []
        amounts = []
        for row in data:
            date = datetime.strptime(row[4], "%d.%m.%Y")
            dates.append(date)
            amounts.append(row[5])
        if not dates or not amounts:
            return go.Figure().add_annotation(text="Нет данных для отображения", x=0.5, y=0.5, showarrow=False)
        df = pd.DataFrame({'Дата': dates, 'Продажи': amounts})
        fig = px.line(df, x='Дата', y='Продажи', title="Динамика продаж", markers=True)
        return fig

    def show_forecast(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        # Переименование столбцов на русский язык
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
        df = df.set_index('Дата').resample('D').sum().reset_index()
        if len(df) < 5:
            return go.Figure().add_annotation(text="Недостаточно данных для прогноза", x=0.5, y=0.5, showarrow=False)
        method = self.forecast_method.currentText()
        if method == "Скользящее среднее":
            window_size = 3
            df['Прогноз'] = df['Цена'].rolling(window_size).mean()
        elif method == "Линейная регрессия":
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['Цена'].values
            model = LinearRegression().fit(X, y)
            df['Прогноз'] = model.predict(X)
        elif method == "Экспоненциальное сглаживание":
            model = ExponentialSmoothing(df['Цена'], seasonal='add', seasonal_periods=7)
            model_fit = model.fit()
            df['Прогноз'] = model_fit.predict(start=0, end=len(df)-1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Дата'], y=df['Цена'], mode='lines+markers', name='Фактические'))
        fig.add_trace(go.Scatter(x=df['Дата'], y=df['Прогноз'], mode='lines', name='Прогноз'))
        fig.update_layout(title=f"Прогноз продаж ({method})", xaxis_title="Дата", yaxis_title="Продажи")
        return fig

    def show_statistics(self, data):
        prices = [row[5] for row in data]
        stats = [
            ("Всего продаж", len(prices)),
            ("Средняя цена", np.mean(prices) if prices else 0),
            ("Максимальная цена", np.max(prices) if prices else 0),
            ("Минимальная цена", np.min(prices) if prices else 0),
            ("Общая выручка", sum(prices)),
            ("Стандартное отклонение", np.std(prices) if prices else 0),
            ("Медиана", np.median(prices) if prices else 0)
        ]
        header = [x[0] for x in stats]
        values = [x[1] for x in stats]
        fig = go.Figure(data=[go.Table(
            header=dict(values=["Показатель", "Значение"]),
            cells=dict(values=[header, values])
        )])
        fig.update_layout(title="Статистические показатели")
        return fig

    def show_heatmap(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        try:
            pivot = df.pivot_table(index='Регион', columns='Продукт', values='Цена', aggfunc='sum', fill_value=0)
            fig = px.imshow(pivot, text_auto=True, aspect="auto", title="Тепловая карта продаж")
            return fig
        except Exception as e:
            return go.Figure().add_annotation(text="Ошибка визуализации", x=0.5, y=0.5, showarrow=False)

    def compare_periods(self, data):
        # Основной период
        main_dates = [datetime.strptime(row[4], "%d.%m.%Y") for row in data]
        main_prices = [row[5] for row in data]
        # Сравниваемый период
        query = '''SELECT * FROM sales 
                   WHERE date BETWEEN ? AND ?'''
        params = (
            self.compare_date_start.date().toString("dd.MM.yyyy"),
            self.compare_date_end.date().toString("dd.MM.yyyy")
        )
        self.cursor.execute(query, params)
        compare_data = self.cursor.fetchall()
        compare_dates = [datetime.strptime(row[4], "%d.%m.%Y") for row in compare_data]
        compare_prices = [row[5] for row in compare_data]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=main_dates, y=main_prices, mode='lines+markers', name='Основной период'))
        fig.add_trace(go.Scatter(x=compare_dates, y=compare_prices, mode='lines+markers', name='Сравниваемый период'))
        fig.update_layout(title="Сравнение периодов", xaxis_title="Дата", yaxis_title="Продажи")
        return fig

    def show_seasonal_decomposition(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        df = df.set_index('date').resample('D').sum()
        if len(df) < 30:
            return go.Figure().add_annotation(text="Недостаточно данных для анализа", x=0.5, y=0.5, showarrow=False)
        decomposition = seasonal_decompose(df['price'], model='additive', period=7)
        dates = df.index
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            subplot_titles=["Наблюдаемый", "Тренд", "Сезонность", "Остатки"])
        fig.add_trace(go.Scatter(x=dates, y=decomposition.observed, mode='lines', name="Наблюдаемый"), row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.trend, mode='lines', name="Тренд"), row=2, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.seasonal, mode='lines', name="Сезонность"), row=3, col=1)
        fig.add_trace(go.Scatter(x=dates, y=decomposition.resid, mode='lines', name="Остатки"), row=4, col=1)
        fig.update_layout(height=800, title_text="Сезонное разложение")
        return fig

    def show_outliers(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        df = df.set_index('date').resample('D').sum().reset_index()
        q1 = df['price'].quantile(0.25)
        q3 = df['price'].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df['price'] < lower) | (df['price'] > upper)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['price'], mode='lines+markers', name="Продажи"))
        fig.add_trace(go.Scatter(x=outliers['date'], y=outliers['price'], mode='markers', 
                                 marker=dict(color='red', size=10), name="Выбросы"))
        fig.update_layout(title="Анализ выбросов", xaxis_title="Дата", yaxis_title="Продажи")
        return fig

    def show_cluster_analysis(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        pivot = df.pivot_table(index='Регион', columns='Продукт', values='Цена', aggfunc='sum', fill_value=0)
        scaler = StandardScaler()
        X = scaler.fit_transform(pivot)
        kmeans = KMeans(n_clusters=3)
        clusters = kmeans.fit_predict(X)
        pca = PCA(n_components=2)
        components = pca.fit_transform(X)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=components[:,0], y=components[:,1],
                                 mode='markers+text',
                                 marker=dict(color=clusters, colorscale='Viridis', size=12),
                                 text=list(pivot.index),
                                 textposition="top center"))
        fig.update_layout(title="Кластерный анализ регионов", xaxis_title="PC1", yaxis_title="PC2")
        return fig

    def show_correlation_analysis(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        pivot = df.pivot_table(index='Дата', columns='Продукт', values='Цена', aggfunc='sum', fill_value=0)
        corr = pivot.corr()
        fig = px.imshow(corr, text_auto=True, title="Корреляция между продуктами")
        return fig

    def show_arima_prophet_forecast(self, data):
        method = self.forecast_method.currentText()
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
        df = df.set_index('Дата').resample('D').sum().reset_index()
        if method == "ARIMA":
            model = ARIMA(df['Цена'], order=(1,1,1))
            results = model.fit()
            forecast = results.predict(start=0, end=len(df)-1)
            df['Прогноз'] = forecast
        else:
            prophet_df = df.rename(columns={'Дата':'ds', 'Цена':'y'})
            model = Prophet()
            model.fit(prophet_df)
            future = model.make_future_dataframe(periods=0)
            forecast = model.predict(future)
            df['Прогноз'] = forecast['yhat']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Дата'], y=df['Цена'], mode='lines+markers', name='Фактические'))
        fig.add_trace(go.Scatter(x=df['Дата'], y=df['Прогноз'], mode='lines', name='Прогноз'))
        fig.update_layout(title=f"Прогноз ({method})", xaxis_title="Дата", yaxis_title="Продажи")
        return fig

    def show_cumulative_sales(self, data):
        df = pd.DataFrame(data, columns=['id','product','seller','region','date','price'])
        df.rename(columns={'product':'Продукт', 'seller':'Продавец', 'region':'Регион', 
                           'date':'Дата', 'price':'Цена'}, inplace=True)
        df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
        df = df.sort_values('Дата')
        df['Кумулятивные продажи'] = df['Цена'].cumsum()
        fig = px.line(df, x='Дата', y='Кумулятивные продажи', title="Кумулятивные продажи")
        return fig

    def show_price_distribution(self, data):
        prices = [row[5] for row in data]
        df = pd.DataFrame({'Цена': prices})
        fig = px.histogram(df, x='Цена', nbins=20, marginal="rug", title="Распределение цен", opacity=0.75)
        fig.update_layout(bargap=0.1)
        return fig

    def export_chart(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "", 
            "HTML Files (*.html);;All Files (*)", 
            options=options
        )
        if filename:
            self.plotlyWidget.page().toHtml(lambda html: open(filename, "w", encoding="utf-8").write(html))

    def reset_filters(self):
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_end.setDate(QDate.currentDate())
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
        if self.previous_window:
            self.previous_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SalesAnalysisWindow(None, None, "admin")
    window.show()
    sys.exit(app.exec_())
