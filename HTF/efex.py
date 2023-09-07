import time
import tkinter
from pandas import DataFrame, to_datetime
import MetaTrader5 as mT5
from tkinter import Tk, Frame, Label, Button, Toplevel, Entry, END, Checkbutton, IntVar, messagebox
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


class MainWindow:
    def __init__(self):
        self.winInit = Tk()
        self.windowWidth = 515
        self.windowHeight = 600
        self.mainNotebook = None
        self.metaInit = mT5
        self.metaConnected = False
        self.connection_status_label = None
        self.loaded_window = None
        self.default_selection = IntVar()
        self.first_tab = None
        self.forex_pairs = ["GBPUSD", "USDCHF", "AUDUSD", "AUDCHF", "EURUSD", "EURGBP", "NZDUSD", "EURCHF", "GBPCHF",
                            "CADCHF", "NZDCHF", "AUDJPY", "CHFJPY", "EURJPY", "GBPJPY", "USDJPY", "USDCAD", "AUDNZD",
                            "AUDCAD", "EURAUD", "EURNZD", "EURCAD", "XAUEUR", "XAUUSD"]

        self.window_settings()
        self.winInit.mainloop()

    def window_settings(self):
        self.winInit.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.winInit.title("Forex Correlation | with AI")
        self.winInit.resizable(False, False)

        self.mainNotebook = Notebook(self.winInit)
        mainView = Frame(self.mainNotebook)
        self.first_tab = mainView

        self.mainNotebook.add(mainView, text='Open Trades')
        self.mainNotebook.place(x=0, y=0, width=self.windowWidth, height=self.windowHeight)

        self.connection_status_label = Label(self.winInit)
        self.connection_status_label.configure(text="not connected", fg="red")
        self.connection_status_label.place(x=self.windowWidth - 100, y=1)

        status_thread = Thread(target=self.initialize_metatrader)
        self.winInit.after(1000, status_thread.start)

        def load_creation_tool():
            if not self.loaded_window:
                trade_creator = Toplevel()
                self.loaded_window = trade_creator
                trade_creator.geometry(f'{self.windowWidth}x{400}')
                trade_creator.title("Create Setup | Live trading | Signal Generation")
                center(trade_creator)

                self.trade_settings(trade_creator)

            else:
                try:
                    self.loaded_window.focus_set()

                except tkinter.TclError:
                    self.loaded_window = None
                    trade_creator = Toplevel()
                    self.loaded_window = trade_creator
                    trade_creator.geometry(f'{self.windowWidth}x{400}')
                    trade_creator.title("Create Setup | Live trading | Signal Generation")
                    center(trade_creator)

                    self.trade_settings(trade_creator)

        create_tracker = Button(mainView, command=load_creation_tool)
        create_tracker.configure(text="[+] create", relief="solid", fg="white", bg="green")
        create_tracker.place(x=self.windowWidth - 100, y=20)

        center(self.winInit)

    def trade_settings(self, mainFrame):
        strategy_selection = Label(mainFrame)
        strategy_selection.configure(text="Choose Strategy", font=('yu gothic ui', 10, 'bold'))
        strategy_selection.place(x=10, y=10)

        strategy_choice = Combobox(mainFrame, font=('yu gothic ui', 11))
        strategy_choice['values'] = ["Margin Exit", "Greedy Exit"]
        strategy_choice.set("Margin Exit")
        strategy_choice.configure(state='disabled', justify='center')
        # strategy_choice.configure(textvariable=self.account_type_value)
        strategy_choice.place(x=130, y=10, width=130)

        entry_selection = Label(mainFrame)
        entry_selection.configure(text="Entry %", font=('yu gothic ui', 10, 'bold'))
        entry_selection.place(x=280, y=10)

        threshold_entry = Entry(mainFrame)
        threshold_entry.insert(END, "0.05")
        threshold_entry.configure(state="readonly", font=('yu gothic ui', 11), justify="center", relief="solid")
        threshold_entry.place(x=360, y=10, width=140, height=25)

        profit_label = Label(mainFrame)
        profit_label.configure(text="Profit (pips)", font=('yu gothic ui', 10, 'bold'))
        profit_label.place(x=40, y=45)

        profit_entry = Entry(mainFrame)
        profit_entry.insert(END, "10")
        profit_entry.configure(state="readonly", font=('yu gothic ui', 11), justify="center", relief="solid")
        profit_entry.place(x=130, y=45, width=130, height=25)

        time_selection = Label(mainFrame)
        time_selection.configure(text="Timeframe", font=('yu gothic ui', 10, 'bold'))
        time_selection.place(x=50, y=80)

        time_choice = Combobox(mainFrame, font=('yu gothic ui', 10))
        time_choice['values'] = ["1 Hour", "2 Hour", "3 Hour", "4 Hour", "8 Hour", "Daily", "Weekly"]
        time_choice.set("Daily")
        time_choice.configure(state='disabled', justify='center')
        # time_choice.configure(textvariable=self.account_type_value)
        time_choice.place(x=130, y=80, width=130, height=28)

        type_selection = Label(mainFrame)
        type_selection.configure(text="Setup Type", font=('yu gothic ui', 10, 'bold'))
        type_selection.place(x=280, y=45)

        type_choice = Combobox(mainFrame, font=('yu gothic ui', 10))
        type_choice['values'] = ["Live Trading", "Signals Only"]
        type_choice.set("Signals Only")
        type_choice.configure(state='disabled', justify='center')
        # type_choice.configure(textvariable=self.account_type_value)
        type_choice.place(x=360, y=45, width=140, height=28)
        
        volume_selection = Label(mainFrame)
        volume_selection.configure(text="Volume", font=('yu gothic ui', 10, 'bold'))
        volume_selection.place(x=280, y=80)

        volume_entry = Entry(mainFrame)
        volume_entry.insert(END, "0.01")
        volume_entry.configure(state="readonly", font=('yu gothic ui', 11), justify="center", relief="solid")
        volume_entry.place(x=360, y=80, width=140, height=25)

        default_values = Checkbutton(mainFrame)
        default_values.configure(text="Defaults", font=('yu gothic ui', 9), variable=self.default_selection)
        default_values.place(x=430, y=110)
        default_values.toggle()

        def checkbutton_toggle(*args):
            try:
                if self.default_selection.get() == 0:
                    strategy_choice.configure(state="readonly")
                    profit_entry.configure(state="normal")
                    threshold_entry.configure(state="normal")
                    type_choice.configure(state="readonly")
                    time_choice.configure(state="readonly")
                    volume_entry.configure(state="normal")

                else:
                    strategy_choice.set("Margin Exit")
                    type_choice.set("Signals Only")
                    time_choice.set("Daily")
                    strategy_choice.configure(state="disabled")
                    type_choice.configure(state="disabled")
                    time_choice.configure(state="disabled")

                    profit_entry.delete(0, END)
                    profit_entry.insert(END, "10")
                    profit_entry.configure(state="readonly")

                    threshold_entry.delete(0, END)
                    threshold_entry.insert(END, "0.05")
                    threshold_entry.configure(state="readonly")
                    
                    volume_entry.delete(0, END)
                    volume_entry.insert(END, "0.01")
                    volume_entry.configure(state="readonly")

            except tkinter.TclError:
                pass

        self.default_selection.trace("w", checkbutton_toggle)

        pair1_selection = Label(mainFrame)
        pair1_selection.configure(text="Pair 1", font=('yu gothic ui', 10, 'bold'))
        pair1_selection.place(x=10, y=152)

        pair1_choice = Combobox(mainFrame, font=('yu gothic ui', 10))
        pair1_choice['values'] = self.forex_pairs
        pair1_choice.set(self.forex_pairs[0])
        pair1_choice.configure(state='readonly', justify='center')
        # pair1_choice.configure(textvariable=self.account_pair1_value)
        pair1_choice.place(x=60, y=150, width=130, height=28)

        pair2_selection = Label(mainFrame)
        pair2_selection.configure(text="Pair 2", font=('yu gothic ui', 10, 'bold'))
        pair2_selection.place(x=220, y=152)

        pair2_choice = Combobox(mainFrame, font=('yu gothic ui', 10))
        pair2_choice['values'] = self.forex_pairs
        pair2_choice.set(self.forex_pairs[1])
        pair2_choice.configure(state='readonly', justify='center')
        # pair2_choice.configure(textvariable=self.account_pair2_value)
        pair2_choice.place(x=270, y=150, width=130, height=28)

        def forex_valuation():
            check_btn.configure(state="disabled")
            first_pair = pair1_choice.get()
            second_pair = pair2_choice.get()
            time_value = time_choice.get()

            if first_pair != second_pair:
                loading_label = Label(results_frame, bg="white")
                loading_label.configure(text="Wait! Calculating correlation....", font=("yu gothic ui", 12, "bold"))
                loading_label.place(x=100, y=30)

                def collection():
                    converted_time, data_count = self.time_converter(time_value)
                    first_pair_data = self.dataCollection(first_pair, converted_time, endIndex=data_count)
                    second_pair_data = self.dataCollection(second_pair, converted_time, endIndex=data_count)

                    if len(first_pair_data) > 1 and len(second_pair_data) > 1:
                        self.metaInit.initialize()
                        firstSpread = self.metaInit.symbol_info(first_pair)[12]
                        firstPrice = round(self.metaInit.symbol_info_tick(first_pair)[1], 5)

                        secondSpread = self.metaInit.symbol_info(second_pair)[12]
                        secondPrice = round(self.metaInit.symbol_info_tick(second_pair)[1], 5)
                        self.metaInit.shutdown()

                        combinedData = DataFrame()
                        first_pair_data['PercentChange'] = first_pair_data['close'].pct_change() * 100
                        first_pair_data = first_pair_data.dropna()
                        combinedData[first_pair] = first_pair_data['PercentChange']

                        second_pair_data['PercentChange'] = second_pair_data['close'].pct_change() * 100
                        second_pair_data = second_pair_data.dropna()
                        combinedData[second_pair] = second_pair_data['PercentChange']

                        correlationMatrix = combinedData.corr()
                        correlation_value = round(correlationMatrix.loc[first_pair, second_pair], 2)

                        loading_label.configure(fg="white")

                        first_pair_label = Label(results_frame)
                        first_pair_label.configure(text=first_pair, bg="white", font=("yu gothic ui", 12, "bold"))
                        first_pair_label.place(x=30, y=5)

                        separator(results_frame, "black", [105, 2], [10, 30])

                        first_pair_spl = Label(results_frame, bg="white")
                        first_pair_spl.configure(text=f"Spread: {firstSpread}", font=("yu gothic ui", 10, "bold"))
                        first_pair_spl.place(x=20, y=35)

                        first_pair_pr = Label(results_frame, bg="white")
                        first_pair_pr.configure(text=f"Price: {firstPrice}", font=("yu gothic ui", 10, "bold"))
                        first_pair_pr.place(x=20, y=55)

                        first_pair_dl = Label(results_frame, bg="white")
                        first_pair_dl.configure(text=f"Data: {len(first_pair_data)}", font=("yu gothic ui", 10, "bold"))
                        first_pair_dl.place(x=20, y=75)

                        separator(results_frame, "black", [2, 90], [130, 10])

                        second_pair_label = Label(results_frame)
                        second_pair_label.configure(text=second_pair, bg="white", font=("yu gothic ui", 12, "bold"))
                        second_pair_label.place(x=165, y=5)

                        separator(results_frame, "black", [105, 2], [148, 30])
                        
                        second_pair_spl = Label(results_frame, bg="white")
                        second_pair_spl.configure(text=f"Spread: {secondSpread}", font=("yu gothic ui", 10, "bold"))
                        second_pair_spl.place(x=160, y=35)

                        second_pair_pr = Label(results_frame, bg="white")
                        second_pair_pr.configure(text=f"Price: {secondPrice}", font=("yu gothic ui", 10, "bold"))
                        second_pair_pr.place(x=160, y=55)

                        second_pair_dl = Label(results_frame, bg="white")
                        second_pair_dl.configure(text=f"Data: {len(second_pair_data)}", font=("yu gothic ui", 10, "bold"))
                        second_pair_dl.place(x=160, y=75)

                        separator(results_frame, "black", [2, 90], [270, 10])
                        
                        result_pair_label = Label(results_frame)
                        result_pair_label.configure(text="Results", bg="white", font=("yu gothic ui", 12, "bold"))
                        result_pair_label.place(x=310, y=5)

                        separator(results_frame, "black", [105, 2], [290, 30])
                        
                        average_pair_spl = Label(results_frame, bg="white")
                        average_pair_spl.configure(text=f"Avg Spread: {(firstSpread+secondSpread)/2}",
                                                   font=("yu gothic ui", 10, "bold"))
                        average_pair_spl.place(x=290, y=35)
                        
                        corr_pair_spl = Label(results_frame, bg="white")
                        corr_pair_spl.configure(text=f"Correlation: {str((correlation_value*100))}%",
                                                font=("yu gothic ui", 10, "bold"))
                        corr_pair_spl.place(x=287, y=55)
                        
                        conclusion_label = Label(results_frame, bg="white")
                        conclusion_label.configure(text="Conclusion:", font=("yu gothic ui", 10, "bold"))
                        conclusion_label.place(x=120, y=110)

                        reco_result = Label(results_frame, bg="white")
                        reco_result.configure(font=("yu gothic ui", 10, "bold"), text="recommended", fg="green")
                        reco_result.place(x=1000, y=1000)

                        not_reco_result = Label(results_frame, bg="white")
                        not_reco_result.configure(font=("yu gothic ui", 10, "bold"), text="not recommended", fg="red")
                        not_reco_result.place(x=1000, y=1000)

                        if (firstSpread+secondSpread)/2 <= 40 and abs(correlation_value) >= 0.7:
                            start_btn.configure(state="normal")
                            reco_result.place(x=195, y=110, width=150)

                        else:
                            start_btn.configure(state="disabled")
                            not_reco_result.place(x=200, y=110)

                        check_btn.configure(state="normal")
                        
                    else:
                        messagebox.showwarning("Data Error", "Could not retrieve all information!")

                collection_thread = Thread(target=collection)
                collection_thread.start()

            else:
                messagebox.showwarning("Pair Selection Error", "Choose different pairs in your selection!")
                self.loaded_window.focus_set()
        
        check_btn = Button(mainFrame, command=forex_valuation)
        check_btn.configure(text="Check", fg="white", bg="orange", relief="solid", font=('yu gothic ui', 11, "bold"))
        check_btn.place(x=440, y=145)

        def start_actions():
            if type_choice.get() == "Signals Only":
                timeframe_value, num_data = self.time_converter(time_choice.get())
                first_pair = pair1_choice.get()
                second_pair = pair2_choice.get()
                threshold = threshold_entry.get()

                try:
                    if float(threshold) > 0.01:
                        self.loaded_window.destroy()
                        self.signal_center([first_pair, second_pair], timeframe_value, threshold)

                except ValueError:
                    messagebox.showerror("Entry Violation", "Make sure you have entered float number only!")
                    self.loaded_window.focus_set()

        start_btn = Button(mainFrame, command=start_actions)
        start_btn.configure(text="Start", fg="white", bg="green", relief="solid", font=('yu gothic ui', 12, "bold"),
                            state="disabled")
        start_btn.place(x=360, y=mainFrame.winfo_height() - 55, width=100)

        separation_frame = Frame(mainFrame)
        separation_frame.configure(bg="black")
        separation_frame.place(x=10, y=135, width=mainFrame.winfo_width() - 20, height=3)
        
        results_frame = Frame(mainFrame)
        results_frame.configure(bg="white", highlightbackground="black", highlightthickness=1, highlightcolor="black")
        results_frame.place(x=50, y=190, width=mainFrame.winfo_width() - 100, height=140)

    def signal_center(self, pairs: list, chartTime, entryPoint):
        def percent_calculator(openValue, currentValue):
            return round(((currentValue - openValue) / openValue) * 100, 2)

        while True:
            pair1Open = self.dataCollection(pairs[0], chartTime, startIndex=1, endIndex=3).iloc[-1]['close']
            pair2Open = self.dataCollection(pairs[1], chartTime, startIndex=1, endIndex=3).iloc[-1]['close']

            pair1Close = self.dataCollection(pairs[0], chartTime, startIndex=0, endIndex=3).iloc[-1]['close']
            pair2Close = self.dataCollection(pairs[1], chartTime, startIndex=0, endIndex=3).iloc[-1]['close']

            pair1_change = percent_calculator(pair1Open, pair1Close)
            pair2_change = percent_calculator(pair2Open, pair2Close)

            if abs(pair1_change) >= float(entryPoint) and abs(pair2_change) >= float(entryPoint):
                print("Found")
                break

            else:
                print("[-] No signal")
                time.sleep(3)

    def initialize_metatrader(self):
        try:
            if not self.metaConnected:
                self.metaInit.initialize()
                self.metaInit.shutdown()
                self.metaConnected = True
                self.connection_status_label.configure(text="connected", fg="green")
                self.connection_status_label.place(x=self.windowWidth - 80, y=1)
                exit()

        except ValueError:
            pass

    def dataCollection(self, forexPair: str, timeFrame: object, startIndex: int = 1, endIndex: int = 100000):
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

    def time_converter(self, specified_time: str):
        if specified_time == "1 Hour":
            return self.metaInit.TIMEFRAME_H1, 4800

        if specified_time == "2 Hour":
            return self.metaInit.TIMEFRAME_H2, 2400

        if specified_time == "3 Hour":
            return self.metaInit.TIMEFRAME_H3, 1600

        if specified_time == "4 Hour":
            return self.metaInit.TIMEFRAME_H4, 1200

        if specified_time == "8 Hour":
            return self.metaInit.TIMEFRAME_H8, 600

        if specified_time == "Daily":
            return self.metaInit.TIMEFRAME_D1, 200

        if specified_time == "Weekly":
            return self.metaInit.TIMEFRAME_W1, 30


if __name__ == '__main__':
    MainWindow()
