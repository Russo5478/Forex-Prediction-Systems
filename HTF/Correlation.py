import time
import MetaTrader5 as mT5
from tkinter import Tk, Frame, Label, Button, Toplevel
from tkinter.ttk import Progressbar, Notebook, Combobox
from threading import Thread
from queue import Queue
# import ttkbootstrap as ttk


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


def metatrader_initializer(func):
    def wrapper(*args, **kwargs):
        mT5.initialize()
        result = func(*args, **kwargs)
        mT5.shutdown()
        return result
    return wrapper


class MainWindow:
    def __init__(self, winInit):
        self.terminal = mT5
        self.winInit = winInit
        self.progressQueue = Queue()
        self.windowWidth = 1300
        self.windowHeight = 750

        self.account_check = False
        self.account_ID = None
        self.account_leverage = None
        self.account_balance = None
        self.terminal_ping = None
        self.new_position_window = None

        self.window_settings()
        self.status_bar()
        self.info_bar()
        self.main_content()

    def window_settings(self):
        self.winInit.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.winInit.title("Forex correlation | Negative | Positive")
        self.winInit.resizable(False, False)
        center(self.winInit)

    def status_bar(self):
        status_frame = Frame(self.winInit)
        status_frame.configure(background="white")
        status_frame.place(x=0, y=0, width=self.windowWidth, height=160)

        self.account_info_tab(status_frame)
        self.risk_meter_tab(status_frame)

    def account_info_tab(self, parent_widget):
        basic_info_frame = Frame(parent_widget)
        basic_info_frame.configure(highlightcolor="black", highlightbackground="black", highlightthickness=1)
        basic_info_frame.place(x=20, y=10, width=250, height=140)

        label_font = ("Tahoma", 11, "bold")
        value_font = ("Tahoma", 11)

        header_frame = Frame(basic_info_frame)
        header_frame.configure(bg="#729DD1")
        header_frame.place(x=0, y=0, width=248, height=25)

        header_title = Label(header_frame)
        header_title.configure(text="Account Information", fg="#fff", bg="#729DD1", font=("yu gothic ui", 11, "bold"))
        header_title.place(x=45, y=0)

        accountID_label = Label(basic_info_frame)
        accountID_label.configure(text="ID:", font=label_font)
        accountID_label.place(x=10, y=30)

        accountID_label_value = Label(basic_info_frame)
        accountID_label_value.configure(text="N/A", font=value_font)
        accountID_label_value.place(x=40, y=30)

        accountLeverage_label = Label(basic_info_frame)
        accountLeverage_label.configure(text="Leverage:", font=label_font)
        accountLeverage_label.place(x=10, y=55)

        accountLeverage_label_value = Label(basic_info_frame)
        accountLeverage_label_value.configure(text="N/A", font=value_font)
        accountLeverage_label_value.place(x=90, y=55)

        accountBal_label = Label(basic_info_frame)
        accountBal_label.configure(text="Balance:", font=label_font)
        accountBal_label.place(x=10, y=80)

        accountBal_label_value = Label(basic_info_frame)
        accountBal_label_value.configure(text="N/A", font=value_font)
        accountBal_label_value.place(x=80, y=80)

        accountPing_label = Label(basic_info_frame)
        accountPing_label.configure(text="Speed:", font=label_font)
        accountPing_label.place(x=10, y=105)

        accountPing_label_value = Label(basic_info_frame)
        accountPing_label_value.configure(text="N/A", font=value_font)
        accountPing_label_value.place(x=70, y=105)

        def update_account_info():
            if self.account_check:
                accountID_label_value.configure(text=self.account_ID)
                accountLeverage_label_value.configure(text=self.account_leverage)
                accountBal_label_value.configure(text=self.account_balance)
                accountPing_label_value.configure(text=self.terminal_ping)

            else:
                self.winInit.after(10, update_account_info)

        self.winInit.after(10, update_account_info)

    def risk_meter_tab(self, parent_widget):
        risk_info_frame = Frame(parent_widget)
        risk_info_frame.configure(highlightcolor="black", highlightbackground="black", highlightthickness=1)
        risk_info_frame.place(x=500, y=10, width=200, height=140)

        risk_label = Label(risk_info_frame)
        risk_label.configure(text="100%", font=("yu gothic ui", 60, "bold"), fg="red")
        risk_label.place(x=5, y=15)

        header_frame = Frame(risk_info_frame)
        header_frame.configure(bg="#729DD1")
        header_frame.place(x=0, y=0, width=198, height=25)

        header_title = Label(header_frame)
        header_title.configure(text="Trade Addition Risk", fg="#fff", bg="#729DD1", font=("yu gothic ui", 11, "bold"))
        header_title.place(x=30, y=0)

    def main_content(self):
        separator_frame = Frame(self.winInit)
        separator_frame.configure(background="black", width=self.windowWidth)
        separator_frame.place(x=0, y=160, height=5)

        tabbing_widget = Notebook(self.winInit)
        tab_1 = Frame(tabbing_widget)
        tab_3 = Frame(tabbing_widget)

        tabbing_widget.add(tab_1, text='Open Trades')
        tabbing_widget.add(tab_3, text='Market Overview')
        tabbing_widget.place(x=0, y=165, width=self.windowWidth, height=self.windowHeight-195)

        self.trades_section(tab_1)

    def trades_section(self, master_widget):
        def position_label_based_on_text(text, label, y_axis):
            num_characters = len(text)
            if float(text) < 0.00:
                label.configure(fg="red")

            elif float(text) > 0.00:
                label.configure(fg="green")

            else:
                label.configure(fg="grey")

            if num_characters <= 7:
                x_placement = 220 - num_characters * 5
                label.configure(text=text)
                label.place(x=x_placement, y=y_axis)

            else:
                x_placement = 180 - num_characters * 5
                label.configure(text=text)
                label.place(x=x_placement, y=y_axis)

        def trade_display(parent_widget, tickets: list, pairs: list, coordinates: list):
            trade_frame = Frame(parent_widget)
            trade_frame.configure(highlightbackground="black", highlightthickness=1)
            trade_frame.place(x=coordinates[0], y=coordinates[1], width=300, height=130)

            header_frame = Frame(trade_frame)
            header_frame.configure(background="#729DD1")
            header_frame.place(x=0, y=0, width=298, height=25)

            footer_frame = Frame(trade_frame)
            footer_frame.configure(background="#729DD1")
            footer_frame.place(x=0, y=100, width=298, height=28)

            frame_id = Label(header_frame)
            frame_id.configure(text=f"Ticket Numbers: (1) {tickets[0]}, (2) {tickets[1]}")
            frame_id.place(x=10, y=2)

            first_pair = Label(trade_frame)
            first_pair.configure(text=f"{pairs[0]}", font=("yu gothic ui", 16, "bold"))
            first_pair.place(x=10, y=25)

            second_pair = Label(trade_frame)
            second_pair.configure(text=f"{pairs[1]}", font=("yu gothic ui", 16, "bold"))
            second_pair.place(x=10, y=60)

            profit_label = Label(trade_frame)
            profit_label.configure(font=("yu gothic ui", 20, "bold"))
            profit_label.place(x=200, y=30)

            position_label_based_on_text("-10.00", profit_label, 40)

        trade_display(master_widget, [203944555, 439993994], ['XAUUSD', 'EURUSD'], [20, 100])
        trade_display(master_widget, [203944555, 439993994], ['AUDUSD', 'USDCAD'], [20, 400])

        top_frame = Frame(master_widget)
        top_frame.configure(bg="red")
        top_frame.place(x=0, y=0, width=self.windowWidth, height=35)

        def create_new_position():
            if not self.new_position_window:
                tradeWindow = Toplevel(self.winInit)
                self.new_position_window = tradeWindow
                tradeWindow.geometry("570x500")
                tradeWindow.title("Create New Position")
                center(tradeWindow)

                separator_frame = Frame(tradeWindow)
                separator_frame.configure(background="black")
                separator_frame.place(x=280, y=10, width=5, height=400)

                pair1_label = Label(tradeWindow)
                pair1_label.configure(text="FX Pair 1", font=('yu gothic ui', 11, 'bold'))
                pair1_label.place(x=20, y=21)

                pair1_combo = Combobox(tradeWindow, font=('yu gothic ui', 12))
                pair1_combo.configure(state='readonly')
                # pair1_combo['values'] = account_types
                # pair1_combo.configure(textvariable=self.account_type_value)
                pair1_combo.place(x=100, y=20, width=150)

                pair2_label = Label(tradeWindow)
                pair2_label.configure(text="FX Pair 2", font=('yu gothic ui', 11, 'bold'))
                pair2_label.place(x=20, y=71)

                pair2_combo = Combobox(tradeWindow, font=('yu gothic ui', 12))
                pair2_combo.configure(state='readonly')
                # pair2_combo['values'] = account_types
                # pair2_combo.configure(textvariable=self.account_type_value)
                pair2_combo.place(x=100, y=70, width=150)

                timeframe_label = Label(tradeWindow)
                timeframe_label.configure(text="Timeframe", font=('yu gothic ui', 11, 'bold'))
                timeframe_label.place(x=19, y=121)

                timeframe_combo = Combobox(tradeWindow, font=('yu gothic ui', 12))
                timeframe_combo.configure(state='readonly')
                # timeframe_combo['values'] = account_types
                # timeframe_combo.configure(textvariable=self.account_type_value)
                timeframe_combo.place(x=100, y=120, width=150)

                data_check = Button(tradeWindow)
                data_check.configure(text="Check Details", fg="#fff", bg="blue", font=('yu gothic ui', 12, 'bold'),
                                     relief="solid")
                data_check.place(x=80, y=170, width=110, height=30)

                border_frame = Frame(tradeWindow)
                border_frame.configure(background="black")
                border_frame.place(x=10, y=220, width=260, height=2)

                pair_corr_label = Label(tradeWindow)
                pair_corr_label.configure(text="Pair Correlation:", font=('yu gothic ui', 12, 'bold'))
                pair_corr_label.place(x=20, y=240)

            else:
                self.new_position_window.focus_set()

        create_trade = Button(top_frame)
        create_trade.configure(text="Create Trade", command=create_new_position)
        create_trade.place(x=1200, y=5)

        close_positions = Button(top_frame)
        close_positions.configure(text="Close All")
        close_positions.place(x=1125, y=5)

    def info_bar(self):
        infoHeight = 30
        info_frame = Frame(self.winInit)
        info_frame.configure(background="green")
        info_frame.place(x=0, y=self.windowHeight-infoHeight, width=self.windowWidth, height=infoHeight)

        progress_bar = Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
        progress_bar.place(x=50, y=10, height=10)

        def update_progress_bar():
            while True:
                progress = self.progressQueue.get()
                if progress is None:
                    break
                progress_bar["value"] = progress
                self.winInit.update_idletasks()

            progress_bar.place(x=10000, y=10000)

        def load_functions():
            status_thread = Thread(target=self.start_bar)
            status_thread.start()
            self.winInit.after(100, update_progress_bar)

        # load_functions()

    def start_bar(self):
        functions = [self.terminal_info, self.terminal_info]
        for step in range(len(functions)):
            functions[step]()
            # Report progress back to the main thread
            progress = (step + 1) * 100 // len(functions)
            self.progressQueue.put(progress)

        # Indicate that the task is done
        self.progressQueue.put(None)

    @metatrader_initializer
    def terminal_info(self):
        terminal_info = self.terminal.terminal_info()
        account_info = self.terminal.account_info()

        self.account_ID = account_info[0]
        self.account_leverage = "1:" + str(account_info[2])
        self.account_balance = str(account_info[10]) + " " + str(account_info[-2])
        self.terminal_ping = str(int(terminal_info[13]/1000)) + " ms"

        self.account_check = True


def load_window():
    window = Tk()
    MainWindow(window)
    window.mainloop()


if __name__ == '__main__':
    load_window()
