import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_test_data(num_records=1000):
    # Базовые параметры
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    products = ['Ноутбук', 'Смартфон', 'Планшет', 'Наушники', 'Принтер']
    regions = ['Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск', 'Екатеринбург']
    salers = ['Иванов И.И.', 'Петрова А.С.', 'Сидоров В.В.', 'Козлова М.Д.', 'Смирнов О.К.']
    
    # Генерация случайных данных
    np.random.seed(42)
    
    # Исправление: создаем список строковых дат
    dates = [d.strftime('%d.%m.%Y') for d in pd.date_range(start_date, end_date)]
    
    data = []
    
    for _ in range(num_records):
        # Основные параметры
        date = np.random.choice(dates)  # Теперь это строка
        product = np.random.choice(products)
        region = np.random.choice(regions)
        saler = np.random.choice(salers)
        
        # Генерация цены (остается без изменений)
        base_price = {
            'Ноутбук': 50000,
            'Смартфон': 30000,
            'Планшет': 25000,
            'Наушники': 5000,
            'Принтер': 15000
        }[product]
        
        price = base_price * np.random.uniform(0.8, 1.2)
        
        if np.random.rand() < 0.05:
            price *= np.random.choice([0.1, 10])
        
        data.append({
            'Product Name': product,
            'Saler Name': saler,
            'Region': region,
            'Date': date,  # Уже отформатированная строка
            'Price': round(price, 2)
        })
    
    return pd.DataFrame(data)

def save_to_excel(df, filename='test_sales_data.xlsx'):
    # Сохраняем в Excel с правильным форматом
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sales')
    
    # Настраиваем форматы
    workbook = writer.book
    worksheet = writer.sheets['Sales']
    
    # Формат даты
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy'})
    worksheet.set_column('D:D', 12, date_format)
    
    # Формат денег
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_column('E:E', 15, money_format)
    
    writer.close()
    print(f"Файл {filename} успешно создан")

# Генерация данных
df = generate_test_data(1500)

# Сохранение в Excel
save_to_excel(df)

# Пример ручной проверки данных
print("\nПервые 5 строк данных:")
print(df.head())

print("\nСтатистика:")
print(df.describe())

print("\nРаспределение по продуктам:")
print(df['Product Name'].value_counts())

print("\nРаспределение по регионам:")
print(df['Region'].value_counts())