import codecs
import collections
import datetime
import os
import pickle
import sys
import time
import traceback
from time import sleep
import json
import numpy as np
import pandas as pd
import requests

ROOT = os.path.abspath(os.path.split(sys.argv[0])[0])


def checkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def checkexist(file):
    return os.path.exists(file)


def readListFromTxt(filePath):
    resultList = []
    fr = codecs.open(filePath, 'r', encoding='utf-8')
    while True:
        line = fr.readline()
        if line:
            resultList.append(line.strip())
        else:
            break
    fr.close()
    return resultList


def dump(path, data):
    output = open(path, 'wb')
    pickle.dump(data, output)
    output.close()


def load(path):
    pkl_file = open(path, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data


def writeList2csv(filePath, infoList):
    fw = open(filePath, 'w', encoding='utf-8')
    for itemList in infoList:
        line = ''
        if isinstance(itemList, list):
            line = ','.join(itemList)
        if isinstance(itemList, str):
            line = itemList.strip()
        if line:
            fw.write(line + '\n')
    fw.close()


root_url = "https://blockchain.info/"


def rawtx(tx):
    url = "{}/{}/{}".format(root_url, "rawtx", tx)
    cache_file = os.path.join(ROOT, "rawtx", tx)
    if checkexist(cache_file):
        return load(cache_file)
    r = requests.get(url)
    obj = r.json()
    dump(cache_file, obj)
    return obj


def rawblock(block):
    url = "{}/{}/{}".format(root_url, "rawblock", block)
    cache_file = os.path.join(ROOT, "rawblock", block)
    if checkexist(cache_file):
        return load(cache_file)
    r = requests.get(url)
    obj = r.json()
    dump(cache_file, obj)
    return obj


def rawaddr(addr, offset):
    url = "{}/{}/{}?offset={}".format(root_url, "rawaddr", addr, offset)
    cache_file = os.path.join(ROOT, "rawaddr", "{}_{}".format(addr, offset))
    if checkexist(cache_file):
        return load(cache_file)
    r = requests.get(url)
    obj = r.json()
    dump(cache_file, obj)
    return obj


def block_height(height):
    url = "{}{}/{}?format=json".format(root_url, "block-height", height)
    cache_file = os.path.join(ROOT, "block-height", str(height))
    if checkexist(cache_file):
        return load(cache_file)
    print(url)
    r = requests.get(url)
    obj = r.json()
    dump(cache_file, obj)
    return obj


def last_block():
    url = "{}/{}".format(root_url, "latestblock")
    r = requests.get(url)
    obj = r.json()
    return obj


def fix_balance(value):
    return round(value / 100000000, 2)


def tx_address(addr_info):
    filter_inputs_size = 5
    filter_out_size = 5
    mixing_size = 10
    txs_last_count = len(addr_info["txs"])
    tx_history = []
    all_in_addrs = []
    all_out_addrs = []

    last_time = 0
    if txs_last_count > 0:
        # print("is > 0 {}".format(addr_info["n_tx"]-1))
        addr_inputs = 0
        addr_out = 0
        for idx in range(0, txs_last_count):
            get_idx = txs_last_count - 1 - idx
            # print("get index of txs: {}".format(get_idx))
            try:
                # print(addr_info["txs"][get_idx]["inputs"])
                # print("address inputs count: {}".format(len(addr_info["txs"][get_idx]["inputs"])))
                addr_inputs = addr_inputs + len(addr_info["txs"][get_idx]["inputs"])
                # print("address out count: {}" .format(len(addr_info["txs"][get_idx]["out"])))
                addr_out = addr_out + len(addr_info["txs"][get_idx]["out"])
                # get input address and output address
                tx_collections = collections.OrderedDict()
                tx_collections['tx'] = addr_info["txs"][get_idx]['hash']
                tx_collections['time'] = addr_info["txs"][get_idx]['time']
                last_time = tx_collections['time']
                tx_collections['timeUTC'] = time.strftime("%Y-%m-%dT%H:%M:%S UTC",
                                                          time.gmtime(addr_info["txs"][get_idx]['time']))
                tx_collections['inputs'] = []
                tx_collections['out'] = []
                for input in addr_info["txs"][get_idx]["inputs"]:
                    if "prev_out" in input:
                        input_addr = input['prev_out']['addr']
                        input_value = fix_balance(input['prev_out']['value'])
                        if input_value >= filter_inputs_size and addr_info['address'] != input_addr:
                            tx_collections['inputs'].append({input_addr: input_value})
                            all_in_addrs.append(input_addr)

                for out in addr_info["txs"][get_idx]["out"]:
                    # print(out)
                    if "addr" in out:
                        out_addr = out['addr']
                        out_value = fix_balance(out['value'])
                        if out_value >= filter_out_size and addr_info['address'] != out_addr:
                            tx_collections['out'].append({out_addr: out_value})
                            all_out_addrs.append(out_addr)
                tx_history.append(tx_collections)
            except Exception as e:
                print("=====Exception======")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("{}".format(repr(traceback.format_exception(exc_type, exc_value, exc_traceback))))
                break
    return tx_history, all_in_addrs, all_out_addrs, last_time


if __name__ == '__main__':
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # today = "2018-04-21"
    # check folder
    caches = ['block-height', 'rawaddr', 'rawblock', 'rawtx']
    for name in caches:
        path = os.path.join(ROOT, name)
        print("init check path {}".format(path))
        checkdir(path)
    save_path = os.path.join(ROOT, 'top1w_richest_{}.csv'.format(today))
    top1w_addr = pd.read_csv(save_path)  # nrows to get top 10
    # get the wallet info
    df = top1w_addr.fillna(0)
    data = df[df['Wallet'] != 0]
    crition_1 = data['Wallet'].map(lambda x: x.split(': ')[1][0].isalpha())
    exchange_addrs = data[crition_1]
    exchange_addrs = exchange_addrs.sort_values(['Wallet'])

    crition_2 = data['Wallet'].map(lambda x: x.split(': ')[1][0].isnumeric())
    number_addrs = data[crition_2]

    exchange_addrs_file = os.path.join(ROOT, 'top1w_exchange_datasets_{}.csv'.format(today))
    exchange_addrs.to_csv(exchange_addrs_file, index=None)

    number_addrs_file = os.path.join(ROOT, 'top1w_number_datasets_{}.csv'.format(today))
    number_addrs.to_csv(number_addrs_file, index=None)

    dataset_file = os.path.join(ROOT, 'top1w_datasets_exchange_{}.csv'.format(today))
    dataset = []
    all_count = len(exchange_addrs)
    total_inputs_address = 0
    total_out_address = 0

    total_inputs_address_dataset = []
    total_out_address_dataset = []

    start = 1
    for index, rows in exchange_addrs.iterrows():
        print("get address info: {}  {}/{}".format(rows.Address, start, all_count))
        offset = 0
        start = start + 1
        try:
            addr_info = rawaddr(rows.Address, offset)
        except Exception as e:
            sleep(3)
            print("error .. sleep 3")
            try:
                addr_info = rawaddr(rows.Address, offset)
            except Exception as e:
                print("error exception to get address: {}".format(rows.Address))
            continue
        # add new features
        rows["n_tx"] = addr_info["n_tx"]
        if rows["n_tx"] > 100000:
            continue
        rows["total_received"] = fix_balance(addr_info["total_received"])
        rows["total_sent"] = fix_balance(addr_info["total_sent"])
        rows["final_balance"] = fix_balance(addr_info["final_balance"])
        # add tx transaction in and out
        print("process no {} / {}".format(index + 1, all_count))
        # transaction history save
        print("n_tx count:" + str(addr_info["n_tx"]))

        # get txs length of the get
        rows["tx_history"] = ""

        total_addr_tx_history = []
        total_addr_in_addrs = []
        total_addr_out_addrs = []

        while offset < rows["n_tx"] + 50:
            if offset > 0:
                try:
                    addr_info = rawaddr(rows.Address, offset)
                except Exception as e:
                    sleep(3)
                    print("get offset error .. sleep 3")
            tx_history, all_in_addrs, all_out_addrs, last_time = tx_address(addr_info)
            total_addr_tx_history.extend(tx_history)
            total_addr_in_addrs.extend(all_in_addrs)
            total_addr_out_addrs.extend(all_out_addrs)
            offset = offset + 50
            time_sub = datetime.datetime.utcnow().timestamp() - last_time > 3600 * 24 * 180
            if offset % 1000 == 0:
                print("get offset of the n_tx: {}   {} {}".format(offset, last_time, time_sub))
            if last_time > 0 and time_sub or offset > 20000:
                break

        rows["tx_history"] = json.dumps(total_addr_tx_history)
        print("orig inputs count {} , out count {}".format(len(total_addr_in_addrs), len(total_addr_out_addrs)))
        # d = {}
        # for one in total_addr_in_addrs:
        #     if one not in d:
        #         d[one] = 1
        #     else:
        #         d[one] = d[one] + 1
        # print(len(d))
        # print(d)
        # print(total_addr_out_addrs)

        total_addr_in_addrs = list(set(total_addr_in_addrs))
        # rows["all_in_addrs"] = json.dumps(total_addr_in_addrs)
        rows["all_in_addrs_count"] = len(total_addr_in_addrs)
        total_addr_out_addrs = list(set(total_addr_out_addrs))
        # rows["all_out_addrs"] = json.dumps(total_addr_out_addrs)
        rows["all_out_addrs_count"] = len(total_addr_out_addrs)
        print("inputs count {} , out count {}".format(rows["all_in_addrs_count"], rows["all_out_addrs_count"]))
        total_inputs_address_dataset.extend(total_addr_in_addrs)
        total_out_address_dataset.extend(total_addr_out_addrs)

        # rows["last_inputs_count"] = addr_inputs
        # rows["last_out_count"] = addr_out
        # rows["avg_last_inputs"] = round(addr_inputs / rows["txs_last_count"], 8)
        # rows["avg_last_out"] = round(addr_out / rows["txs_last_count"], 8)

        total_inputs_address = total_inputs_address + rows["all_in_addrs_count"]
        total_out_address = total_out_address + rows["all_out_addrs_count"]

        dataset.append(rows)

    df_dataset = pd.DataFrame(dataset)
    df_dataset.to_csv(dataset_file, index=None)

    total_inputs_address_dataset = list(set(total_inputs_address_dataset))
    df_allinputs = pd.DataFrame(total_inputs_address_dataset)
    all_inputs_file = os.path.join(ROOT, 'top1w_datasets_exchange_inputs_{}.csv'.format(today))
    df_allinputs.to_csv(all_inputs_file, index=None, header=None)

    total_out_address_dataset = list(set(total_out_address_dataset))
    df_allout = pd.DataFrame(total_out_address_dataset)
    all_out_file = os.path.join(ROOT, 'top1w_datasets_exchange_out_{}.csv'.format(today))
    df_allout.to_csv(all_out_file, index=None, header=None)
    print("Total Address: {} Inputs Address: {} , Out Address: {} End".format(len(total_inputs_address_dataset) +
                                                                              len(total_out_address_dataset),
                                                                              len(total_inputs_address_dataset),
                                                                              len(total_out_address_dataset)))

    # get mixing
    total_mixing_address_dataset = []
    last_block = last_block()
    # TODO, this is set the top height to test
    last_block['height'] = 519258
    last_height = last_block['height']
    print("get last_height: {}".format(last_height))
    start = 0
    get_mixing_size = 10000
    is_mixing_size = 10

    # get others
    get_others_size = 10000
    others_balance = 0.5
    total_others_address_dataset = []

    # get white list
    all_inputs_file = os.path.join(ROOT, 'top1w_datasets_exchange_inputs_{}.csv'.format(today))
    all_out_file = os.path.join(ROOT, 'top1w_datasets_exchange_out_{}.csv'.format(today))
    inputs_d = pd.read_csv(all_inputs_file)
    out_d = pd.read_csv(all_out_file)
    inputs_out_whitelist = np.union1d(inputs_d.values, out_d.values)
    print("get inputs out white list count: {}".format(len(inputs_out_whitelist)))
    while last_height - start > 0:
        get_height = last_height - start
        start = start + 1
        try:
            block = block_height(get_height)
            # print(block['blocks'][0])
            for tx in block['blocks'][0]['tx']:
                if len(tx["inputs"]) > is_mixing_size:
                    # print("get inputs size large then mixing size: {}".format(len(tx["inputs"])))
                    for input in tx["inputs"]:
                        if "prev_out" in input:
                            input_addr = input['prev_out']['addr']
                            input_value = fix_balance(input['prev_out']['value'])
                            if input_addr not in total_mixing_address_dataset \
                                    and input_addr not in inputs_out_whitelist:
                                total_mixing_address_dataset.append(input_addr)
                else:
                    for input in tx["inputs"]:
                        if "prev_out" in input:
                            input_addr = input['prev_out']['addr']
                            input_value = fix_balance(input['prev_out']['value'])
                            if input_value < others_balance and input_addr not in total_mixing_address_dataset \
                                    and input_addr not in inputs_out_whitelist:
                                total_others_address_dataset.append(input_addr)

            print("get mixing len {} others len {}".format(len(total_mixing_address_dataset),
                                                           len(total_others_address_dataset)))
            if len(total_mixing_address_dataset) > get_mixing_size \
                    and len(total_others_address_dataset) > get_others_size:
                break
        except Exception as e:
            print("=====Mixing get Exception======")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("{}".format(repr(traceback.format_exception(exc_type, exc_value, exc_traceback))))
            continue

    mixing_addrs_file = os.path.join(ROOT, 'top1w_mixing_datasets_{}.csv'.format(today))
    df_mixing = pd.DataFrame(total_mixing_address_dataset)
    df_mixing.to_csv(mixing_addrs_file, index=None, header=None)
    # print("mixing dump ok, len {}".format(len(total_mixing_address_dataset)))

    others_addrs_file = os.path.join(ROOT, 'top1w_others_datasets_{}.csv'.format(today))
    df_others = pd.DataFrame(total_others_address_dataset)
    df_others.to_csv(others_addrs_file, index=None, header=None)
    print("mixing dump ok, len {}, others dump ok, len {}".format(len(total_mixing_address_dataset),
                                                                  len(total_others_address_dataset)))

    df_allinputs_diff = pd.DataFrame(np.setdiff1d(df_allinputs, df_allout))
    df_allout_diff = pd.DataFrame(np.setdiff1d(df_allout, df_allinputs))
    print("get the 1 len {} , 2 len {} 3 len {}, 4 len {}".format(len(df_allinputs_diff),
                                                                  len(df_allout_diff),
                                                                  len(df_mixing),
                                                                  len(df_others)))
    df_allinputs_diff['0_label'] = 1
    df_allout_diff['0_label'] = 2
    df_mixing['0_label'] = 3
    df_others['0_label'] = 4

    # merge
    all_train = [df_allinputs_diff, df_allout_diff, df_mixing, df_others]
    train_test_file = os.path.join(ROOT, 'top1w_train_test_datasets_{}.csv'.format(today))
    train_test__all_file = os.path.join(ROOT, 'top1w_train_test_all_datasets_{}.csv'.format(today))
    df_all = pd.concat(all_train)
    df_all.columns = ['Address', '0_label']
    df_all.to_csv(train_test_file, index=None)
    all_count = len(df_all)
    print("get the train test file size: {}".format(all_count))

    dataset_train = []
    total_inputs_address_train_dataset = []
    total_out_address_train_dataset = []
    start = 1
    df_all = df_all.sample(frac=1)
    for index, rows in df_all.iterrows():
        print("get address info: {}  {}/{}".format(rows.Address, start, all_count))
        offset = 0
        start = start + 1
        try:
            addr_info = rawaddr(rows.Address, offset)
        except Exception as e:
            sleep(3)
            print("error .. sleep 3")
            try:
                addr_info = rawaddr(rows.Address, offset)
            except Exception as e:
                print("error exception to get address: {}".format(rows.Address))
            continue
        # add new features
        rows["n_tx"] = addr_info["n_tx"]
        rows["total_received"] = fix_balance(addr_info["total_received"])
        rows["total_sent"] = fix_balance(addr_info["total_sent"])
        rows["final_balance"] = fix_balance(addr_info["final_balance"])
        # add tx transaction in and out
        # print("process no {} / {}".format(index + 1, all_count))
        # transaction history save
        print("n_tx count:" + str(addr_info["n_tx"]))

        total_addr_tx_history = []
        total_addr_in_addrs = []
        total_addr_out_addrs = []

        while offset < rows["n_tx"] + 50:
            if offset > 0:
                try:
                    addr_info = rawaddr(rows.Address, offset)
                except Exception as e:
                    sleep(3)
                    print("get offset error .. sleep 3")
            tx_history, all_in_addrs, all_out_addrs, last_time = tx_address(addr_info)
            # total_addr_tx_history.extend(tx_history)
            total_addr_in_addrs.extend(all_in_addrs)
            total_addr_out_addrs.extend(all_out_addrs)
            offset = offset + 50
            time_sub = datetime.datetime.utcnow().timestamp() - last_time > 3600 * 24 * 180
            if offset % 1000 == 0:
                print("get offset of the n_tx: {}   {} {}".format(offset, last_time, time_sub))
            if last_time > 0 and time_sub or offset > 20000:
                break

        # rows["tx_history"] = json.dumps(total_addr_tx_history)
        print("orig inputs count {} , out count {}".format(len(total_addr_in_addrs), len(total_addr_out_addrs)))

        total_addr_in_addrs = list(set(total_addr_in_addrs))
        # rows["all_in_addrs"] = json.dumps(total_addr_in_addrs)
        rows["all_in_addrs_count"] = len(total_addr_in_addrs)
        total_addr_out_addrs = list(set(total_addr_out_addrs))
        # rows["all_out_addrs"] = json.dumps(total_addr_out_addrs)
        rows["all_out_addrs_count"] = len(total_addr_out_addrs)
        print("inputs count {} , out count {}".format(rows["all_in_addrs_count"], rows["all_out_addrs_count"]))
        total_inputs_address_train_dataset.extend(total_addr_in_addrs)
        total_out_address_train_dataset.extend(total_addr_out_addrs)

        dataset_train.append(rows)

        if len(dataset_train) % 100 == 0:
            pd_all_out = pd.DataFrame(dataset_train)
            pd_all_out.to_csv(train_test__all_file, index=None)
            print("generate all train test is ok by step! len {}".format(len(pd_all_out)))
    pd_all_out = pd.DataFrame(dataset_train)
    pd_all_out.to_csv(train_test__all_file, index=None)
    print("generate all train test is ok! len {}".format(len(pd_all_out)))


