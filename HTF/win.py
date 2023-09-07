import MetaTrader5 as mT5
from pandas import DataFrame, to_datetime
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class BackEnd:
    def __init__(self):
        self.meta = mT5
        self.maximumSpread = 100
        self.fxPairs = ["GBPUSD", "USDCHF", "AUDUSD", "AUDCHF", "EURUSD", "EURGBP", "NZDUSD", "EURCHF", "GBPCHF",
                        "CADCHF", "NZDCHF", "AUDJPY", "CHFJPY", "EURJPY", "GBPJPY", "USDJPY", "USDCAD", "AUDNZD",
                        "AUDCAD","EURAUD", "EURNZD", "EURCAD", "XAUEUR", "XAUUSD"]
        self.performCorrelation(self.fxPairs, self.meta.TIMEFRAME_H4)

    def dataCollection(self, forexPair: str, timeFrame: object, startIndex: int = 1, endIndex: int = 100):
        try:
            self.meta.initialize()
            ticks = self.meta.copy_rates_from_pos(forexPair, timeFrame, startIndex, endIndex)
            ticks_data = DataFrame(ticks)
            ticks_data['time'] = to_datetime(ticks_data['time'], unit='s')
            ticks_data['time'] = to_datetime(ticks_data['time'], format='%Y-%m-%d')
            self.meta.shutdown()

            return ticks_data

        except KeyError:
            pass

    def performCorrelation(self, currencyList: list, timeFrame: object):
        """
        Perform A Correlation Matrix
        :param currencyList: List of forex pairs or stock available on your broker platform
        :param timeFrame: Timeframe values to use to calculate the correlation matrix
        """
        combinedData = DataFrame()
        if len(currencyList):
            for pair in currencyList:
                self.meta.initialize()
                currencySpread = self.meta.symbol_info(pair)[12]

                if int(currencySpread) <= self.maximumSpread:
                    collectedData = self.dataCollection(forexPair=str(pair), timeFrame=timeFrame)
                    collectedData['PercentChange'] = collectedData['close'].pct_change() * 100
                    collectedData = collectedData.dropna()
                    combinedData[pair] = collectedData['PercentChange']
                self.meta.shutdown()

        # Calculate the correlation matrix
        correlationMatrix = combinedData.corr()

        # Set diagonal elements to NaN to exclude self-correlations
        np.fill_diagonal(correlationMatrix.values, np.nan)

        # Find the indices of the top correlated pairs
        num_pairs = 10
        top_corr_indices = correlationMatrix.unstack().sort_values(ascending=False).index
        top_corr_indices = [(pair[0], pair[1]) for pair in top_corr_indices if
                            not np.isnan(correlationMatrix.loc[pair])]

        processed_pairs = set()
        processed_pairs_dict = {}

        for pair in top_corr_indices:
            # Check if the pair or its reverse has been processed
            if pair not in processed_pairs and (pair[1], pair[0]) not in processed_pairs:
                processed_pairs.add(pair)
                processed_pairs_dict[pair] = correlationMatrix.loc[pair]
                processed_pairs.add((pair[1], pair[0]))

        # Separate the pairs into positive and negative correlations
        positive_corr_pairs = {pair: correlation for pair, correlation in processed_pairs_dict.items() if
                               correlation > 0}
        negative_corr_pairs = {pair: correlation for pair, correlation in processed_pairs_dict.items() if
                               correlation < 0}

        # Print the top positively correlated pairs
        print("Top Positively Correlated Pairs:")
        for pair, correlation_value in sorted(positive_corr_pairs.items(), key=lambda item: item[1], reverse=True)[
                                       :num_pairs]:
            print(pair[0], pair[1], correlation_value)

        # Print the top negatively correlated pairs
        print("\nTop Negatively Correlated Pairs:")
        for pair, correlation_value in sorted(negative_corr_pairs.items(), key=lambda item: item[1], reverse=False)[
                                       :num_pairs]:
            print(pair[0], pair[1], correlation_value)

        # Create and display correlation heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlationMatrix, annot=True, cmap="plasma")
        plt.title('Correlation Heatmap')
        plt.show()

    def scanMarket(self):
        pass


if __name__ == '__main__':
    BackEnd()
