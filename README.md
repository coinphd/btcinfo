# 用机器学习算法对BTC地址进行分类

## 团队成员
Xinqi Yang, Yong Ren, Yang Lin, Zhenjiang YU

## 项目结构
```
├── README.md      说明文件
├── block-height   区块高度缓存
├── btcinfo_randomforest.model  模型文件
├── crawler.py     爬虫文件
├── dataset.py     数据集构建文件
├── randomforest.py 随机森林模型训练器
├── rawaddr         BTC地址缓存
├── rawblock        区块缓存
├── rawtx           交易缓存
├── requirements.txt  系统依赖文件
├── test.py           测试文件
├── top1w_datasets_exchange_2018-04-21.csv  抓取交易所数据文件（包含交易历史）
├── top1w_datasets_exchange_inputs_2018-04-21.csv 抓取交易所地址的inputs地址
├── top1w_datasets_exchange_out_2018-04-21.csv    抓取交易所地址的out地址
├── top1w_datasets_test.csv                       10条测试数据
├── top1w_exchange_datasets_2018-04-21.csv        TOP1万的BTC地址文件筛选出来的121标记为交易所钱包地址的文件
├── top1w_mixing_datasets_2018-04-21.csv          可能为混币服务地址数据
├── top1w_number_datasets_2018-04-21.csv          TOP1万的BTC地址文件筛选出来的数字编号的地址文件
├── top1w_others_datasets_2018-04-21.csv          其他类型的地址数据
├── top1w_richest_2018-04-21.csv                  爬虫文件抓取的TOP1万的BTC地址文件
├── top1w_richest_diff_2018-04-21.csv             交易所inputs,out地址的交集数据
├── top1w_train_test_all_datasets_2018-04-21.csv  包含全部特征的训练数据
└── top1w_train_test_datasets_2018-04-21.csv      包含地址及分类标签的训练数据
```
## 执行流程
### 安装系统依赖包：
本项目使用python3环境，请按照python3及以上版本，安装好之后安装pip3,之后安装系统依赖库
```bash
cd btcinfoo
pip3 install -r requirements.txt 
```

### 抓取Top1W的最富有用户地址
执行爬虫文件，抓取最富有的TOP1W用户地址，执行完成后生产 top1w_richest_2018-04-21.csv 某日期下的排名地址文件。
```bash
python3 crawler.py 
```
#### 爬虫实现：
使用urllib.request遍历100分页，获取网页html代码，之后使用 BeautifulSoup 解析网页dom树，获取需要数据，并使用pandas保存成csv文件。
如下： 
```
No,Address,Balance,WeekMonth,Week,Month,PercentOfCoins,FirstIn,LastIn,NumberOfIns,FirstOut,LastOut,NumberOfOuts,Wallet
1,3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r,187456 , -5598 BTC / -17.15 BTC,-5598,-17.15,1.10%,2017-01-05 12:34:15 UTC,2018-04-21 00:19:44 UTC,4795,2017-01-06 10:29:06 UTC,2018-04-18 01:29:35 UTC,4012,wallet: Bitfinex-coldwallet
2,16rCmCmbuWDhPjWTrpQGaU3EPdZF7MTdUk,137203 , / -22000 BTC,,-22000,0.8082%,2016-02-27 18:00:09 UTC,2018-04-20 19:11:16 UTC,138,2016-11-16 20:50:07 UTC,2018-04-12 14:51:36 UTC,54,wallet: Bittrex-coldwallet
3,3Nxwenay9Z8Lc9JBiywExpnEFiLp6Afp8v,103848 , +4000 BTC / +14000 BTC,+4000,+14000,0.6117%,2015-10-16 14:43:06 UTC,2018-04-20 15:12:54 UTC,179,2015-10-29 10:44:26 UTC,2018-03-05 13:05:46 UTC,54,wallet: Bitstamp-coldwallet
```

### 构建训练数据集
执行构建训练数据集文件,生成 top1w_exchange_datasets_2018-04-21.csv , top1w_mixing_datasets_2018-04-21.csv, top1w_number_datasets_2018-04-21.csv, top1w_others_datasets_2018-04-21.csv 4种类型地址数据。
根据4种地址数据合并并安装类型打上标签，获取详细交易数据后生成训练数据。


#### 获取已经标注交易所钱包地址
根据抓取TOP1W用户地址，根据Wallet标签，获取交易所钱包地址列表：
通过top1w_richest_2018-04-21.csv中获取已经标注好交易所地址的数据存成top1w_exchange_datasets_2018-04-21.csv，总共121条
```
No,Address,Balance,WeekMonth,Week,Month,PercentOfCoins,FirstIn,LastIn,NumberOfIns,FirstOut,LastOut,NumberOfOuts,Wallet
5,16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe,99947.0,0,0.0,0.0,0.5887%,2017-12-08 07:51:10 UTC,2018-04-09 08:00:58 UTC,100,2017-12-10 16:55:29 UTC,2018-02-08 19:57:52 UTC,56.0,wallet: Binance-wallet
30,1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s,31525.0, -10556 BTC / -20284 BTC,-10556.0,-20284.0,0.1857%,2017-08-08 10:32:55 UTC,2018-04-21 00:19:44 UTC,138743,2017-08-08 11:57:36 UTC,2018-04-21 00:19:44 UTC,121241.0,wallet: Binance-wallet
1789,19PkHafEN18mquJ9ChwZt5YEFoCdPP5vYB,946.32,0,0.0,0.0,0.005574155359071%,2011-11-07 13:44:47 UTC,2018-04-18 23:18:02 UTC,6488,2011-11-08 08:48:03 UTC,2018-04-20 19:26:04 UTC,6444.0,wallet: BitMinter.com
1002,17ac9tXHxu1nxdLgLu9WYk7vR8ggFN5GkH,1400.0,0,0.0,0.0,0.0082485495608837%,2017-11-23 15:25:09 UTC,2018-04-20 15:12:54 UTC,912,2017-11-24 06:00:04 UTC,2018-04-20 15:12:54 UTC,892.0,wallet: BitX.co
7323,1E3DT3nSNWKx378mkPCiCFig4xSg9Q6Pw4,203.55,0,0.0,0.0,0.0011989660437195%,2016-12-16 08:01:37 UTC,2018-04-18 15:41:27 UTC,426,2016-12-20 15:34:09 UTC,2018-04-16 10:08:19 UTC,420.0,wallet: BitX.co
```

#### 根据交易所钱包地址获取交易所用户地址及大户(Whale)地址
根据121个已标记的交易所地址，通过遍历地址的transactions交易记录，获取inputs打入交易所的地址信息，及交易所打出的地址信息
交易所打入地址规则， 打入交易所钱包地址的都属于交易所用户地址
大户地址规则， 交易所打出到个人地址，每次>5个币的定义为大户地址

#### 获取混币服务地址及其他用户others用户地址
获取最后一个区块，根据区块的交易记录，筛选转入地址 大于 10 个以上的地址，并且不在白名单中（交易所地址，交易所用户地址，大户用户地址），定位为混币地址。
当转入地址小于0.5的，并且不属于 以上3中地址中的，定义为其他地址

Note:特征工程中花费的时间最多

#### 使用pickle.dump缓存区块信息
访问的requests中每次将返回数据存储成文件，调试时候，减少网络开销，加快交易信息读取速度。


```
python3 dataset.py
```

生成： 
top1w_exchange_datasets_2018-04-21.csv      
top1w_mixing_datasets_2018-04-21.csv       
top1w_number_datasets_2018-04-21.csv      
top1w_others_datasets_2018-04-21.csv       

生成带标签训练数据：  
top1w_train_test_datasets_2018-04-21.csv 打好标签： 1 exchange交易所, 2 whale 大户， 3 mixer 混币地址， 4 others其他地址

```
Address,0_label
112AMaD8ovAk3GZsVRUJwz2ScLF7xoFhdf,1
3FiiNJNwbwcubMTW6QcPpnoyVoB12WfLLd,2
16LuR5F4nmJKwTzropWbdBuXpDL2gvwEKc,3
1754wG24CBTtqxGoQuGDhApMSjRTwrZCHe,4
```
生成详细特征训练数据：
top1w_train_test_all_datasets_2018-04-21.csv 这个数据用于训练模型
```
Address,0_label,n_tx,total_received,total_sent,final_balance,all_in_addrs_count,all_out_addrs_count
3CdL3fQdseso4h5Yfg7SqjYnNA5AzMqRUr,4,162,1.3,1.2,0.1,0,0
15RgpQUiJrYTdxCVgpQvyjSNaQzvfiUucv,4,14,6.51,6.51,0.0,10,7
17f5MeFyL9LALB5ATs3Ppkoh3KosTDnEbX,2,2,14.43,14.43,0.0,1,1
```

### 训练模型
执行,开始训练模型
```
python3 randomforest.py
```
执行过程， 读取训练数据，构造数据集X，Y，使用RandomForestClassifier 随机森林分类器生成模型，保存，并输出模型评分。
之后调用测试用例， top1w_datasets_test.csv， 对模型进行验证，输出Accuracy精确度和执行时间Time。

#### 模型调优
通过挑战n_estimators=10参数来定义不同数量的树来不段优化结果。

```
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
```

执行结果日志：
```
➜  btcinfo git:(master) ✗ python3 randomforest.py
====== Training ======
read datasets /git/btcinfo/top1w_train_test_all_datasets_2018-04-21.csv
['n_tx', 'total_received', 'total_sent', 'final_balance', 'all_in_addrs_count', 'all_out_addrs_count']
get dataset count: 1800
feature matrix shape:  (1800, 6)
label matrix shape:  (1800,)
====== data shape ======
X:
[[-0.0761847  -0.05413812 -0.05353206 -0.06651113 -0.30768165 -0.16509111]
 [-0.08588238 -0.05377133 -0.0531582  -0.06727708 -0.2612613  -0.12847587]
 [-0.08666869 -0.05321376 -0.05260057 -0.06727708 -0.3030396  -0.15986036]
 [-0.08601343 -0.05419514 -0.05358205 -0.06727708 -0.14056848 -0.14416812]
 [-0.08535818 -0.05422964 -0.05361655 -0.06727708 -0.30768165 -0.16509111]]
Y:
[4 4 2 3 4]
training model success, save to path: btcinfo_randomforest.model and validate score is:
[0.74033149 0.75690608 0.72928177 0.74033149 0.71823204 0.74033149
 0.75       0.77653631 0.78651685 0.78531073]
====== Tests ======
read test /git/btcinfo/top1w_datasets_test.csv, len 10
==== Address predict ===
[4 1 1 1 1 4 1 1 2 4]
Address: 1PizJisvgNy37yKzpmpDf2vWPzaPezRbV Result:    OK Predict: others Label: others
Address: 1Mm6ZHtR1XNmybNyYH2o7MjnV9K6BCjBLX Result:    OK Predict: exchange Label: exchange
Address: 3GYv9iJohGibG2S6Mwfqrj4jhwo3fynZFH Result: ERROR Predict: exchange Label: mixer
Address: 36AwqvsZ4RjTnJwHrmKUvKyivajkZq3XUi Result:    OK Predict: exchange Label: exchange
Address: 3BheihB1B81wpYAobPVCwXrozVDENJQhbL Result: ERROR Predict: exchange Label: mixer
Address: 15ke6Ba2kmVsk3hi9Ho4g4e4y2WdnoFcQD Result:    OK Predict: others Label: others
Address: 1GpEkDCwtbqLWkL4F1uiSbMDiWdNorpZrJ Result:    OK Predict: exchange Label: exchange
Address: 1JoN6DoV7dHyxDSoyxZKYCz6ExhVpxxPDX Result: ERROR Predict: exchange Label: whale
Address: 3Bera5tY2arQccYaecDY2ovtMA5XJqhwAq Result:    OK Predict: whale Label: whale
Address: 3FJGTdkPYJme1x8jMckNWWHyoDuc42sisZ Result:    OK Predict: others Label: others
timstamp: 1524328565.09844 ~ 1524328565.1425102
Accuracy: 70.0%  Time: 4.41ms
```

