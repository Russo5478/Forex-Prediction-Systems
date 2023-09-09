import time

from pandas import DataFrame, to_datetime
from ttkbootstrap import Window, Meter
import MetaTrader5 as mT5
from tkinter import Tk, Frame, Label, Button, Toplevel, Entry, END, Checkbutton, IntVar, messagebox, Text, Canvas
from tkinter.ttk import Notebook, Combobox
from threading import Thread


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
        self.windowHeight = 650
        self.windowWidth = 1100
        self.maximumSpread = 35
        self.collected_data = None
        self.meters = []
        self.meter_frames = []

        self.forex_pairs = ["GBPUSD", "USDCHF", "AUDUSD", "AUDCHF", "EURUSD", "EURGBP", "NZDUSD", "EURCHF",
                            "GBPCHF", "CADCHF", "NZDCHF", "GBPJPY", "USDJPY", "CADJPY", "NZDJPY", "EURNZD",
                            "EURCAD", "USDCAD", "GBPAUD", "GBPCAD", "GBPNZD", "NZDCAD", "XAUUSD", "XAUEUR",
                            "AUDJPY", "AUDNZD", "EURAUD", "AUDCAD", "EURJPY", "CHFJPY"]
        self.symbols = ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF", "XAU"]

        self.window_settings()
        self.winInit.mainloop()

    def window_settings(self):
        self.winInit.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.winInit.title("Forex Correlation | Signals Only")
        self.winInit.resizable(False, False)

        center(self.winInit)

        daily_thread = Thread(target=self.plot_meters, args=(self.metaInit.TIMEFRAME_D1,))
        self.winInit.after(1000, daily_thread.start)
        self.window_widgets()

        def on_closing():
            print("perfom closing activities")
            self.winInit.destroy()

        self.winInit.protocol("WM_DELETE_WINDOW", on_closing)

    def window_widgets(self):
        side_frame_width = 250
        side_frame = Frame(self.winInit)
        # side_frame.configure(highlightbackground="white", highlightthickness=2)
        side_frame.place(x=0, y=0, width=side_frame_width, height=self.windowHeight)

        separator(self.winInit, "#fff", [2, self.windowHeight], [250, 0])

        plot_settings_frame = Frame(side_frame)
        plot_settings_frame.place(x=0, y=0, width=side_frame_width, height=150)

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
        # plot_time_choice.configure(textvariable=self.account_type_value)
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
            collectedData = self.dataCollection(forexPair=str(pair), timeFrame=time_frame)
            collectedData['PercentChange'] = collectedData['close'].pct_change() * 100
            collectedData = collectedData.dropna()
            combinedData[pair] = collectedData['PercentChange']
            self.metaInit.shutdown()

        self.collected_data = combinedData.T
        frameCoordinates = [[270, 30], [270, 250], [270, 470], [550, 30], [550, 250], [550, 470], [830, 30], [830, 250],
                            [830, 470]]
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


if __name__ == '__main__':
    WindowClass()
