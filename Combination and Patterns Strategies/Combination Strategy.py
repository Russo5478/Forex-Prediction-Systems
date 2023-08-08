import time
import multiprocessing
import MetaTrader5 as Metatrader
import pandas as pd
from datetime import datetime

login_id = 0
pass_word = ""
server_name = ""
Metatrader.initialize(login=login_id, password=pass_word, server=server_name)
profit_margin = 3


def place_order(symbol_type, trade_type, stop, pips):
    if trade_type.lower() == "buy":
        volume = 0.5
        price = Metatrader.symbol_info_tick(symbol_type).ask
        take_profit = price + pips + pips

        send_request = {"action": Metatrader.TRADE_ACTION_PENDING,
                        "symbol": symbol_type,
                        "volume": volume,
                        "type": Metatrader.ORDER_TYPE_BUY_STOP,
                        "price": price + pips,
                        "sl": stop,
                        "tp": take_profit,
                        "type_time": Metatrader.ORDER_TIME_GTC,
                        "type_filling": Metatrader.ORDER_FILLING_IOC}
        result = Metatrader.order_send(send_request)
        print(result)

    elif trade_type.lower() == "sell":
        volume = 0.5
        price = Metatrader.symbol_info_tick(symbol_type).bid
        take_profit = price - pips - pips

        send_request = {"action": Metatrader.TRADE_ACTION_PENDING,
                        "symbol": symbol_type,
                        "volume": volume,
                        "type": Metatrader.ORDER_TYPE_SELL_STOP,
                        "price": price - pips,
                        "sl": stop,
                        "tp": take_profit,
                        "type_time": Metatrader.ORDER_TIME_GTC,
                        "type_filling": Metatrader.ORDER_FILLING_IOC}
        result = Metatrader.order_send(send_request)
        print(result)


def number_of_pips(stock_symbol):
    point = Metatrader.symbol_info(stock_symbol).point

    if str(point) == '0.001':
        pips = profit_margin * 0.001
        return pips

    else:
        pips = profit_margin * 0.00001
        return pips


def stop_loss(stock_symbol):
    points = Metatrader.symbol_info(stock_symbol).point

    if str(points) == '0.001':
        spread = Metatrader.symbol_info(stock_symbol)[12]
        total = (spread * 0.001) + (profit_margin * 0.001)
        return total

    else:
        spread = Metatrader.symbol_info(stock_symbol)[12]
        total = (spread * 0.00001) + (profit_margin * 0.00001)
        return total


def timing_trade(stock_symbol, chart_frame):
    try:
        minute_5 = [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600]
        minute_6 = [0, 360, 720, 1080, 1440, 1800, 2160, 2520, 2880, 3240, 3600]
        minute_10 = [0, 600, 1200, 1800, 2400, 3000, 3600]
        minute_12 = [0, 720, 1440, 2160, 2880, 3600]
        minute_15 = [0, 900, 1800, 2700, 3600]
        minute_20 = [0, 1200, 2400, 3600]
        minute_30 = [0, 1800, 3600]
        one_hour = [0, 3600]
        optimal_time = 5
        tick_information = Metatrader.symbol_info_tick(stock_symbol)
        tick_time = str(datetime.fromtimestamp(tick_information[0]))

        if int(chart_frame) == 5:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_5) + 1):
                if total_seconds <= minute_5[i]:
                    time_left = minute_5[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 6:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_6) + 1):
                if total_seconds <= minute_6[i]:
                    time_left = minute_6[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 10:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_10) + 1):
                if total_seconds <= minute_10[i]:
                    time_left = minute_10[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 12:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_12) + 1):
                if total_seconds <= minute_12[i]:
                    time_left = minute_12[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 15:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_15) + 1):
                if total_seconds <= minute_15[i]:
                    time_left = minute_15[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 20:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_20) + 1):
                if total_seconds <= minute_20[i]:
                    time_left = minute_20[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 30:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(minute_30) + 1):
                if total_seconds <= minute_30[i]:
                    time_left = minute_30[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

        elif int(chart_frame) == 60:
            time_minute = tick_time[-5] + tick_time[-4]
            time_seconds = tick_time[-2] + tick_time[-1]
            total_seconds = (int(time_minute) * 60) + int(time_seconds)

            for i in range(0, len(one_hour) + 1):
                if total_seconds <= one_hour[i]:
                    time_left = one_hour[i] - total_seconds - optimal_time
                    if time_left >= 4:
                        print("[-] Waiting for", time_left, "secs")
                        time.sleep(time_left)
                        break

                    else:
                        time.sleep(6)

    except TypeError:
        pass

def collect_data(currency, chart_timeframe, start_point, end_point):
    ticks = Metatrader.copy_rates_from_pos(currency, chart_timeframe, start_point, end_point)
    ticks_data = pd.DataFrame(ticks)
    ticks_data['time'] = pd.to_datetime(ticks_data['time'], unit='s')
    ticks_data['time'] = pd.to_datetime(ticks_data['time'], format='%Y-%m-%d')
    ticks_data = ticks_data.set_index('time')

    return ticks_data


def williams_fractals_strategy(forex, chart_time, start_bar, end_bar):
    frct = 15
    period = 200
    timing_trade(stock_symbol=forex, chart_frame=chart_time)

    william_data = collect_data(forex, chart_time, start_bar, end_bar)
    william_data['ema'] = william_data['close'].ewm(span=period).mean()

    for i in range(1, frct):
        if william_data.iloc[frct - i]['high'] < william_data.iloc[frct]['high']:
            pass


def bollinger_only_strategy(forex, chart_time, start_bar, end_bar):
    try:
        standard_deviation = 2
        period = 20
        ema = 200
        timing_trade(stock_symbol=forex, chart_frame=chart_time)

        def multi_chart(val):
            if val == Metatrader.TIMEFRAME_M5:
                return Metatrader.TIMEFRAME_M10

            elif val == Metatrader.TIMEFRAME_M6:
                return Metatrader.TIMEFRAME_M12

            elif val == Metatrader.TIMEFRAME_M10:
                return Metatrader.TIMEFRAME_M20

            elif val == Metatrader.TIMEFRAME_M12:
                return Metatrader.TIMEFRAME_M30

            elif val == Metatrader.TIMEFRAME_M15:
                return Metatrader.TIMEFRAME_M30

            elif val == Metatrader.TIMEFRAME_M20:
                return Metatrader.TIMEFRAME_H1

            elif val == Metatrader.TIMEFRAME_M30:
                return Metatrader.TIMEFRAME_H1

        twice_time = multi_chart(chart_time)
        print(chart_time, twice_time)

        bollinger_data = collect_data(forex, chart_time, start_bar, end_bar)

        bollinger_data['SMA'] = bollinger_data['close'].rolling(period).mean()
        bollinger_data['STD'] = bollinger_data['close'].rolling(period).std()
        bollinger_data['UPPER'] = bollinger_data['SMA'] + (standard_deviation * bollinger_data['STD'])
        bollinger_data['LOWER'] = bollinger_data['SMA'] - (standard_deviation * bollinger_data['STD'])

        bollinger_data['ema'] = bollinger_data['close'].ewm(span=ema, adjust=False).mean()
        bollinger_data['dema'] = 2*bollinger_data['ema'] - bollinger_data['ema'].ewm(com=ema, adjust=False).mean()
        bollinger_data2 = collect_data(forex, twice_time, start_bar, end_bar)

        bollinger_data2['ema'] = bollinger_data2['close'].ewm(span=ema, adjust=False).mean()
        bollinger_data2['dema'] = 2*bollinger_data2['ema'] - bollinger_data2['ema'].ewm(com=ema, adjust=False).mean()

        current_dema = bollinger_data.iloc[-1]['dema']
        current2_dema = bollinger_data2.iloc[-1]['dema']

        current_close = bollinger_data.iloc[-1]['close']
        current_open = bollinger_data.iloc[-1]['open']
        current_low = bollinger_data.iloc[-1]['low']
        current_high = bollinger_data.iloc[-1]['high']
        current_lower = bollinger_data.iloc[-1]['LOWER']
        current_upper = bollinger_data.iloc[-1]['UPPER']

        previous_close = bollinger_data.iloc[-2]['close']
        previous_sma = bollinger_data.iloc[-2]['SMA']
        previous_open = bollinger_data.iloc[-2]['open']
        previous_low = bollinger_data.iloc[-2]['low']
        previous_high = bollinger_data.iloc[-2]['high']
        previous_lower = bollinger_data.iloc[-2]['LOWER']
        previous_upper = bollinger_data.iloc[-2]['UPPER']

        previous2_low = bollinger_data.iloc[-3]['low']
        previous2_high = bollinger_data.iloc[-3]['high']

        if previous_close < previous_lower and current_close > current_lower and current_dema > current2_dema and current_close > current2_dema:
            print("----------------------------------------------------", twice_time, "-------------------------")
            # Buy Signal
            stop_losses = min(bollinger_data['low']) - stop_loss(forex)
            print("[+]", datetime.now().strftime("%H:%M:%S"), "Bollinger(DEMA) +Buy signal", forex, "at", chart_time)
            place_order(forex, "buy", stop_losses, number_of_pips(forex))
            time.sleep(10)
            bollinger_only_strategy(forex, chart_time, start_bar, end_bar)

        elif previous_open > previous_close < previous_lower and previous_high > previous_sma and current_open < current_close and current_low < current_lower < current_close:
            stop_losses = min(bollinger_data['low']) - stop_loss(forex)
            print("[+]", datetime.now().strftime("%H:%M:%S"), "Bollinger +Buy signal", forex, "at", chart_time)
            place_order(forex, "buy", stop_losses, number_of_pips(forex))
            time.sleep(10)
            bollinger_only_strategy(forex, chart_time, start_bar, end_bar)

        elif previous_close > previous_upper and current_close < current_upper and current_dema < current2_dema and current_close < current2_dema:
            print("----------------------------------------------------", twice_time, "-------------------------")
            # Sell Signal
            stop_losses = max(bollinger_data['high']) + stop_loss(forex)
            print("[+]", datetime.now().strftime("%H:%M:%S"), "Bollinger(DEMA) -Sell signal", forex, "at", chart_time)
            place_order(forex, "sell", stop_losses, number_of_pips(forex))
            time.sleep(10)
            bollinger_only_strategy(forex, chart_time, start_bar, end_bar)

        elif previous_open < previous_close > previous_upper and previous_low < previous_sma and current_open > current_close and current_high > current_upper > current_close:
            # Sell Signal
            stop_losses = max(bollinger_data['high']) + stop_loss(forex)
            print("[+]", datetime.now().strftime("%H:%M:%S"), "Bollinger -Sell signal", forex, "at", chart_time)
            place_order(forex, "sell", stop_losses, number_of_pips(forex))
            time.sleep(10)
            bollinger_only_strategy(forex, chart_time, start_bar, end_bar)

        else:
            time.sleep(10)
            bollinger_only_strategy(forex, chart_time, start_bar, end_bar)

    except TypeError:
        pass


def candle_patterns(forex, chart_time, start_bar, end_bar):
    # Variables
    standard_deviation = 2
    period = 20
    timing_trade(stock_symbol=forex, chart_frame=chart_time)

    candle_data = collect_data(forex, chart_time, start_bar, end_bar)

    candle_data['SMA'] = candle_data['close'].rolling(period).mean()
    candle_data['STD'] = candle_data['close'].rolling(period).std()
    candle_data['UPPER'] = candle_data['SMA'] + (standard_deviation * candle_data['STD'])
    candle_data['LOWER'] = candle_data['SMA'] - (standard_deviation * candle_data['STD'])

    def convert(val):
        point = Metatrader.symbol_info(forex).point

        if str(point) == '0.001':
            pips = val * 1000
            return pips

        else:
            pips = val * 100000
            return pips

    for i in range(2, candle_data.shape[0]):
        current = candle_data.iloc[i, :]
        previous_1 = candle_data.iloc[i - 1, :]
        previous_2 = candle_data.iloc[i - 2, :]

        real_body = abs(current['open'] - current['close'])
        calculated_body = convert(real_body)
        previous_body_2 = abs(previous_2['open'] - previous_2['close'])
        candle_range = current['high'] - current['low']
        idx = candle_data.index[i]

        # Bullish Engulfing Candlestick Pattern
        candle_data.loc[idx, 'Bullish Engulfing'] = current['high'] > previous_1['high'] and current['low'] < previous_1['low'] and real_body >= 0.8 * candle_range and current['close'] > current['open']

        # Bearish Engulfing Candlestick Pattern
        candle_data.loc[idx, 'Bearish Engulfing'] = current['high'] > previous_1['high'] and current['low'] < previous_1['low'] and real_body >= 0.8 * candle_range and current['close'] < current['open']

        # Bullish Swing Candlestick Pattern
        candle_data.loc[idx, 'Bullish Swing'] = previous_2['close'] < previous_2['open'] and current['open'] < current['close'] and current['low'] > previous_1['low'] < previous_2['low'] and previous_1['high'] < current['high'] and convert(previous_body_2) > 20 and convert(real_body) > 20

        # Bearish Swing Candlestick Pattern
        candle_data.loc[idx, 'Bearish Swing'] = previous_2['close'] > previous_2['open'] and current['open'] > current['close'] and current['high'] < previous_1['high'] > previous_2['high'] and previous_1['low'] > current['low'] and convert(previous_body_2) > 20 and convert(real_body) > 20

        # Bullish Crouch
        candle_data.loc[idx, 'Bullish Crouch'] = current['high'] > previous_1['high'] and current['low'] > previous_1['low'] and previous_1['close'] < current['low'] and previous_1['open'] > previous_1['close'] and current['open'] < current['close']

        # Bearish Crouch
        candle_data.loc[idx, 'Bearish Crouch'] = current['low'] < previous_1['low'] and current['high'] < previous_1['high'] and current['high'] < previous_1['close'] and previous_1['open'] < previous_1['close'] and current['open'] > current['close']

        # Bullish Trends
        candle_data.loc[idx, 'Bullish Trend 1'] = current['open'] < current['close'] and calculated_body > 80

        # Bearish Trends
        candle_data.loc[idx, 'Bearish Trend 1'] = current['open'] > current['close'] and calculated_body > 80

    candle_data.fillna(False, inplace=True)

    if str(candle_data.iloc[-1]['Bullish Engulfing']).upper() == "TRUE":
        stop_losses = min(candle_data['low']) - stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish Engulfing +Buy signal", forex, "at", chart_time)
        place_order(forex, "buy", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    elif str(candle_data.iloc[-1]['Bullish Trend 1']).upper() == "TRUE":
        stop_losses = min(candle_data['low']) - stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish Trend 1 candle body +Buy signal", forex, "at", chart_time)
        place_order(forex, "buy", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    elif str(candle_data.iloc[-1]['Bearish Engulfing']).upper() == "TRUE":
        stop_losses = max(candle_data['high']) + stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish Engulfing -Sell signal", forex, "at", chart_time)
        place_order(forex, "sell", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    elif str(candle_data.iloc[-1]['Bearish Trend 1']).upper() == "TRUE":
        stop_losses = max(candle_data['high']) + stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish Trend 1 candle body -Sell signal", forex, "at", chart_time)
        place_order(forex, "sell", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    elif str(candle_data.iloc[-1]['Bullish Crouch']).upper() == "TRUE":
        stop_losses = min(candle_data['low']) - stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bullish Crouch +Buy signal", forex, "at", chart_time)
        place_order(forex, "buy", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    elif str(candle_data.iloc[-1]['Bearish Crouch']).upper() == "TRUE":
        stop_losses = max(candle_data['high']) + stop_loss(forex)
        print("[+]", datetime.now().strftime("%H:%M:%S"), "Bearish Crouch -Sell signal", forex, "at", chart_time)
        place_order(forex, "sell", stop_losses, number_of_pips(forex))
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)

    else:
        time.sleep(10)
        candle_patterns(forex, chart_time, start_bar, end_bar)


if __name__ == '__main__':
    try:
        START = 0
        BARS = 300

# --------------------------------------------------------- AUDUSD ----------------------------------------------------
        AUDUSD_Bollinger_5 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        AUDUSD_Bollinger_6 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M6, START, BARS))
        AUDUSD_Bollinger_10 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M10, START, BARS))
        AUDUSD_Bollinger_12 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        AUDUSD_Bollinger_15 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        AUDUSD_Bollinger_20 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        AUDUSD_Bollinger_30 = multiprocessing.Process(target=bollinger_only_strategy, args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        AUDUSD_Candle_12 = multiprocessing.Process(target=candle_patterns, args=("AUDUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        AUDUSD_Candle_15 = multiprocessing.Process(target=candle_patterns, args=("AUDUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        AUDUSD_Candle_20 = multiprocessing.Process(target=candle_patterns, args=("AUDUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        AUDUSD_Candle_30 = multiprocessing.Process(target=candle_patterns, args=("AUDUSD", Metatrader.TIMEFRAME_M30, START, BARS))

# ------------------------------------------------------ EURUSD -------------------------------------------------------
        EURUSD_Bollinger_5 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        EURUSD_Bollinger_6 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M6, START, BARS))
        EURUSD_Bollinger_10 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M10, START, BARS))
        EURUSD_Bollinger_12 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        EURUSD_Bollinger_15 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        EURUSD_Bollinger_20 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        EURUSD_Bollinger_30 = multiprocessing.Process(target=bollinger_only_strategy, args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        EURUSD_Candle_12 = multiprocessing.Process(target=candle_patterns, args=("EURUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        EURUSD_Candle_15 = multiprocessing.Process(target=candle_patterns, args=("EURUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        EURUSD_Candle_20 = multiprocessing.Process(target=candle_patterns, args=("EURUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        EURUSD_Candle_30 = multiprocessing.Process(target=candle_patterns, args=("EURUSD", Metatrader.TIMEFRAME_M30, START, BARS))

# ------------------------------------------------------ USDJPY -------------------------------------------------------
        USDJPY_Bollinger_5 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M5, START, BARS))
        USDJPY_Bollinger_6 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M6, START, BARS))
        USDJPY_Bollinger_10 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M10, START, BARS))
        USDJPY_Bollinger_12 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M12, START, BARS))
        USDJPY_Bollinger_15 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        USDJPY_Bollinger_20 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M20, START, BARS))
        USDJPY_Bollinger_30 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

        USDJPY_Candle_12 = multiprocessing.Process(target=candle_patterns, args=("USDJPY", Metatrader.TIMEFRAME_M12, START, BARS))
        USDJPY_Candle_15 = multiprocessing.Process(target=candle_patterns, args=("USDJPY", Metatrader.TIMEFRAME_M15, START, BARS))
        USDJPY_Candle_20 = multiprocessing.Process(target=candle_patterns, args=("USDJPY", Metatrader.TIMEFRAME_M20, START, BARS))
        USDJPY_Candle_30 = multiprocessing.Process(target=candle_patterns, args=("USDJPY", Metatrader.TIMEFRAME_M30, START, BARS))

# ------------------------------------------------------ GBPUSD -------------------------------------------------------
        GBPUSD_Bollinger_5 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M5, START, BARS))
        GBPUSD_Bollinger_6 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M6, START, BARS))
        GBPUSD_Bollinger_10 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M10, START, BARS))
        GBPUSD_Bollinger_12 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        GBPUSD_Bollinger_15 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        GBPUSD_Bollinger_20 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        GBPUSD_Bollinger_30 = multiprocessing.Process(target=bollinger_only_strategy, args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

        GBPUSD_Candle_12 = multiprocessing.Process(target=candle_patterns, args=("GBPUSD", Metatrader.TIMEFRAME_M12, START, BARS))
        GBPUSD_Candle_15 = multiprocessing.Process(target=candle_patterns, args=("GBPUSD", Metatrader.TIMEFRAME_M15, START, BARS))
        GBPUSD_Candle_20 = multiprocessing.Process(target=candle_patterns, args=("GBPUSD", Metatrader.TIMEFRAME_M20, START, BARS))
        GBPUSD_Candle_30 = multiprocessing.Process(target=candle_patterns, args=("GBPUSD", Metatrader.TIMEFRAME_M30, START, BARS))

# ------------------------------------------------------ USDCAD -------------------------------------------------------
        USDCAD_Bollinger_5 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M5, START, BARS))
        USDCAD_Bollinger_6 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M6, START, BARS))
        USDCAD_Bollinger_10 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M10, START, BARS))
        USDCAD_Bollinger_12 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M12, START, BARS))
        USDCAD_Bollinger_15 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        USDCAD_Bollinger_20 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M20, START, BARS))
        USDCAD_Bollinger_30 = multiprocessing.Process(target=bollinger_only_strategy, args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

        USDCAD_Candle_12 = multiprocessing.Process(target=candle_patterns, args=("USDCAD", Metatrader.TIMEFRAME_M12, START, BARS))
        USDCAD_Candle_15 = multiprocessing.Process(target=candle_patterns, args=("USDCAD", Metatrader.TIMEFRAME_M15, START, BARS))
        USDCAD_Candle_20 = multiprocessing.Process(target=candle_patterns, args=("USDCAD", Metatrader.TIMEFRAME_M20, START, BARS))
        USDCAD_Candle_30 = multiprocessing.Process(target=candle_patterns, args=("USDCAD", Metatrader.TIMEFRAME_M30, START, BARS))

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
        AUDUSD_Bollinger_5.start()
        #AUDUSD_Bollinger_6.start()
        AUDUSD_Bollinger_10.start()
        AUDUSD_Bollinger_12.start()
        AUDUSD_Bollinger_15.start()
        AUDUSD_Bollinger_20.start()
        AUDUSD_Bollinger_30.start()

        AUDUSD_Candle_12.start()
        AUDUSD_Candle_15.start()
        AUDUSD_Candle_20.start()
        AUDUSD_Candle_30.start()

        EURUSD_Bollinger_5.start()
        #EURUSD_Bollinger_6.start()
        EURUSD_Bollinger_10.start()
        EURUSD_Bollinger_12.start()
        EURUSD_Bollinger_15.start()
        EURUSD_Bollinger_20.start()
        EURUSD_Bollinger_30.start()

        EURUSD_Candle_12.start()
        EURUSD_Candle_15.start()
        EURUSD_Candle_20.start()
        EURUSD_Candle_30.start()

        USDJPY_Bollinger_5.start()
        #USDJPY_Bollinger_6.start()
        USDJPY_Bollinger_10.start()
        USDJPY_Bollinger_12.start()
        USDJPY_Bollinger_15.start()
        USDJPY_Bollinger_20.start()
        USDJPY_Bollinger_30.start()

        USDJPY_Candle_12.start()
        USDJPY_Candle_15.start()
        USDJPY_Candle_20.start()
        USDJPY_Candle_30.start()

        GBPUSD_Bollinger_5.start()
        #GBPUSD_Bollinger_6.start()
        GBPUSD_Bollinger_10.start()
        GBPUSD_Bollinger_12.start()
        GBPUSD_Bollinger_15.start()
        GBPUSD_Bollinger_20.start()
        GBPUSD_Bollinger_30.start()

        GBPUSD_Candle_12.start()
        GBPUSD_Candle_15.start()
        GBPUSD_Candle_20.start()
        GBPUSD_Candle_30.start()

        USDCAD_Bollinger_5.start()
        #USDCAD_Bollinger_6.start()
        USDCAD_Bollinger_10.start()
        USDCAD_Bollinger_12.start()
        USDCAD_Bollinger_15.start()
        USDCAD_Bollinger_20.start()
        USDCAD_Bollinger_30.start()

        USDCAD_Candle_12.start()
        USDCAD_Candle_15.start()
        USDCAD_Candle_20.start()
        USDCAD_Candle_30.start()

    except KeyboardInterrupt:
        Metatrader.shutdown()
        exit()
