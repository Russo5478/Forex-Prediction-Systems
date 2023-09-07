import MetaTrader5 as mT5
from pandas import DataFrame, to_datetime, merge, read_csv, Timestamp
from tkinter import Tk, Frame
from tkinter.ttk import Notebook
from concurrent.futures import ThreadPoolExecutor


def timex_numerical(time2):
    if time2 == 16385:
        return 1 * 60

    elif time2 == 16386:
        return 2 * 60

    elif time2 == 16387:
        return 3 * 60

    elif time2 == 16388:
        return 4 * 60

    elif time2 == 16390:
        return 6 * 60

    elif time2 == 16392:
        return 8 * 60

    elif time2 == 16392:
        return 12 * 60

    elif time2 == 32769:
        return 1 * 60 * 24 * 7

    elif time2 == 49153:
        return 1 * 60 * 24 * 30

    else:
        return time2


def timey_numerical(time2):
    if time2 == 16385:
        return 1

    elif time2 == 16386:
        return 2

    elif time2 == 16387:
        return 3

    elif time2 == 16388:
        return 4

    elif time2 == 16390:
        return 6

    elif time2 == 16392:
        return 8

    elif time2 == 16392:
        return 12

    elif time2 == 32769:
        return 1

    elif time2 == 49153:
        return 1

    else:
        return time2


def bars_function(time1, time2, count):
    if time1 < 16385:
        unit = "minutes"

    elif 30 < time1 < 32769:
        unit = "hours"

    elif time1 == 32769:
        unit = "weeks"

    else:
        unit = "months"

    x = timex_numerical(time2)
    y = timey_numerical(time1)

    if unit == "minutes":
        intervals = int(y / x)
    elif unit == "hours":
        intervals = int((y * 60) / x)
    elif unit == "weeks":
        intervals = int((y * 60 * 24 * 7) / x)
    else:
        intervals = int((y * 60 * 24 * 30) / x)

    return intervals * count, intervals


class Window:
    def __init__(self, windowInit):
        self.meta = mT5
        self.windowInit = windowInit
        self.windowNote = None

        # Execute Functions
        self.window_settings()

    def dataCollection(self, forexPair: str, timeFrame: object, startIndex: int = 1, endIndex: int = 100):
        self.meta.initialize()
        ticks = self.meta.copy_rates_from_pos(forexPair, timeFrame, startIndex, endIndex)
        ticks_data = DataFrame(ticks)
        ticks_data['time'] = to_datetime(ticks_data['time'], unit='s')
        ticks_data['time'] = to_datetime(ticks_data['time'], format='%Y-%m-%d')
        self.meta.shutdown()

        return ticks_data

    def window_settings(self):
        windowWidth = 500
        windowHeight = 300
        self.windowInit.geometry(f'{windowWidth}x{windowHeight}')
        self.windowInit.title("Correlation Trading Strategy | Backtesting")
        self.windowInit.resizable(False, False)

        self.windowNote = Notebook(self.windowInit)
        self.windowNote.place(x=0, y=0, width=windowWidth, height=windowHeight)

        self.backtesting_window()

    def backtesting_window(self):
        backtestFrame = Frame(self.windowNote, bg='white')
        self.windowNote.add(backtestFrame, text="Strategy Backtest")

        self.backtest_function("AUDUSD", "USDCHF", self.meta.TIMEFRAME_H6, self.meta.TIMEFRAME_M5)

    def backtest_function(self, pair1: str, pair2: str, majorTime, minorTime, profitMargin: int = 20,
                          lots: float = 0.01, barBack: int = 100):
        minorBars, intervals = bars_function(majorTime, minorTime, barBack)

        pair1majorData = self.dataCollection(pair1, majorTime, endIndex=barBack)
        pair1minorData = self.dataCollection(pair1, minorTime, endIndex=minorBars)

        pair2majorData = self.dataCollection(pair2, majorTime, endIndex=barBack)
        pair2minorData = self.dataCollection(pair2, minorTime, endIndex=minorBars)
        print(intervals)

        if len(pair1majorData) == len(pair2majorData) and len(pair1minorData) == len(pair2minorData):
            def find_first_common_time(df1, df2):
                df1['time'] = to_datetime(df1['time'])
                df2['time'] = to_datetime(df2['time'])

                # Merge DataFrames on 'Time' to find common times
                merged = merge(df1, df2, on='time', how='inner')

                # Find the first common time
                first_common_time = merged['time'].iloc[0] if not merged.empty else None

                # Get all common times
                common_times = merged['time'].tolist()

                return first_common_time, common_times

            def analyze_forex_pair(major_minor_data):
                common_time, common_times = find_first_common_time(major_minor_data[0], major_minor_data[1])
                index_time_major = major_minor_data[0][major_minor_data[0]['time'] == common_time].index.tolist()[0]
                index_time_minor = major_minor_data[1][major_minor_data[1]['time'] == common_time].index.tolist()[0]

                index_last_major = major_minor_data[1][major_minor_data[1]['time'] == common_times[-1]].index.tolist()[0]

                largerTimeframe_data = DataFrame(major_minor_data[0][index_time_major:])
                smallerTimeframe_data = DataFrame(major_minor_data[1][index_time_minor:index_last_major])

                changes = []
                smallerTimeframe_data['change'] = None

                for x in range(0, len(largerTimeframe_data)):
                    try:
                        larger_time = largerTimeframe_data['time'].iloc[x-1]
                        for y in range(0, len(smallerTimeframe_data)):
                            small_time = smallerTimeframe_data['time'].iloc[y]

                            if small_time >= larger_time:
                                difference = (smallerTimeframe_data['close'].iloc[y] - largerTimeframe_data['open'].iloc[x-1])
                                change = (difference / largerTimeframe_data['open'].iloc[x-1]) * 100
                                changes.append(change)
                                smallerTimeframe_data.loc[y, 'change'] = change

                    except IndexError:
                        pass

                smallerTimeframe_data.to_csv(major_minor_data[2], index=False)

            # analyze_forex_pair([pair1majorData, pair1minorData, "pair1.csv"])
            # analyze_forex_pair([pair2majorData, pair2minorData, "pair2.csv"])

        pair_1 = read_csv("pair1.csv")
        pair_2 = read_csv("pair2.csv")

        pair1_position = {"Order": "", "Entry": "", "Time": ""}
        pair2_position = {"Order": "", "Entry": "", "Time": ""}

        if len(pair_1) == len(pair_2):
            for z in range(0, len(pair_1)):
                if not pair1_position["Order"] and not pair2_position["Order"]:
                    if pair_1['change'].iloc[z] >= 0.1 and pair_2['change'].iloc[z] >= 0.1:
                        pair1_position["Order"] = "sell"
                        pair1_position["Entry"] = pair_1['close'].iloc[z]
                        pair1_position["Time"] = pair_1['time'].iloc[z]

                        pair2_position["Order"] = "sell"
                        pair2_position["Entry"] = pair_2['close'].iloc[z]
                        pair2_position["Time"] = pair_2['time'].iloc[z]
                        # print(f"Sell position @ {pair_1['time'].iloc[z]}", pair1_position, pair2_position)

                    elif pair_1['change'].iloc[z] <= -0.1 and pair_2['change'].iloc[z] <= -0.1:
                        pair1_position["Order"] = "buy"
                        pair1_position["Entry"] = pair_1['close'].iloc[z]
                        pair1_position["Time"] = pair_1['time'].iloc[z]

                        pair2_position["Order"] = "buy"
                        pair2_position["Entry"] = pair_2['close'].iloc[z]
                        pair2_position["Time"] = pair_2['time'].iloc[z]
                        # print(f"Buy position @ {pair_1['time'].iloc[z]}")

                    else:
                        pass

                else:
                    if pair1_position["Order"] == "buy" and pair2_position["Order"] == "buy":
                        pair1_diff = (pair_1['high'].iloc[z] - pair1_position["Entry"]) + (pair_1['close'].iloc[z] - pair1_position['Entry'])
                        pair2_diff = (pair_2['high'].iloc[z] - pair2_position["Entry"]) + (pair_2['close'].iloc[z] - pair2_position['Entry'])

                        combined = pair1_diff + pair2_diff

                        if combined >= 0.0002:
                            print(f"Buy trade @ {pair1_position['Time']}, with {round(combined, 5)}, exit at {pair_1['time'].iloc[z]}")
                            pair1_position["Order"] = ""
                            pair1_position["Entry"] = ""
                            pair1_position["Time"] = ""

                            pair2_position["Order"] = ""
                            pair2_position["Entry"] = ""
                            pair2_position["Time"] = ""

                        else:
                            continue

                    elif pair1_position["Order"] == "sell" and pair2_position["Order"] == "sell":
                        pair1_diff = (pair_1['high'].iloc[z] - pair1_position["Entry"]) + (pair_1['close'].iloc[z] - pair1_position['Entry'])
                        pair2_diff = (pair_2['high'].iloc[z] - pair2_position["Entry"]) + (pair_2['close'].iloc[z] - pair2_position['Entry'])

                        combined = pair1_diff + pair2_diff

                        if combined <= -0.0002:
                            print(f"Sell trade @ {pair1_position['Time']}, with {round(combined, 5)}, exit at {pair_1['time'].iloc[z]}")
                            pair1_position["Order"] = ""
                            pair1_position["Entry"] = ""
                            pair1_position["Time"] = ""

                            pair2_position["Order"] = ""
                            pair2_position["Entry"] = ""
                            pair1_position["Time"] = ""

                        else:
                            continue

                    else:
                        continue



def load_window():
    window = Tk()
    Window(windowInit=window)
    window.mainloop()


if __name__ == '__main__':
    load_window()
