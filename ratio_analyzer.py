import ast
import sys
import statistics as st
import seaborn as sns
import quandl
import matplotlib.pyplot as plt

with open('ratio_table.dictionary') as rat, open('ticker_industries.dictionary') as tic, open('sec2tic.dictionary') as sec:
    rat = ast.literal_eval(rat.read())
    tic2sec = ast.literal_eval(tic.read())
    sec2tic = ast.literal_eval(sec.read())

if len(sys.argv) > 3:
    target_ticker = sys.argv[3]
numer = sys.argv[1]
denom = sys.argv[2]


def generate_sec_to_tics(tic2sec):
    sec2tic = {}
    for key, val in tic2sec.items():
        if val in sec2tic:
            sec2tic[val][key] = True
        else:
            sec2tic[val] = {key: True}
    with open('sec2tic.dictionary', 'w+') as w:
        w.write(str(sec2tic))
    return sec2tic


def get_avg_per_sector(sector, sec2tic, date='2019-08-06', numer='news_volume', denom='trade_volume'):
    num_tot, den_tot = 0, 0
    data = []
    for tic, _ in sec2tic[sector].items():
        name = tic+'_'+date
        if name in rat:
            ratio = rat[name]['ratio']
            if ratio != 1.0:
                num_tot += rat[name][numer]
                den_tot += rat[name][denom]
                data.append(num_tot / den_tot)
    avg = num_tot / den_tot if den_tot > 0 else 0
    std = st.stdev(data) if data else 0
    return avg, std


def get_ticker_ratio(ticker, rat, date='2019-08-06', numer='news_volume', denom='trade_volume'):
    name = ticker+'_'+date
    ratio = rat[name]['ratio'] if name in rat else 1
    return ratio


def get_stdev_from_avg(target_ticker):
    targ_sector = tic2sec[target_ticker]
    # print('---')
    # print(f'Targeting {target_ticker}:')
    # print(f'{target_ticker} is from {targ_sector}')
    avg, std = get_avg_per_sector(targ_sector, sec2tic)
    # print(f'The average and stdev of {numer} to {denom} ratio of {targ_sector} is {avg} and {std}')
    ratio = get_ticker_ratio(target_ticker, rat)
    if ratio != 1.0:
        # print(f'The ratio for {target_ticker} is {ratio}')
        z = (ratio - avg) / std if std != 0 else 0
        # print(f'This is {z} std from the average.')
    else:
        # print(f'One of the fields for {target_ticker} is missing, so cannot be calculated.')
        z = 0
    return z


def get_stdevs_for_all_tickers(tic2sec):
    stdevs = []
    for ticker, _ in tic2sec.items():
        stdev = get_stdev_from_avg(ticker)
        stdevs.append((stdev, ticker))
    stdevs.sort(key=lambda tup: tup[0], reverse=True)
    return stdevs


def generate_top_news_to_volume_file():
    stdevs = get_stdevs_for_all_tickers(tic2sec)
    with open('stdevs.list', 'w+') as w:
        # print(stdevs)
        w.write(str(stdevs))


def plot_top_stdev_tickers(n):
    with open('stdevs.list') as f:
        stdevs = ast.literal_eval(f.read())
    y, x = zip(*stdevs)
    y, x = list(y)[:n], list(x)[:n]
    g = sns.barplot(x=x, y=y, ci=None)
    g.set(xlabel='Tickers', ylabel='St.D within own Sector')
    plt.xticks(rotation=45)
    plt.show()

plot_top_stdev_tickers(25)
