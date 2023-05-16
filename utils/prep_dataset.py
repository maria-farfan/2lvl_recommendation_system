import pandas as pd
import datetime
import numpy as np

def clear_city(city, opt=1):
    if opt == 1:
        index = city.find('(') - 1
        if index > 0:
            city = city[:index]
        return city
    else:
        index = city.find('?')
        if index > 0:
            city = city[:index]
        return city
    
def replace_group_items(group2, group3, group4):
    if group4 is np.nan and group3 is not np.nan:
        return group3
    elif group4 is np.nan and group2 is not np.nan:
        return group2
    else:
        return group4     

def prepare_df(df):
    
    from datetime import datetime
    
    df['СуммаЗаказаНаСайте'] = df['СуммаЗаказаНаСайте'].apply(lambda x: x.replace(" ", ""))
    df['СуммаЗаказаНаСайте'] = df['СуммаЗаказаНаСайте'].astype(int)
    
    df['Цена'] = df['Цена'].apply(lambda x: x.replace(" ", ""))
    df['Цена'] = df['Цена'].apply(lambda x: x.replace(",", "."))
    df['Цена'] = df['Цена'].apply(lambda x: float(x))
    
    df['ЦенаЗакупки'] = df['ЦенаЗакупки'].astype(str)
    df['ЦенаЗакупки'] = df['ЦенаЗакупки'].apply(lambda x: x.replace(",", "."))
    df['ЦенаЗакупки'] = df['ЦенаЗакупки'].apply(lambda x: x.replace(" ", ""))
    df['ЦенаЗакупки'] = df['ЦенаЗакупки'].astype(float)
    
    df['Маржа'] = df['Маржа'].astype(str)
    df['Маржа'] = df['Маржа'].apply(lambda x: x.replace(",", "."))
    df['Маржа'] = df['Маржа'].apply(lambda x: x.replace(" ", ""))
    df['Маржа'] = df['Маржа'].astype(float)
    
    df['date_order_site'] = df['ДатаЗаказаНаСайте'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M'))
    df['date_delivery'] = df['ДатаДоставки'].apply(lambda x: datetime.strptime(str(x), '%d.%m.%Y %H:%M') if str(x) != 'nan' else x)
    df['date'] = df['Дата'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M'))
    
    df['mnth'] = df['date'].apply(lambda x: x.month)
    df['weekday'] = df['date'].apply(lambda x: x.weekday())
    df['time'] = df['date'].apply(lambda x: x.hour)
    df['date'] = df['date'].apply(lambda x: x.date())
    df['date'] = pd.to_datetime(df['date'])
    
    df = df.fillna({'ГородМагазина': 'Unknown', 'Регион': 'Unknown'})
    df['city'] = df['Регион'].apply(lambda x: clear_city(x))
    
    df['item_name'] = df.apply(lambda x: replace_group_items(x['Группа2'], x['Группа3'], x['Группа4']), axis=1)
    df['item_name'] = df.apply(lambda x: x['item_name'].lower() if x['item_name'] is not np.nan \
                               else x['item_name'], axis=1)
    
    return df