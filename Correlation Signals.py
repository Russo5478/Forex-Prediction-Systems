import numpy as np
from pandas import DataFrame, to_datetime
from ttkbootstrap import Window, Meter
import MetaTrader5 as mT5
from tkinter import Frame, Label, Button, messagebox, Text, END
from tkinter.ttk import Combobox
from threading import Thread
from datetime import datetime
from playsound import playsound


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def separator(master_widget, color, dimension: list, placement: list):
    separator_frame = Frame(master_widget)
    separator_frame.configure(background=color)
    separator_frame.place(x=placement[0], y=placement[1], width=dimension[0], height=dimension[1])


class WindowClass:
    def __init__(self):
        self.winInit = Window(themename="superhero")
        self.metaInit = mT5
        self.windowHeight = 590
        self.windowWidth = 1400
        self.maximumSpread = 35
        self.days_data = 366
        self.correlation_threshold = 0.7
        self.percent_threshold = 0.08
        self.collected_data = None
        self.meters = []
        self.meter_frames = []

        self.forex_pairs = ["GBPUSD", "USDCHF", "AUDUSD", "AUDCHF", "EURUSD", "EURGBP", "NZDUSD", "EURCHF",
                            "GBPCHF", "CADCHF", "NZDCHF", "GBPJPY", "USDJPY", "CADJPY", "NZDJPY", "EURNZD",
                            "EURCAD", "USDCAD", "GBPAUD", "GBPCAD", "GBPNZD", "NZDCAD", "XAUUSD", "XAUEUR",
                            "AUDJPY", "AUDNZD", "EURAUD", "AUDCAD", "EURJPY", "CHFJPY"]
        self.symbols = ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF", "XAU"]
        self.daily_cs = None
        self.h12_cs = None
        self.h8_cs = None
        self.h6_cs = None
        self.h4_cs = None
        self.positive_signals = None
        self.negative_signals = None
        self.window_closed = False
        self.signaled_pair = []
        self.sound_file = "not.mp3"

        self.window_settings()
        self.winInit.mainloop()

    def window_settings(self):
        self.winInit.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.winInit.title("Forex Correlation | Signals Only")
        self.winInit.resizable(False, False)

        center(self.winInit)
        self.window_widgets()

        daily_thread = Thread(target=self.plot_meters, args=(self.metaInit.TIMEFRAME_D1,))
        self.winInit.after(1000, daily_thread.start)

        signal_thread = Thread(target=self.signal_generator)
        self.winInit.after(10000, signal_thread.start)

        def correlation_():
            self.daily_cs = self.correlation_calculation(self.metaInit.TIMEFRAME_D1, self.days_data)
            self.h12_cs = self.correlation_calculation(self.metaInit.TIMEFRAME_H12, self.days_data*2)
        
        def run_correlation():
            corr_thread = Thread(target=correlation_())
            corr_thread.start()

        self.winInit.after(5000, run_correlation)

        def on_closing():
            print("perfom closing activities")
            self.window_closed = True
            self.winInit.destroy()

        self.winInit.protocol("WM_DELETE_WINDOW", on_closing)

    def window_widgets(self):
        side_frame_width = 250
        side_frame_height = 150
        side_frame = Frame(self.winInit)
        side_frame.place(x=0, y=440, width=self.windowWidth, height=side_frame_height)

        separator(self.winInit, "#fff", [self.windowWidth, 2], [0, 430])

        plot_settings_frame = Frame(side_frame)
        plot_settings_frame.place(x=0, y=0, width=side_frame_width, height=120)

        plot_settings_title = Label(plot_settings_frame)
        plot_settings_title.configure(text="Currency Strength Settings", font=('yu gothic ui', 12, "bold"))
        plot_settings_title.place(x=23, y=10)

        separator(plot_settings_frame, "#fff", [side_frame_width-20, 1], [10, 35])

        plot_timeframe_label = Label(plot_settings_frame)
        plot_timeframe_label.configure(text="Timeframe", font=('yu gothic ui', 10, "bold"))
        plot_timeframe_label.place(x=15, y=48)
        
        plot_time_choice = Combobox(plot_settings_frame)
        plot_time_choice['values'] = ["Last 4 Hour", "Last 6 Hour", "Last 8 Hour", "Last 12 Hour", "Today"]
        plot_time_choice.set("Today")
        plot_time_choice.configure(justify='center', font=('yu gothic ui', 10), state='readonly')
        plot_time_choice.place(x=90, y=45, width=140)

        def refresh_plots():
            plot_button.configure(state='disabled')
            selected_time = plot_time_choice.get()

            if selected_time == "Last 4 Hour":
                collecting_time = self.metaInit.TIMEFRAME_H4

            elif selected_time == "Last 6 Hour":
                collecting_time = self.metaInit.TIMEFRAME_H6

            elif selected_time == "Last 8 Hour":
                collecting_time = self.metaInit.TIMEFRAME_H8

            elif selected_time == "Last 12 Hour":
                collecting_time = self.metaInit.TIMEFRAME_H12

            else:
                collecting_time = self.metaInit.TIMEFRAME_D1

            for meter_plotted in self.meter_frames:
                meter_plotted.destroy()

            self.meter_frames.clear()

            refresh_thread = Thread(target=self.plot_meters, args=(collecting_time,))
            refresh_thread.start()
            plot_button.configure(state='normal')

        plot_button = Button(plot_settings_frame, command=refresh_plots)
        plot_button.configure(text="Refresh Data", font=('yu gothic ui', 10, "bold"), bg="blue", relief="solid",
                              borderwidth=1)
        plot_button.place(x=70, y=85, width=100, height=25)

        positive_corr_frame = Frame(side_frame)
        positive_corr_frame.place(x=270, y=0, width=550, height=side_frame_height)
        
        negative_corr_frame = Frame(side_frame)
        negative_corr_frame.place(x=838, y=0, width=550, height=side_frame_height)

        positive_corr_title = Label(positive_corr_frame)
        positive_corr_title.configure(text="Positive Correlation Signals", font=('yu gothic ui', 12, "bold"))
        positive_corr_title.place(x=170, y=0)

        separator(positive_corr_frame, "#fff", [side_frame_width - 20, 1], [158, 25])
        
        negative_corr_title = Label(negative_corr_frame)
        negative_corr_title.configure(text="Negative Correlation Signals", font=('yu gothic ui', 12, "bold"))
        negative_corr_title.place(x=170, y=0)

        separator(negative_corr_frame, "#fff", [side_frame_width - 20, 1], [158, 25])

        positive_corr_center = Text(positive_corr_frame)
        positive_corr_center.configure(background="#fff", foreground="#000", state="disabled")
        positive_corr_center.place(x=0, y=38, width=550, height=110)
        self.positive_signals = positive_corr_center
        
        negative_corr_center = Text(negative_corr_frame)
        negative_corr_center.configure(background="#fff", foreground="#000", state="disabled")
        negative_corr_center.place(x=0, y=38, width=550, height=110)
        self.negative_signals = negative_corr_center

        def clear_list():
            self.signaled_pair.clear()

        clear_btn = Button(self.winInit, command=clear_list)
        clear_btn.configure(text="Clear", relief="solid")
        clear_btn.place(x=20, y=560)

    def dataCollection(self, forexPair: str, timeFrame: object, startIndex: int = 0, endIndex: int = 2):
        try:
            self.metaInit.initialize()
            ticks = self.metaInit.copy_rates_from_pos(forexPair, timeFrame, startIndex, endIndex)
            ticks_data = DataFrame(ticks)
            ticks_data['time'] = to_datetime(ticks_data['time'], unit='s')
            ticks_data['time'] = to_datetime(ticks_data['time'], format='%Y-%m-%d')
            self.metaInit.shutdown()

            return ticks_data

        except KeyError:
            pass

    def create_widgets(self, coordinates: list, symbol: str, load_style: str, status: str):
        holderFrame = Frame(self.winInit)
        holderFrame.place(x=coordinates[0], y=coordinates[1], width=245, height=170)

        frameTitle = Label(holderFrame)
        frameTitle.configure(text=f"{symbol} currency strength", font=('yu gothic ui', 12))
        frameTitle.place(x=40, y=0)

        mainMeter = Meter(master=holderFrame, metertype="semi", textright="%", arcoffset=170, arcrange=200)
        mainMeter.configure(amountused=0, subtext=f"{status}", interactive=False, stripethickness=5,
                            bootstyle=load_style, subtextstyle=load_style)
        mainMeter.place(x=20, y=30)

        return holderFrame, mainMeter

    def plot_meters(self, time_frame):
        combinedData = DataFrame()
        for pair in self.forex_pairs:
            self.metaInit.initialize()
            try:
                collectedData = self.dataCollection(forexPair=str(pair), timeFrame=time_frame)
                collectedData['PercentChange'] = collectedData['close'].pct_change() * 100
                collectedData = collectedData.dropna()
                combinedData[pair] = collectedData['PercentChange']

            except TypeError:
                pass

            self.metaInit.shutdown()

        self.collected_data = combinedData.T
        frameCoordinates = [[20, 30], [20, 250], [300, 30], [300, 250], [580, 30], [580, 250], [860, 30], [860, 250],
                            [1140, 30]]
        count = 0

        for symbol in self.symbols:
            netChange, load_type, status = self.comparer(symbol)
            frames, meter_widget = self.create_widgets(frameCoordinates[count], symbol, load_type, status)
            meter_widget.configure(amountused=netChange)
            self.meter_frames.append(frames)
            self.meters.append(meter_widget)
            count += 1

    def comparer(self, symbol):
        base_pairs = self.collected_data[self.collected_data.index.str.endswith(f'{symbol.upper()}')]
        quote_pairs = self.collected_data[self.collected_data.index.str.startswith(f'{symbol.upper()}')]
        net_change = (-(base_pairs.sum().sum()) + quote_pairs.sum().sum())/(len(base_pairs) + len(quote_pairs))*100

        def map_value(value):
            # First, map the value from the 'from' range to a 0-1 range
            normalized_value = (value - (-100)) / (100 - (-100))

            # Then, map the normalized value to the 'to' range
            result = 0 + (normalized_value * (100 - 0))

            return result

        ranged_change = round(map_value(net_change), 2)

        if ranged_change <= 30:
            load_type = 'danger'
            status = 'Very Weak'

        elif ranged_change <= 50:
            load_type = 'warning'
            status = 'Weak'

        elif  ranged_change <= 70:
            load_type = 'info'
            status = 'Moderate'

        else:
            load_type = 'success'
            status = 'Very Strong'

        return ranged_change, load_type, status

    def correlation_calculation(self, timeFrame, end_count):
        combinedData = DataFrame()
        for pair in self.forex_pairs:
            self.metaInit.initialize()
            collectedData = self.dataCollection(forexPair=str(pair), timeFrame=timeFrame, startIndex=1,
                                                endIndex=end_count)
            collectedData['PercentChange'] = collectedData['close'].pct_change() * 100
            collectedData = collectedData.dropna()
            combinedData[pair] = collectedData['PercentChange']
            self.metaInit.shutdown()

        correlationMatrix = combinedData.corr()

        # Set diagonal elements to NaN to exclude self-correlations
        np.fill_diagonal(correlationMatrix.values, np.nan)

        # Find the indices of the top correlated pairs
        top_corr_indices = correlationMatrix.unstack().sort_values(ascending=False).index
        top_corr_indices = [(pair[0], pair[1]) for pair in top_corr_indices if
                            not np.isnan(correlationMatrix.loc[pair])]

        # Create a set to track pairs that have been processed
        processed_pairs = set()

        # Create a dictionary to store processed pairs and their correlation values
        processed_pairs_dict = {}

        for corr_pair in top_corr_indices:
            if corr_pair[0] != corr_pair[1]:
                if corr_pair not in processed_pairs and (corr_pair[1], corr_pair[0]) not in processed_pairs:
                    processed_pairs.add(corr_pair)
                    processed_pairs_dict[corr_pair] = correlationMatrix.loc[corr_pair]

                    # Mark the reverse pair as processed as well to avoid duplication
                    processed_pairs.add((corr_pair[1], corr_pair[0]))

        # Separate the pairs into positive and negative correlations
        positive_corr_pairs = {pair: correlation for pair, correlation in processed_pairs_dict.items() if
                               correlation > 0 and correlation >= self.correlation_threshold}
        negative_corr_pairs = {pair: correlation for pair, correlation in processed_pairs_dict.items() if
                               correlation < 0 and correlation <= -self.correlation_threshold}

        positive_pairs = [pair for pair in positive_corr_pairs]
        negative_pairs = [pair for pair in negative_corr_pairs]

        return positive_pairs, negative_pairs

    def signal_generator(self):
        if not self.window_closed:
            def negative_check(pairs_combo, timeFrame):
                today = datetime.today()
                current_time = today.strftime("%d-%b %H:%M:%S")

                for currency_pair in pairs_combo:
                    collectedData_pair1 = self.dataCollection(forexPair=currency_pair[0], timeFrame=timeFrame)
                    collectedData_pair2 = self.dataCollection(forexPair=currency_pair[1], timeFrame=timeFrame)

                    try:
                        collectedData_pair1['PercentChange'] = collectedData_pair1['close'].pct_change() * 100
                        collectedData_pair1 = collectedData_pair1.dropna()

                        collectedData_pair2['PercentChange'] = collectedData_pair2['close'].pct_change() * 100
                        collectedData_pair2 = collectedData_pair2.dropna()

                        if collectedData_pair1.iloc[-1]['PercentChange'] < 0 and \
                                collectedData_pair2.iloc[-1]['PercentChange'] < 0 and \
                                abs(collectedData_pair1.iloc[-1]['PercentChange']) >= self.percent_threshold and \
                                abs(collectedData_pair2.iloc[-1]['PercentChange']) >= self.percent_threshold and \
                                currency_pair not in self.signaled_pair and \
                                abs(abs(collectedData_pair1.iloc[-1]['PercentChange']) - abs(
                                    collectedData_pair2.iloc[-1]['PercentChange'])) <= 0.02:

                            self.signaled_pair.append(currency_pair)
                            self.negative_signals.configure(state='normal')
                            self.negative_signals.insert(END, f"[+] {current_time}: {currency_pair}, buys here, "
                                                              f"{self.check_timer(timeFrame)}, "
                                                              f"{round(collectedData_pair1.iloc[-1]['PercentChange'], 2)}, "
                                                              f"{round(collectedData_pair2.iloc[-1]['PercentChange'], 2)}\n")
                            self.negative_signals.see("end")
                            self.negative_signals.configure(state="disabled")
                            print(currency_pair, collectedData_pair1.iloc[-1]['PercentChange'],
                                  collectedData_pair2.iloc[-1]['PercentChange'], self.check_timer(timeFrame))
                            playsound(self.sound_file)

                        elif collectedData_pair1.iloc[-1]['PercentChange'] > 0 and \
                                collectedData_pair2.iloc[-1]['PercentChange'] > 0 and \
                                abs(collectedData_pair1.iloc[-1]['PercentChange']) >= self.percent_threshold and \
                                abs(collectedData_pair2.iloc[-1]['PercentChange']) >= self.percent_threshold and \
                                currency_pair not in self.signaled_pair and \
                                abs(abs(collectedData_pair1.iloc[-1]['PercentChange']) - abs(
                                    collectedData_pair2.iloc[-1]['PercentChange'])) <= 0.02:

                            self.signaled_pair.append(currency_pair)
                            self.negative_signals.configure(state='normal')
                            self.negative_signals.insert(END, f"[+] {current_time}: {currency_pair}, Sells here!, "
                                                              f"{self.check_timer(timeFrame)}, "
                                                              f"{round(collectedData_pair1.iloc[-1]['PercentChange'], 2)}, "
                                                              f"{round(collectedData_pair2.iloc[-1]['PercentChange'], 2)}\n")
                            self.negative_signals.see("end")
                            self.negative_signals.configure(state="disabled")
                            print(currency_pair, collectedData_pair1.iloc[-1]['PercentChange'],
                                  collectedData_pair2.iloc[-1]['PercentChange'], self.check_timer(timeFrame))
                            playsound(self.sound_file)

                    except TypeError:
                        pass

            negative_check(self.daily_cs[1], self.metaInit.TIMEFRAME_D1)

            self.winInit.after(3000, self.signal_generator)

    def check_timer(self, time_frame):
        if time_frame == self.metaInit.TIMEFRAME_D1:
            return "Daily"

        elif time_frame == self.metaInit.TIMEFRAME_H12:
            return "12 Hour"

        elif time_frame == self.metaInit.TIMEFRAME_H8:
            return "8 Hour"

        elif time_frame == self.metaInit.TIMEFRAME_H6:
            return "6 Hour"

        elif time_frame == self.metaInit.TIMEFRAME_H4:
            return "4 Hour"


if __name__ == '__main__':
    WindowClass()
