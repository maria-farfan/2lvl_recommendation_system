import pandas as pd
import numpy as np

def top_k(user, item):
    return item[:len(user)]

def remove_train_items(train, preds, k):
    new_preds = pd.DataFrame()
    for user_id, user_data in train.groupby('user_id'):
        user_preds = preds[preds.user_id == user_id]
        new_preds = pd.concat([new_preds, 
                               user_preds[~np.in1d(user_preds.item_id, user_data.item_id)][:k]
                              ])
    return new_preds

def top_prediction(test, train, num_users, freq_thr=10, k=15):
    mean_rating = train.groupby('item_id').qty.mean()
    mean_rating = mean_rating[train.groupby('item_id').qty.sum() >= freq_thr]
    top_pred = np.array(mean_rating.sort_values(ascending=False).index)[:k]
    #preds = np.tile(preds, (num_users, 1))
    # get prediction for test
    test_pred = test.groupby('user_id').apply(lambda x: top_k(x, top_pred)).reset_index()
    test_pred = test_pred.rename(columns={0: "item_id"})
    test_pred = test_pred.explode("item_id")

    test_pred = remove_train_items(train, test_pred, k)
    test_pred['rank_top'] = test_pred.sort_values(by='user_id').groupby(['user_id'])['user_id'].rank(method='first').astype(int)
    return test_pred