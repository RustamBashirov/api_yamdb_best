import pandas as pd
import sqlite3
import os

# Путь к базе данных
db_path = 'db.sqlite3'

# Подключение к базе данных
conn = sqlite3.connect(db_path)

# Папка с CSV файлами
csv_folder = './'  # Здесь укажите путь к папке с вашими CSV файлами

# Получаем список всех CSV файлов в папке
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# Префикс для имен таблиц
prefix = 'reviews_'  # Задайте нужный префикс

for csv_file in csv_files:
    # Читаем CSV файл в DataFrame
    df = pd.read_csv(os.path.join(csv_folder, csv_file))

    # Имя таблицы - имя файла + префикс
    table_name = prefix + os.path.splitext(csv_file)[0]

    # Записываем данные в таблицу, добавляя их к существующим
    df.to_sql(table_name, conn, if_exists='append', index=False)

    print(f'Данные из {csv_file} были загружены в таблицу {table_name}.')

# Закрываем соединение
conn.close()
