import MetaTrader5 as Metatrader
import pandas as pd

login_id = 35820
pass_word = "FXpesaflanelegit2"
server_name = "EGMSecurities-Demo"
Metatrader.initialize(login=login_id, password=pass_word, server=server_name)
profit_margin = 3


def collect_data(currency, chart_timeframe, start_point, end_point):
    ticks = Metatrader.copy_rates_from_pos(currency, chart_timeframe, start_point, end_point)
    ticks_data = pd.DataFrame(ticks)
    ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
    ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
    ticks_data = ticks_data.set_index('time')

    return ticks_data


def candle_patterns(forex, chart_time, start_bar, end_bar):
    candle_data = collect_data(forex, chart_time, start_bar, end_bar)

    idx = candle_data.index.name
    candle_data.reset_index(inplace=True)

    candle_data['heikin close'] = (candle_data['open'] + candle_data['close'] + candle_data['low'] + candle_data[
        'high']) / 4

    for i in range(0, len(candle_data)):
        if i == 0:
            candle_data.loc[i, 'heikin open'] = (candle_data.loc[i, 'open'] + candle_data.loc[i, 'close']) / 2
        else:
            candle_data.loc[i, 'heikin open'] = (candle_data.loc[i - 1, 'heikin open'] + candle_data.loc[
                i - 1, 'heikin close']) / 2

    if idx:
        candle_data.set_index(idx, inplace=True)

    candle_data['heikin high'] = candle_data[['heikin close', 'heikin open', 'high']].max(axis=1)
    candle_data['heikin low'] = candle_data[['heikin close', 'heikin open', 'low']].min(axis=1)

    print(candle_data.tail(5))


candle_patterns("XAUUSD", Metatrader.TIMEFRAME_H1, 1, 10000)
