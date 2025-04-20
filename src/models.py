import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scraper import start_scraping

def creation_of_observations(step=50000, max_value=1000000, max_mounth=12):
    """
    Функция создает наблюдения для будущей модели KNN.
    """
    df = pd.DataFrame({
        'Сумма вклада': range(10000, max_value, step),
        'Срок вклада': np.random.randint(1, (max_mounth + 1), size=len(range(10000, max_value, step)))
    })
    df1 = df.copy()
    df2 = df.copy()
    df['Пополнение'] = 1
    df['Снятие'] = 1
    df1['Пополнение'] = 0
    df1['Снятие'] = 0
    df2['Пополнение'] = 1
    df2['Снятие'] = 0
    df = pd.concat([df, df1, df2], ignore_index=True)
    return df

def find_best_deposit(row, deposits):
    """
    Присваивает лучший вклад набору требований, иначе None.
    """
    filtered_deposits = deposits[
        (row['Срок вклада'] >= deposits['Минимальный срок']) &
        (row['Срок вклада'] <= deposits['Максимальный срок']) &
        (row['Сумма вклада'] >= deposits['Минимальная сумма']) &
        (row['Сумма вклада'] <= deposits['Максимальная сумма']) &
        ((row['Пополнение'] == deposits['Возможность пополнения']) | (~row['Пополнение'])) &
        ((row['Снятие'] == deposits['Возможность снятия']) | (~row['Снятие']))
    ]
    if not filtered_deposits.empty:
        best_deposit = filtered_deposits.loc[filtered_deposits['Годовая ставка в %'].idxmax()]
        return best_deposit['Название вклада']
    else:
        return 'Нет подходящего вклада'

def load_deposits():
    """
    Загружает DataFrame с данными вкладов из файла.
    """
    return pd.read_csv('./data/deposits.csv')

def update_observations_info():
    """
    Обновляет информацию наблюдений.
    """
    deposits = load_deposits()
    observations = creation_of_observations(20000, 1000000, 12)
    observations['Лучший вклад'] = observations.apply(find_best_deposit, axis=1, deposits=deposits)
    observations.to_csv('./data/observations.csv', index=False)

def scale_features(df, features):
    """
    Масштабирует указанные признаки в DataFrame.
    """
    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])
    return df, scaler

def update_info():
    '''
    Обновляет информацию о вкладах и наблюдениях
    '''
    start_scraping()
    update_observations_info()

def load_observations():
    """
    Загружает DataFrame с данными наблюдений из файла.
    """
    return pd.read_csv('./data/observations.csv')