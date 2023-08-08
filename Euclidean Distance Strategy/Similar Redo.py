from pandas import read_csv, DataFrame
from math import sqrt


def euclidean_distance(list_a: list, list_b: list):
    total_distance = []

    if len(list_a) == len(list_b):
        for values in range(0, len(list_a)):
            mini_distance = (list_a[values] - list_b[values]) ** 2
            total_distance.append(mini_distance)

    return sqrt(sum(total_distance))


class MainClass:
    def __init__(self):
        self.raw_data_file = 'bol1.csv'
        self.prepared_data_file = 'prepared.csv'
        self.testing_index = -1
        self.useful_fields = ['CN_change, HA_change']

        # self.data_preparation()
        self.value_finder()

    def data_preparation(self):
        raw_data = read_csv(self.raw_data_file)
        candle_data = DataFrame(raw_data)

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

        candle_data.to_csv(self.prepared_data_file, index=False)

    def value_finder(self):
        prepared_data = read_csv(self.prepared_data_file)
        prepared_values = DataFrame(prepared_data)

        testing_index = prepared_values.iloc[-1]

        for k in range(0, len(prepared_values)):
            pass
        print(testing_index)


if __name__ == '__main__':
    MainClass()
