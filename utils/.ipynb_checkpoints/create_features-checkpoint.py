import pandas as pd
import numpy as np
from utils.prep_dataset import clear_city

# для каждого заказа считаем цену товара только 
def base_info_check(df, window='14d'):
    ind = []
    # collect information about every order (в один день несколько заказо от одного юезра)
    check_info_order = pd.DataFrame(df\
                                .groupby(['user_id', 'НомерЗаказаНаСайте', 'date'])\
                                .sum()[['Количество', 'Цена']])\
                                .reset_index()[['user_id', 'Цена', 'Количество', 'date']]\
    
    check_info_order = check_info_order\
        .rename(columns={'Цена': 'Cумма_в_чеке', 'Количество': 'Количество_товаров_в_чеке'})
    
    # считаем траты за день
    check_info_order = check_info_order.groupby(['user_id', 'date']).sum().reset_index()
    
    # в начале считаем окном 
    # от значений полученных окном берем статистики 
    check_info_order = check_info_order.groupby('user_id')\
        .rolling(window = window, on = 'date')\
        .mean().reset_index(1, drop=True)\
        .groupby('user_id')\
        .agg(['mean', lambda x: np.std(x, ddof=0)])
    
    multi_index = check_info_order.columns
    ind.append('user_id')
    for pair in multi_index:
        i_col = pair[0] + '_' + pair[1] 
        ind.append(i_col)
        
    check_info = pd.DataFrame(data =np.array(check_info_order.reset_index()))
    check_info = check_info.set_axis(ind, axis=1) # final result/
    # check_info = check_info.fillna(0)
    
    check_info = check_info\
        .rename(columns={'Cумма_в_чеке_mean': 'mean_amt_order', 'Количество_товаров_в_чеке_mean': 'mean_qty_item_in_order',\
                        'Cумма_в_чеке_<lambda_0>': 'std_amt_order', 'Количество_товаров_в_чеке_<lambda_0>': \
                         'std_qty_item_in_order'})
    check_info = check_info[['user_id','mean_amt_order', 'mean_qty_item_in_order', 'std_amt_order', \
                             'std_qty_item_in_order']]

    return check_info

def detect_sex(df):
    female_name, male_name = [], []
    with open("../russian_name/female_names_rus.txt", "r") as f:
        for line in f.readlines():
            female_name.append(line[:-1])
            
    with open("../russian_name/male_names_rus.txt", "r") as f:
        for line in f.readlines():
            male_name.append(line[:-1])
        
    sex = pd.DataFrame({'name': female_name, 'sex': [1]*len(female_name)})
    sex = pd.concat([sex, pd.DataFrame({'name': male_name, 'sex': [-1]*len(male_name)})])
    sex = sex[['name', 'sex']].drop_duplicates() 
     
    df = df[['user_id', 'Клиент']].drop_duplicates()   
    df = df[['user_id', 'Клиент']].drop_duplicates() 
    a = df[['user_id', 'Клиент']].groupby('user_id').count() > 1
    user_id = a[a.Клиент == True].reset_index().user_id.values
    df = df[~df.user_id.isin(user_id)]
    df = df.merge(sex, left_on='Клиент', right_on='name', how='left')
    df = df.drop(['name', 'Клиент'], axis = 1)
    df = df.drop_duplicates()  
    df = df.dropna(thresh = 2)
    return df

def add_stat(df):
    
    info_city_stat = pd.read_csv('../stat_data/info_city.csv')[['address', 'dolgota', 'население', 'зп новое 2014']]
    info_region = pd.read_csv('../stat_data/region.csv')
    
    df = df[['user_id', 'city']].drop_duplicates()
    info_city_stat['dolgota'] = info_city_stat['dolgota'].apply(lambda x: clear_city(x, 2))
    info_city_stat = info_city_stat.rename(columns={'dolgota': 'city'})
    info_region = info_region.rename(columns={'Город': 'city'})

    info_city_stat = pd.merge(info_city_stat, info_region, on=['city'], how='left')\
        [['address', 'население', 'city','зп новое 2014', 'Регион']]
    info_city_stat = info_city_stat.rename(columns={'Регион': 'region'})
    info_city_stat = info_city_stat.rename(columns={'dolgota': 'city'})

    client_region = pd.merge(df, info_city_stat, on=['city'], how='left')\
        [['user_id', 'region', 'население', 'зп новое 2014']]
    
    a = client_region[['user_id', 'region']].groupby('user_id').count() > 1
    user_id = a[a.region == True].reset_index().user_id.values
    client_region = client_region[~client_region.user_id.isin(user_id)]
    
    client_region['население'] = client_region.apply(lambda x: np.nan if x['население'] == '#Н/Д'\
                                                 else x['население'],axis = 1)
    client_region = client_region.dropna(thresh = 2)
    client_region = client_region.drop_duplicates() 
    return client_region

def share_group2(df):
    ind_share, to_drop_column = [], []
    
    df = df.pivot_table(index='user_id', columns='Группа2', \
                                            values=['Количество'], aggfunc=['sum'])
    multi_index = df.columns
    ind_share.append('user_id')
    for pair in multi_index:
        i_col = pair[0] + '_' + pair[1] + '_' + pair[2]
        ind_share.append(i_col)

    category_info = pd.DataFrame(data = np.array(df.reset_index()))
    category_info = category_info.set_axis(ind_share, axis=1) # final result/
    category_info = category_info.fillna(0)
    
    category_info['sum'] = category_info.loc[:, category_info.columns != 'user_id'].sum(axis=1)
    
    columns_actual = [i_name for i_name in ind_share if i_name.find('sum_Количество') != -1]
    for i_name_col in columns_actual:
        start = i_name_col.find('о_') + 2
        new_name = 'share_' + i_name_col[start:]
        to_drop_column.append(i_name_col)
        category_info[new_name] = category_info[i_name_col] / category_info['sum']
        
    category_info = category_info.drop(columns=to_drop_column)
    return category_info

# для формирования этих признаков не важна дата и поэтому не зависит от разбиения 
def stat_features(df, users):
    sex = detect_sex(df)
    stat = add_stat(df)
    
    # # результут сегменатации
    segment = pd.read_csv('../segment_model/user_segmentation.csv', index_col=0)
    
    stat_user_features = users.merge(sex,
                           on=['user_id'],
                           how='left')\
                         .merge(stat,
                                   on=['user_id'],
                                   how='left')\
                         .merge(segment,
                           on=['user_id'],
                           how='left')
    # preprocessing
    stat_item_features = df[['item_id', 'Группа2', 'Тип']].drop_duplicates()
    
    stat_user_features['население'] = stat_user_features['население'].apply(lambda x: x.replace(u'\xa0', '') if x is not np.nan
                                                                        else x)
    stat_user_features['население'] = stat_user_features['население'].apply(lambda x: int(x) if x is not np.nan
                                                                        else x)
    stat_user_features['зп новое 2014'] = stat_user_features['зп новое 2014'].apply(lambda x: x.replace(u'\xa0', '') if x is not np.nan
                                                                        else x)
    stat_user_features['зп новое 2014'] = stat_user_features['зп новое 2014'].apply(lambda x: float(x) if x is not np.nan
                                                                        else x)
    
    stat_user_features['sex'] = stat_user_features['sex'].fillna(0)
    stat_user_features = pd.get_dummies(stat_user_features, columns=['sex'], drop_first=True)
    stat_user_features = pd.get_dummies(stat_user_features, columns=['region'], drop_first=True)
    stat_item_features = pd.get_dummies(stat_item_features, columns=['Группа2'], drop_first=True)
    stat_item_features = pd.get_dummies(stat_item_features, columns=['Тип'], drop_first=True)
    stat_user_features = pd.get_dummies(stat_user_features, columns=['segment'], drop_first=True)
    
    stat_user_features = stat_user_features\
        .rename(columns={'зп новое 2014': 'Зарплата'})
    
    return stat_user_features, stat_item_features

# количество прошедших дней между покупкой
def qty_last_dt(group):
    if len(group) == 1:
        return 0
    else:
        group = group.sort_values(by='date', ascending=False)
        day = (group.iloc[0,-1] - group.iloc[1,-1]).days
        return int(day)