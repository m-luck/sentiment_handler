import ast
import argparse
import arrow
import matplotlib.pyplot as plt
import quandl
import seaborn as sns
import sys
import yaml

from typing import List


def cmdline_args():
    '''
    Parse args.
    '''
    p = argparse.ArgumentParser(description="""
        This is a test of the command line argument parser in Python.
        """,
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument("property", help="news_volume")
    p.add_argument("ticker", help="news_volume")

    return(p.parse_args())


def prepare_quandl():
    '''
    Get settings, return tickers.
    '''
    with open('tickers.csv') as f, open('git_ignore_this.config') as q:
        tickers = [line.split(',')[0] for line in f]
        config = yaml.safe_load(q)
        quandl.ApiConfig.api_key = config['q']
    return tickers


def get_historical_avg_of_field(tic: str, field: str = 'news_volume', back_range: int = 56):
    '''
    Get avg of so many days.
    '''
    vals = []
    tot = 0
    for i in range(back_range+1, 1, -1):
        ptr = arrow.utcnow().shift(days=-i).format('YYYY-MM-DD')
        senti_data = quandl.get_table('IFT/NSA', date=ptr, ticker=tic).iloc[0]
        try:
            tot += senti_data[field]
            vals.append((ptr, senti_data[field]))
        except:
            print('Field is not in sentiment data row...')
    avg = tot / back_range
    return avg, vals


def get_diff_from_today(tic: str, subtractor, field: str = 'news_volume'):
    '''
    Get difference of passed in value from today.
    '''
    ptr = arrow.utcnow().shift(days=-1).format('YYYY-MM-DD')
    senti_data = quandl.get_table('IFT/NSA', date=ptr, ticker=tic).iloc[0]
    val = senti_data[field]
    print(val, '-', subtractor)
    res = val - subtractor

    return float(f'{res:0.2f}')


def plot_last_n_days(vals: List):
    x, y = zip(*vals)
    g = sns.barplot(x=x, y=y, ci=None)
    g.set(xlabel='Date', ylabel='Value')
    plt.xticks(rotation=45)
    plt.show()


if __name__ == '__main__':

    if sys.version_info < (3, 0, 0):
        sys.stderr.write("You need python 3.0 or later to run this script\n")
        sys.exit(1)
    try:
        args = cmdline_args()
    except:
        print('Try $python <script_name> news_volume')
    ticks = prepare_quandl()
    avg, vals = get_historical_avg_of_field(args.ticker, args.property, 10)
    diff = get_diff_from_today(args.ticker, avg, args.property)
    plot_last_n_days(vals)
