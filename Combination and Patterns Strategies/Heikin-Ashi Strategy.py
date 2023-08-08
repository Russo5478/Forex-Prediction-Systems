import MetaTrader5 as Metatrader
import pandas as pd

login_id = 0
pass_word = ""
server_name = ""
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
    candle_data['heikin close'] = (candle_data['open'] + candle_data['close'] + candle_data['low'] + candle_data['high'])/4

    idx = candle_data.index.name
    candle_data.reset_index(inplace=True)

    for i in range(0, len(candle_data)):
        if i == 0:
            candle_data._set_value(i, 'heikin open', ((candle_data._get_value(i, 'open') + candle_data._get_value(i, 'close'))/2))

        else:
            candle_data._set_value(i, 'heikin open', ((candle_data._get_value(i-1, 'heikin open') + candle_data._get_value(i-1, 'heikin close'))/2))

    if idx:
        candle_data.set_index(idx, inplace=True)

    candle_data['heikin high'] = candle_data[['heikin close', 'heikin open', 'high']].max(axis=1)
    candle_data['heikin low'] = candle_data[['heikin close', 'heikin open', 'low']].min(axis=1)

    current_body = abs(candle_data.iloc[-1]['heikin close'] - candle_data.iloc[-1]['heikin open'])
    previous1_body = abs(candle_data.iloc[-2]['heikin close'] - candle_data.iloc[-2]['heikin open'])
    previous2_body = abs(candle_data.iloc[-3]['heikin close'] - candle_data.iloc[-3]['heikin open'])

    if candle_data.iloc[-1]['heikin close'] > candle_data.iloc[-1]['heikin open'] and candle_data.iloc[-2]['heikin close'] > candle_data.iloc[-2]['heikin open'] and candle_data.iloc[-3]['heikin close'] < candle_data.iloc[-3]['heikin open'] and candle_data.iloc[-1]['heikin high'] > candle_data.iloc[-2]['heikin high'] and candle_data.iloc[-1]['heikin low'] > candle_data.iloc[-2]['heikin low'] and current_body > previous1_body:
        print("True buy")

    if candle_data.iloc[-1]['heikin open'] < candle_data.iloc[-1]['heikin close'] and candle_data.iloc[-2]['heikin open'] < candle_data.iloc[-2]['heikin close'] and candle_data.iloc[-1]['heikin high'] < candle_data.iloc[-2]['heikin high'] and candle_data.iloc[-1]['heikin low'] > candle_data.iloc[-2]['heikin low'] and candle_data.iloc[-1]['heikin close'] < candle_data.iloc[-2]['heikin close']:
        print("True sell")

    candle_data.to_csv('bol1.csv')


candle_patterns("USDCAD", Metatrader.TIMEFRAME_M5, 0, 100)
