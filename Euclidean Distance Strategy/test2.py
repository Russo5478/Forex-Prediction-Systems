from pandas import to_datetime, DataFrame, read_csv
import MetaTrader5 as MeT5
from math import sqrt


class SimRedone:
    def __init__(self):
        self.meta = MeT5
        self.un_formatted_xl = 'bol1.csv'
        self.formatted_xl = 'prepared.csv'
        self.test_bar = -10
        self.start_compare = 10
        self.num_of_results = 3
        self.short_trend = 2
        self.long_trend = 9

        self.data_collection("XAUUSD", self.meta.TIMEFRAME_H1, 1, 30000)
        self.data_preparation()
        indexes = self.euclidean_function()
        self.find_values(indexes)

    def data_collection(self, symbol_chart, timeframe_chart, start_pos, end_pos):
        self.meta.initialize()
        current_values = self.meta.copy_rates_from_pos(symbol_chart, timeframe_chart, start_pos, end_pos)
        self.meta.shutdown()

        current_dataframe = DataFrame(current_values)
        current_dataframe['time'] = to_datetime(current_dataframe['time'], unit='s')
        current_dataframe['time'] = to_datetime(current_dataframe['time'], format='%Y-%m-%d')
        current_dataframe = current_dataframe.drop(["spread", "real_volume"], axis=1)

        current_dataframe.fillna(False, inplace=True)
        current_dataframe.to_csv(self.un_formatted_xl, index=False)

        return current_dataframe

    def data_preparation(self):
        file_ = read_csv(self.un_formatted_xl)
        candle_data = DataFrame(file_)

        candle_data['HA_close'] = (candle_data['open'] + candle_data['close'] + candle_data['low'] + candle_data[
            'high']) / 4

        for i in range(0, len(candle_data)):
            if i == 0:
                candle_data.loc[i, 'HA_open'] = (candle_data.loc[i, 'open'] + candle_data.loc[i, 'close']) / 2
            else:
                candle_data.loc[i, 'HA_open'] = (candle_data.loc[i - 1, 'HA_open'] + candle_data.loc[i - 1, 'HA_close']) / 2

        candle_data['HA_high'] = candle_data[['HA_close', 'HA_open', 'high']].max(axis=1)
        candle_data['HA_low'] = candle_data[['HA_close', 'HA_open', 'low']].min(axis=1)

        for x in range(1, candle_data.shape[0]):
            current = candle_data.iloc[x, :]
            previous = candle_data.iloc[x - 1, :]

            candle_change = ((current['close'] - previous['close']) / previous['close']) * 100
            heikin_change = ((current['HA_close'] - previous['HA_close']) / previous['HA_close']) * 100

            idx = candle_data.index[x]
            candle_data.loc[idx, 'CN_change'] = candle_change
            candle_data.loc[idx, 'HA_change'] = heikin_change

        candle_data = candle_data.dropna()
        candle_data.to_csv(self.formatted_xl, index=False)

    def euclidean_function(self):
        file_ = read_csv(self.formatted_xl)
        data = DataFrame(file_)
        conditions = []

        def euclidean_distance(col_vals, var_vals):
            distances = []

            if len(col_vals) == len(var_vals):
                for i in range(0, len(col_vals)):
                    mini_distance = (col_vals[i] - var_vals[i]) ** 2
                    distances.append(mini_distance)

            return sqrt(sum(distances))

        for i in range(0, len(data) - self.start_compare):
            var1 = [data.iloc[self.test_bar]['CN_change'], data.iloc[self.test_bar]['HA_change']]
            var2 = [data.iloc[i]['CN_change'], data.iloc[i]['HA_change']]

            dist_ = euclidean_distance(var1, var2)
            conditions.append(dist_)

        sorted_list = sorted(set(conditions))
        min_five = sorted_list[:self.num_of_results]
        indexed = []

        for nums in min_five:
            index_nums = conditions.index(nums)
            indexed.append(index_nums)

        return indexed

    def find_values(self, list_index):
        file_ = read_csv(self.formatted_xl)
        data = DataFrame(file_)
        buys = []
        sells = []

        long_buys = []
        long_sells = []

        for indexes in list_index:
            for x in range(1, self.short_trend + 1):
                next_index = indexes + x

                if data.iloc[next_index]['close'] > data.iloc[next_index]['open']:
                    buy_pips = data.iloc[next_index]['close'] - data.iloc[next_index]['open']
                    sell_pips = 0

                elif data.iloc[next_index]['close'] < data.iloc[next_index]['open']:
                    buy_pips = 0
                    sell_pips = data.iloc[next_index]['open'] - data.iloc[next_index]['close']

                else:
                    buy_pips = 0
                    sell_pips = 0

                buys.append(buy_pips)
                sells.append(sell_pips)

            for z in range(1, self.long_trend + 1):
                next_index = indexes + z

                if data.iloc[next_index]['close'] > data.iloc[next_index]['open']:
                    l_buy_pips = data.iloc[next_index]['close'] - data.iloc[next_index]['open']
                    l_sell_pips = 0

                elif data.iloc[next_index]['close'] < data.iloc[next_index]['open']:
                    l_buy_pips = 0
                    l_sell_pips = data.iloc[next_index]['open'] - data.iloc[next_index]['close']

                else:
                    l_buy_pips = 0
                    l_sell_pips = 0

                long_buys.append(l_buy_pips)
                long_sells.append(l_sell_pips)

        total_pips = sum(buys) + sum(sells)
        buy_percent = round(((sum(buys) / total_pips) * 100), 2)
        sell_percent = round(((sum(sells) / total_pips) * 100), 2)

        print("Short Trend Total Pips:", round(total_pips, 2), "-----> Buy Pips:", round(sum(buys), 2),
              "-----> Sell Pips:", round(sum(sells), 2))

        print("Average Buy Pips:", round(sum(buys) / self.num_of_results, 2),
              "Average Sell Pips:", round(sum(sells) / self.num_of_results, 2))

        print("Short Trend (", self.short_trend, ") Buy% >", buy_percent)
        print("Short Trend (", self.short_trend, ") Sell% >", sell_percent)

        long_total_pips = sum(long_buys) + sum(long_sells)
        long_buy_percent = round(((sum(long_buys) / long_total_pips) * 100), 2)
        long_sell_percent = round(((sum(long_sells) / long_total_pips) * 100), 2)

        print("\nLong Trend Total Pips:", round(long_total_pips, 2), "-----> Buy Pips:", round(sum(long_buys), 2),
              "-----> Sell Pips:", round(sum(long_sells), 2))

        print("Average Buy Pips:", round(sum(long_buys) / self.num_of_results, 2),
              "Average Sells Pips:", round(sum(long_sells) / self.num_of_results, 2))

        print("Long Trend (", self.long_trend, ") Buy% >", long_buy_percent)
        print("Long Trend (", self.long_trend, ") Sell% >", long_sell_percent)

        print("\nLast Time:", data.iloc[self.test_bar]['time'])


if __name__ == '__main__':
    SimRedone()