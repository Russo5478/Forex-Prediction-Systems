import time

import MetaTrader5 as mT5
from pandas import DataFrame, to_datetime


def collector(forexPair, timeFrame, startIndex, endIndex):
    mT5.initialize()
    ticks = mT5.copy_rates_from_pos(forexPair, timeFrame, startIndex, endIndex)
    ticks_data = DataFrame(ticks)
    ticks_data['time'] = to_datetime(ticks_data['time'], unit='s')
    ticks_data['time'] = to_datetime(ticks_data['time'], format='%Y-%m-%d')
    mT5.shutdown()

    return ticks_data


pairs = ["AUDUSD", "USDCAD"]
major_timeframe = mT5.TIMEFRAME_H4
margin_call = 0.05
sleeper = 2

current_open1 = collector(pairs[0], major_timeframe, 0, 2)['open'].iloc[-1]
current_open2 = collector(pairs[1], major_timeframe, 0, 2)['open'].iloc[-1]

position = {"Order": ""}
print("Start")

while True:
    if not position["Order"]:
        current1 = collector(pairs[0], mT5.TIMEFRAME_M1, 0, 2)
        current2 = collector(pairs[1], mT5.TIMEFRAME_M1, 0, 2)

        current_change1 = ((current1['close'].iloc[-1] - current_open1) / current_open1) * 100
        current_change2 = ((current2['close'].iloc[-1] - current_open2) / current_open2) * 100

        if current_change1 >= margin_call and current_change2 >= margin_call:
            print(f"Buy position @ {current1['time'].iloc[-1]}")
            position["Order"] = "buy"
            time.sleep(sleeper)

        elif current_change1 <= -margin_call and current_change2 <= -margin_call:
            print(f"Sell position @ {current1['time'].iloc[-1]}")
            position["Order"] = "sell"
            time.sleep(sleeper)

        else:
            time.sleep(sleeper)

    else:
        break
