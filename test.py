import pandas as pd
import os
import sys
import datetime
import numpy as np

ROOT = os.path.abspath(os.path.split(sys.argv[0])[0])


if __name__ == '__main__':
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    dataset_file = os.path.join(ROOT, 'top1w_datasets_exchange_{}.csv'.format(today))
    df = pd.read_csv(dataset_file, nrows=2)
    for index, row in df.iterrows():
        print(row['Wallet'], row['all_in_addrs_count'], row[''])



    save_path = os.path.join(ROOT, 'top1w_richest_diff_{}.csv'.format(today))

    all_inputs_file = os.path.join(ROOT, 'top1w_datasets_exchange_inputs_{}.csv'.format(today))
    df_allinputs = pd.read_csv(all_inputs_file)

    all_out_file = os.path.join(ROOT, 'top1w_datasets_exchange_out_{}.csv'.format(today))
    df_allout = pd.read_csv(all_out_file)

    diff = np.intersect1d(df_allinputs.values, df_allout.values)

    df = pd.DataFrame(diff)
    df.to_csv(save_path, header=None)
    print("diff count is : {}".format(len(diff)))
