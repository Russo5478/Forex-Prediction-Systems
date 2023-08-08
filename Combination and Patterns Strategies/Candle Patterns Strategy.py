import time

import MetaTrader5 as Metatrader
import pandas as pd
from datetime import datetime
from WaitingTime import timing
import multiprocessing
from trade import initiate_trade

login_id = 0
pass_word = ""
server_name = ""
Metatrader.initialize(login=login_id, password=pass_word, server=server_name)
profit_margin = 3


def bollinger_bands(stock_symbol, chart_time, starting_point, bars_back):
    # Useful variables
    standard_deviation = 2
    period = 20

    # Getting the right time to trade
    try:
        tick_information = Metatrader.symbol_info_tick(stock_symbol)
        tick_time = str(datetime.fromtimestamp(tick_information[0]))
        timing(current_time=tick_time, chart_timeframe=chart_time)

    except TypeError:
        pass

    # Get number of points and spread
    def decimal_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            total = profit_margin * 0.001
            return total

        else:
            total = profit_margin * 0.00001
            return total

    def stop_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.001) + (profit_margin * 0.001)
            return total

        else:
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.00001) + (profit_margin * 0.00001)
            return total

    def collect_ticks():
        ticks = Metatrader.copy_rates_from_pos(stock_symbol, chart_time, starting_point, bars_back)
        ticks_data = pd.DataFrame(ticks)
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
        ticks_data = ticks_data.set_index('time')

        return ticks_data

    data = collect_ticks()
    data['ema'] = data['close'].rolling(5).mean()
    data['simple moving average'] = data['close'].rolling(period).mean()
    data['std'] = data['close'].rolling(period).std()
    data['upper_band'] = data['simple moving average'] + (standard_deviation * data['std'])
    data['lower_band'] = data['simple moving average'] - (standard_deviation * data['std'])

    # First check for the basic trade signals:
    if data.iloc[-2]['close'] < data.iloc[-2]['lower_band'] and data.iloc[-1]['close'] > data.iloc[-1]['lower_band']:
        # Buy Signal
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())

    elif data.iloc[-2]['close'] > data.iloc[-2]['upper_band'] and data.iloc[-1]['close'] < data.iloc[-1]['upper_band']:
        # Sell Signal
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bollinger Buy for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())

    else:
        time.sleep(10)
        bollinger_bands(stock_symbol, chart_time, starting_point, bars_back)


def candle_pattern1(stock_symbol, chart_time, starting_point, bars_back):
    # Getting the right time to trade
    try:
        tick_information = Metatrader.symbol_info_tick(stock_symbol)
        tick_time = str(datetime.fromtimestamp(tick_information[0]))
        timing(current_time=tick_time, chart_timeframe=chart_time)

    except TypeError:
        pass

    # Get number of points and spread
    def decimal_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            total = profit_margin * 0.001
            return total

        else:
            total = profit_margin * 0.00001
            return total

    def stop_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.001) + (profit_margin * 0.001)
            return total

        else:
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.00001) + (profit_margin * 0.00001)
            return total

    def collect_ticks():
        ticks = Metatrader.copy_rates_from_pos(stock_symbol, chart_time, starting_point, bars_back)
        ticks_data = pd.DataFrame(ticks)
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
        ticks_data = ticks_data.set_index('time')

        return ticks_data

    data = collect_ticks()
    for i in range(2, data.shape[0]):
        current = data.iloc[i, :]
        previous_1 = data.iloc[i - 1, :]
        previous_2 = data.iloc[i - 2, :]

        real_body = abs(current['open'] - current['close'])
        candle_range = current['high'] - current['low']
        idx = data.index[i]

        # Bullish swing
        data.loc[idx, 'Bullish swing'] = current['low'] > previous_1['low'] and previous_1['low'] < previous_2[
            'low'] and previous_1['high'] < current['high'] and \
                                         previous_1['high'] < previous_2['high'] <= current['high'] and current['low'] > \
                                         previous_2['low']

        # Bearish swing
        data.loc[idx, 'Bearish swing'] = current['high'] < previous_1['high'] and previous_1['high'] > previous_2[
            'high'] and previous_1['low'] > previous_2['low'] and previous_1['low'] > current['low'] and current[
                                             'high'] <= previous_2['high'] and current['low'] < previous_2['low']

        # Bullish pinbar
        data.loc[idx, 'Bullish pinbar'] = real_body <= candle_range / 3 and min(current['open'], current['close']) > (
                current['high'] + current['low']) / 2 and previous_1['low'] > current['low'] and current['high'] < \
                                          previous_1['high']

        # Bearish pinbar
        data.loc[idx, 'Bearish pinbar'] = real_body <= candle_range / 3 and max(current['open'], current['close']) < (
                current['high'] + current['low']) / 2 and previous_1['high'] < current['high'] and current['low'] > \
                                          previous_1['low']

        # Bullish engulfing
        data.loc[idx, 'Bullish engulfing'] = current['high'] > previous_1['high'] and current['low'] < previous_1[
            'low'] and real_body >= 0.8 * candle_range and current['close'] > current['open']

        # Bearish engulfing
        data.loc[idx, 'Bearish engulfing'] = current['high'] > previous_1['high'] and current['low'] < previous_1[
            'low'] and real_body >= 0.8 * candle_range and current['close'] < current['open']
    data.fillna(False, inplace=True)

    if str(data.iloc[-1]['Bullish swing']).upper() == "TRUE":
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish swing for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)

    if str(data.iloc[-1]['Bearish swing']).upper() == "TRUE":
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish swing for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)

    if str(data.iloc[-1]['Bullish pinbar']).upper() == "TRUE":
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish pinbar for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)

    if str(data.iloc[-1]['Bearish pinbar']).upper() == "TRUE":
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish pinbar for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)

    if str(data.iloc[-1]['Bullish engulfing']).upper() == "TRUE":
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish engulfing for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)

    if str(data.iloc[-1]['Bearish engulfing']).upper() == "TRUE":
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish engulfing for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern1(stock_symbol, chart_time, starting_point, bars_back)


def candle_pattern2(stock_symbol, chart_time, starting_point, bars_back):
    # Useful variables
    standard_deviation = 2
    period = 20

    # Getting the right time to trade
    try:
        tick_information = Metatrader.symbol_info_tick(stock_symbol)
        tick_time = str(datetime.fromtimestamp(tick_information[0]))
        timing(current_time=tick_time, chart_timeframe=chart_time)

    except TypeError:
        pass

    # Get number of points and spread
    def decimal_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            total = profit_margin * 0.001
            return total

        else:
            total = profit_margin * 0.00001
            return total

    def stop_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.001) + (profit_margin * 0.001)
            return total

        else:
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.00001) + (profit_margin * 0.00001)
            return total

    def collect_ticks():
        ticks = Metatrader.copy_rates_from_pos(stock_symbol, chart_time, starting_point, bars_back)
        ticks_data = pd.DataFrame(ticks)
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
        ticks_data = ticks_data.set_index('time')

        return ticks_data

    def percent(val):
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            total = val * 1000
            return total

        else:
            total = val * 100000
            return total

    data = collect_ticks()
    data['ema'] = data['close'].rolling(5).mean()
    data['simple moving average'] = data['close'].rolling(period).mean()
    data['std'] = data['close'].rolling(period).std()
    data['upper_band'] = data['simple moving average'] + (standard_deviation * data['std'])
    data['lower_band'] = data['simple moving average'] - (standard_deviation * data['std'])
    current = data.iloc[-1]['close']
    previous = data.iloc[-2]['close']
    percentage = abs((current - previous) / (current + previous)) * 100
    figure = percent(percentage)
    print(figure)

    if data.iloc[-1]['close'] > data.iloc[-1]['simple moving average'] > data.iloc[-1]['low'] and data.iloc[-1][
        'high'] > data.iloc[-1]['simple moving average'] > data.iloc[-1]['open'] and data.iloc[-2]['high'] < \
            data.iloc[-2]['simple moving average'] and data.iloc[-2]['low'] < data.iloc[-1][
        'simple moving average'] and figure >= 40:
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "SMA Pattern Buy for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())

    elif data.iloc[-1]['close'] < data.iloc[-1]['simple moving average'] < data.iloc[-1]['low'] and data.iloc[-1][
        'high'] < data.iloc[-1]['simple moving average'] < data.iloc[-1]['open'] and data.iloc[-2]['high'] > \
            data.iloc[-2]['simple moving average'] and data.iloc[-2]['low'] > data.iloc[-1][
        'simple moving average'] and figure >= 40:
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "SMA Pattern Sell for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())

    else:
        time.sleep(10)
        candle_pattern2(stock_symbol, chart_time, starting_point, bars_back)


def candle_pattern3(stock_symbol, chart_time, starting_point, bars_back):
    # Useful variables
    standard_deviation = 2
    period = 20

    # Getting the right time to trade
    try:
        tick_information = Metatrader.symbol_info_tick(stock_symbol)
        tick_time = str(datetime.fromtimestamp(tick_information[0]))
        timing(current_time=tick_time, chart_timeframe=chart_time)

    except TypeError:
        pass

    # Get number of points and spread
    def decimal_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            total = profit_margin * 0.001
            return total

        else:
            total = profit_margin * 0.00001
            return total

    def stop_counter():
        points = Metatrader.symbol_info(stock_symbol).point

        if str(points) == '0.001':
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.001) + (profit_margin * 0.001)
            return total

        else:
            spread = Metatrader.symbol_info(stock_symbol)[12]
            total = (spread * 0.00001) + (profit_margin * 0.00001)
            return total

    def collect_ticks():
        ticks = Metatrader.copy_rates_from_pos(stock_symbol, chart_time, starting_point, bars_back)
        ticks_data = pd.DataFrame(ticks)
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
        ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
        ticks_data = ticks_data.set_index('time')

        return ticks_data

    data = collect_ticks()
    data['ema'] = data['close'].rolling(5).mean()
    data['simple moving average'] = data['close'].rolling(period).mean()
    data['std'] = data['close'].rolling(period).std()
    data['upper_band'] = data['simple moving average'] + (standard_deviation * data['std'])
    data['lower_band'] = data['simple moving average'] - (standard_deviation * data['std'])

    if data.iloc[-1]['high'] > data.iloc[-1]['simple moving average'] > data.iloc[-1]['low'] and data.iloc[-1][
        'close'] > data.iloc[-1]['simple moving average'] > data.iloc[-1]['open'] and data.iloc[-2]['high'] > data.iloc[-2]['simple moving average'] and data.iloc[-2]['open'] > data.iloc[-2]['simple moving average'] and data.iloc[-2]['low'] < data.iloc[-2]['simple moving average']and data.iloc[-2]['close'] < data.iloc[-2]['simple moving average'] and data.iloc[-1]['high'] > data.iloc[-2]['high'] and data.iloc[-1]['low'] >= data.iloc[-2]['low']:
        sl = min(data.iloc[-2]['low'], data.iloc[-3]['low'], data.iloc[-4]['low'], data.iloc[-5]['low'],
                 data.iloc[-6]['low'], data.iloc[-1]['low'])
        stop_losses = sl - stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Candle Pattern 3 BUY for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "buy", stop_losses, decimal_counter())
        time.sleep(10)

    elif data.iloc[-1]['high'] > data.iloc[-1]['simple moving average'] > data.iloc[-1]['low'] and data.iloc[-1][
        'close'] < data.iloc[-1]['simple moving average'] < data.iloc[-1]['open'] and data.iloc[-2]['high'] > \
            data.iloc[-2]['simple moving average'] > data.iloc[-2]['open'] and data.iloc[-2]['low'] < data.iloc[-2]['simple moving average']and data.iloc[-2]['close'] > data.iloc[-2]['simple moving average'] and data.iloc[-1]['high'] <= data.iloc[-2]['high'] and data.iloc[-1]['low'] < data.iloc[-2]['low']:
        sl = max(data.iloc[-2]['high'], data.iloc[-3]['high'], data.iloc[-4]['high'], data.iloc[-5]['high'],
                 data.iloc[-6]['high'], data.iloc[-1]['high'])
        stop_losses = sl + stop_counter()
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Candle Pattern 3 SELL for", stock_symbol, "at", chart_time)
        initiate_trade(stock_symbol, "sell", stop_losses, decimal_counter())
        time.sleep(10)

    else:
        time.sleep(10)
        candle_pattern2(stock_symbol, chart_time, starting_point, bars_back)


if __name__ == '__main__':
    try:
        # Bollinger Bands-------------------------------------------------------------------------------------------
        START = 0
        BARS = 100
        # AUDUSD
        audusd15 = multiprocessing.Process(target=bollinger_bands,
                                           args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        audusd30 = multiprocessing.Process(target=bollinger_bands,
                                           args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # EURUSD
        eurusd15 = multiprocessing.Process(target=bollinger_bands,
                                           args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        eurusd30 = multiprocessing.Process(target=bollinger_bands,
                                           args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDJPY
        usdjpy15 = multiprocessing.Process(target=bollinger_bands,
                                           args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        usdjpy30 = multiprocessing.Process(target=bollinger_bands,
                                           args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDCAD
        usdcad15 = multiprocessing.Process(target=bollinger_bands,
                                           args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        usdcad30 = multiprocessing.Process(target=bollinger_bands,
                                           args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

        # GBPUSD
        gbpusd15 = multiprocessing.Process(target=bollinger_bands,
                                           args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        gbpusd30 = multiprocessing.Process(target=bollinger_bands,
                                           args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # Candle Pattern----------------------------------------------------------------------------------------------
        audusd_5_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("AUDUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        audusd_15_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        audusd_30_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # EURUSD
        eurusd_5_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("EURUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        eurusd_15_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        eurusd_30_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDJPY
        usdjpy_5_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("USDJPY", Metatrader.TIMEFRAME_M5, START, BARS))
        usdjpy_15_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        usdjpy_30_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDCAD
        usdcad_5_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("USDCAD", Metatrader.TIMEFRAME_M5, START, BARS))
        usdcad_15_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        usdcad_30_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

        # GBPUSD
        gbpusd_5_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("GBPUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        gbpusd_15_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        gbpusd_30_candle1 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # Candle Pattern Two 2-----------------------------------------------------------------------------------------
        audusd_5_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("AUDUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        audusd_15_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        audusd_30_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # EURUSD
        eurusd_5_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("EURUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        eurusd_15_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        eurusd_30_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDJPY
        usdjpy_5_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("USDJPY", Metatrader.TIMEFRAME_M5, START, BARS))
        usdjpy_15_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        usdjpy_30_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDCAD
        usdcad_5_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("USDCAD", Metatrader.TIMEFRAME_M5, START, BARS))
        usdcad_15_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        usdcad_30_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

        # GBPUSD
        gbpusd_5_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                   args=("GBPUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        gbpusd_15_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        gbpusd_30_candle2 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # Candle Pattern Three 3-----------------------------------------------------------------------------------------
        audusd_15_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        audusd_30_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # EURUSD
        eurusd_15_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        eurusd_30_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDJPY
        usdjpy_15_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        usdjpy_30_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

        # USDCAD
        usdcad_15_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        usdcad_30_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

        # GBPUSD
        gbpusd_15_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        gbpusd_30_candle3 = multiprocessing.Process(target=candle_pattern1,
                                                    args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        audusd_5_candle1.start()
        audusd_15_candle1.start()
        audusd_30_candle1.start()

        eurusd_5_candle1.start()
        eurusd_15_candle1.start()
        eurusd_30_candle1.start()

        usdjpy_5_candle1.start()
        usdjpy_15_candle1.start()
        usdjpy_30_candle1.start()

        usdcad_5_candle1.start()
        usdcad_15_candle1.start()
        usdcad_30_candle1.start()

        gbpusd_5_candle1.start()
        gbpusd_15_candle1.start()
        gbpusd_30_candle1.start()

        audusd_5_candle2.start()
        audusd_15_candle2.start()
        audusd_30_candle2.start()

        eurusd_5_candle2.start()
        eurusd_15_candle2.start()
        eurusd_30_candle2.start()

        usdjpy_5_candle2.start()
        usdjpy_15_candle2.start()
        usdjpy_30_candle2.start()

        usdcad_5_candle2.start()
        usdcad_15_candle2.start()
        usdcad_30_candle2.start()

        gbpusd_5_candle2.start()
        gbpusd_15_candle2.start()
        gbpusd_30_candle2.start()

        audusd_15_candle3.start()
        audusd_30_candle3.start()

        eurusd_15_candle3.start()
        eurusd_30_candle3.start()

        usdjpy_15_candle3.start()
        usdjpy_30_candle3.start()

        usdcad_15_candle3.start()
        usdcad_30_candle3.start()

        gbpusd_15_candle3.start()
        gbpusd_30_candle3.start()

        audusd15.start()
        audusd30.start()

        eurusd15.start()
        eurusd30.start()

        usdjpy15.start()
        usdjpy30.start()

        usdcad15.start()
        usdcad30.start()

        gbpusd15.start()
        gbpusd30.start()

    except KeyboardInterrupt:
        Metatrader.shutdown()
        exit()
