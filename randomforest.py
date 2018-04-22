# import ray.dataframe as pd

import datetime
import os
import sys
import time
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score

ROOT = os.path.abspath(os.path.split(sys.argv[0])[0])
model_name = 'btcinfo_randomforest.model'

test_one_name = os.path.join(ROOT, 'test_one_address_dataset.csv')

feature_labels = ['n_tx', 'total_received', 'total_sent', 'final_balance', 'all_in_addrs_count', 'all_out_addrs_count']
used_features = []


def select_features(x, y):
    from sklearn.feature_selection import SelectFromModel
    clf = RandomForestClassifier(n_estimators=10)
    clf = clf.fit(x, y)
    print("Importance of features:", clf.feature_importances_)
    importance = clf.feature_importances_
    indices = np.argsort(importance)[::-1]
    print(importance)
    print(indices)
    print(feature_labels)
    for f in range(x.shape[1]):
        print("{} {} {}".format(f, feature_labels[f], importance[indices[f]]))
    model = SelectFromModel(clf, prefit=True)
    x_new = model.transform(x)
    columns = x_new.shape[1]
    global used_features
    used_features = feature_labels[:columns]
    print(used_features)
    return x_new


def ml_train_test(feat, obj):
    clf = RandomForestClassifier(n_estimators=10)
    clf.fit(feat, obj)
    scores = cross_val_score(clf, feat, obj, cv=10)
    # save model
    joblib.dump(clf, os.path.join(ROOT, model_name))
    print("training model success, save to path: {} and validate score is:".format(model_name))
    print(scores)


def ret_name(res):
    if res == 1:
        predict_result_str = "exchange"
    elif res == 2:
            predict_result_str = "whale"
    elif res == 3:
        predict_result_str = "mixer"
    else:
        predict_result_str = "others"
    return predict_result_str


def ml_predict(df):
    clf = joblib.load(os.path.join(ROOT, model_name))

    global used_features
    X = df[used_features]

    X = df[feature_labels]
    # .astype('float32').as_matrix()

    # # feature matrix standardization
    # scaler = preprocessing.StandardScaler()
    # # scaler = preprocessing.MinMaxScaler()
    # # X = scaler.fit_transform(X)
    # X = select_features(X, None)
    t1 = time.time()
    result = clf.predict(X)
    print("==== Address predict ===")
    # print(df)
    print(result)
    index = 0
    ok_count = 0
    for res in result:
        result = 'ERROR'
        if res == df[["Address", "0_label"]].values[index][1]:
            result = '   OK'
            ok_count = ok_count + 1
        print("Address: {} Result: {} Predict: {} Label: {} ".format(df[["Address", "0_label"]].values[index][0],
                                                                     result,
                                                                     ret_name(res),
                                                                     ret_name(
                                                                         df[["Address", "0_label"]].values[index][1])))
        index = index + 1
    t2 = time.time()
    print("timstamp: {} ~ {}".format(t1, t2))
    print("Accuracy: {}%  Time: {}ms".format(round(ok_count/index, 2) * 100, round(((t2-t1) * 1000)/index, 2)))


def create_dataset(data_all):
    # exchange
    X = data_all[feature_labels].astype('float32').as_matrix()
    # feature matrix standardization
    scaler = preprocessing.StandardScaler()
    # scaler = preprocessing.MinMaxScaler()
    X = scaler.fit_transform(X)

    Y = data_all[['0_label']].astype('int32').as_matrix()
    Y = np.squeeze(Y, axis=1)
    # feature selection
    # X = select_features(X, Y)
    print("feature matrix shape: ", X.shape)
    print("label matrix shape: ", Y.shape)

    print("====== data shape ======")
    print("X:")
    print(X[0:5])
    print("Y:")
    print(Y[0:5])

    return X, Y


def main():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today = '2018-04-21'
    fname = os.path.join(ROOT, 'top1w_train_test_all_datasets_{}.csv'.format(today))
    print("====== Training ======")
    print("read datasets {}".format(fname))
    df = pd.read_csv(fname)
    print(feature_labels)
    data = df.fillna(0)
    print("get dataset count: {}".format(len(data)))
    feature_matrix, targets = create_dataset(data)
    # print(type(targets))
    ml_train_test(feature_matrix, targets)

    print("====== Tests ======")
    # load test the do predict
    fname_predict = os.path.join(ROOT, 'top1w_datasets_test.csv')
    df_predict = pd.read_csv(fname_predict)
    print("read test {}, len {}".format(fname_predict, len(df_predict)))
    df_predict = df_predict.fillna(0)
    ml_predict(df_predict)


if __name__ == '__main__':
    main()
