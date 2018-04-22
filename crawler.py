from bs4 import BeautifulSoup
import urllib.request

import collections
import pandas as pd
from time import sleep
import datetime
import os
import sys

ROOT = os.path.abspath(os.path.split(sys.argv[0])[0])
today = datetime.datetime.now().strftime("%Y-%m-%d")
wallet_count = 0
total = []

request_url = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses{}.html"

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'


def formatRow(ele):
    rel_soup = BeautifulSoup(ele, "lxml")
    tds = rel_soup.select('td')

    d1 = collections.OrderedDict()
    if len(tds) == 0 or len(tds[0]) == 0:
        return d1
    # log.debug("get row length : {}".format(len(tds)))

    d1['No'] = tds[0].text
    d1['Address'] = tds[1].text[0:34]
    balance = tds[2].text
    spans = tds[2].select('span')
    d1['Balance'] = balance.split('BTC')[0].replace(',', '')
    if len(spans) > 0:
        d1['WeekMonth'] = spans[0].text
        wm = spans[0].text.split("/")
        if len(wm) > 1:
            d1['Week'] = wm[0].replace("BTC", "").replace(" ", "")
            d1['Month'] = wm[1].replace("BTC", "").replace(" ", "")
        elif len(wm) == 1:
            d1['Week'] = wm[0].replace("BTC", "").replace(" ", "")
            d1['Month'] = ""
        else:
            d1['Week'] = ""
            d1['Month'] = ""
    else:
        d1['WeekMonth'] = ""
        d1['Week'] = ""
        d1['Month'] = ""
    # d1['BalanceUSD'] = re.search('($\w+ USD)', balance).group(0).replace(',', '')
    # if len(spans) > 2:
    #     d1['Balance1w'] = spans[0].text
    # if len(spans) > 1:
    #     d1['Balance1m'] = spans[1].text

    d1['PercentOfCoins'] = tds[3].text
    d1['FirstIn'] = tds[4].text
    d1['LastIn'] = tds[5].text
    d1['NumberOfIns'] = tds[6].text
    d1['FirstOut'] = tds[7].text
    d1['LastOut'] = tds[8].text

    d1['NumberOfOuts'] = tds[9].text

    wallet = rel_soup.select('small')
    if len(wallet) > 0:
        d1['Wallet'] = wallet[0].text
        global wallet_count
        wallet_count = wallet_count + 1
    else:
        d1['Wallet'] = ''
    return d1


def getPageContent(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': user_agent
    })
    response = urllib.request.urlopen(req)
    content = response.read().decode('utf-8')
    # log.debug(content)
    soup = BeautifulSoup(content, "lxml")
    items1 = soup.select('#tblOne tr')
    items2 = soup.select('#tblOne2 tr')
    n1 = 0
    n2 = 0
    length1 = len(items1)
    length2 = len(items2)
    # print("get length 1 and 2: {} {}".format(length1, length2))
    while n1 < length1:
        # log.debug(type(items1[n1]))
        # log.debug(str(items1[n1]))
        out = formatRow(str(items1[n1]))
        if len(out) > 5:
            total.append(out)
        # log.debug(out)
        # put to dict
        n1 += 1
    while n2 < length2:
        out = formatRow(str(items2[n2]))
        total.append(out)
        # put to dict
        n2 += 1


# get first

lastpage = 101
start = 1
for i in range(start, lastpage):
    if i == 1:
        get_url = request_url.format('')
    else:
        get_url = request_url.format("-{}".format(i))
    print("get page {} ".format(get_url))
    sleep(0.5)
    getPageContent(get_url)
    df = pd.DataFrame(total)
    save_path = os.path.join(ROOT, 'top1w_richest_{}.csv'.format(today))
    df.to_csv(save_path, index=None)

print("Total:{} Wallet: {} generate finished.".format(len(total), wallet_count))
