from ctypes import windll as window_dpi
from tkinter import Tk, Label, Button, StringVar, Entry, END, Frame
from tkinter.ttk import Combobox
import MetaTrader5 as Mt5
from pandas import DataFrame, to_datetime, Timedelta
from threading import Thread
from tkcalendar import Calendar
from datetime import datetime

window_dpi.shcore.SetProcessDpiAwareness(1)


def convert_date_format(date_string: str):
    # Convert input date string to datetime object
    date_object = datetime.strptime(date_string, '%m/%d/%y')

    # Get day of the week (e.g., Tuesday)
    day_of_week = date_object.strftime('%A')

    # Get day of the month (e.g., 9th)
    day_of_month = date_object.strftime('%d')
    if day_of_month.endswith('1') and day_of_month != '11':
        day_suffix = 'st'
    elif day_of_month.endswith('2') and day_of_month != '12':
        day_suffix = 'nd'
    elif day_of_month.endswith('3') and day_of_month != '13':
        day_suffix = 'rd'
    else:
        day_suffix = 'th'

    # Get month (e.g., August)
    month = date_object.strftime('%B')

    # Get year (e.g., 2023)
    year = date_object.strftime('%Y')

    formatted_date = f"{day_of_week} {day_of_month}{day_suffix} {month} {year}"
    return formatted_date


def convert_to_timestamp(formatted_date_string):
    date_form = '%Y-%m-%d %H:%M:%S'
    dt_object = datetime.strptime(formatted_date_string, date_form)
    timestamp = int(dt_object.timestamp())
    return timestamp


def change_date_format(formatted_date_string):
    date_object = datetime.strptime(formatted_date_string, '%A %dth %B %Y %H:%M')
    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date


def get_forward_time(current_time, step):
    vals = ['15 Minute', '30 Minute', '1 Hour', '2 Hour', '3 Hour', '4 Hour']

    if step == vals[0]:
        forward_time = current_time + Timedelta(minutes=15)

    elif step == vals[1]:
        forward_time = current_time + Timedelta(minutes=30)

    elif step == vals[2]:
        forward_time = current_time + Timedelta(hours=1)

    elif step == vals[3]:
        forward_time = current_time + Timedelta(hours=2)

    elif step == vals[4]:
        forward_time = current_time + Timedelta(hours=3)

    else:
        forward_time = current_time + Timedelta(hours=4)

    print(forward_time)

    return convert_to_timestamp(str(forward_time))


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("Prediction Script")
        self.geometry(f"{470}x{500}+{200}+{100}")
        self.dataframe = None

        self.create_widgets()

    def create_widgets(self):
        timeframe_label = Label(self, text="Select Timeframe: ")
        timeframe_label.place(x=20, y=20)

        timeframes_values = ['15 Minute', '30 Minute', '1 Hour', '2 Hour', '3 Hour', '4 Hour']
        time_frame_tracer = StringVar()

        timeframe_choice = Combobox(self)
        timeframe_choice.configure(state="readonly", textvariable=time_frame_tracer)
        timeframe_choice['values'] = timeframes_values
        timeframe_choice.place(x=130, y=20)

        def return_time(timer):
            if timer == timeframes_values[0]:
                return Mt5.TIMEFRAME_M15

            if timer == timeframes_values[1]:
                return Mt5.TIMEFRAME_M30

            if timer == timeframes_values[2]:
                return Mt5.TIMEFRAME_H1

            if timer == timeframes_values[3]:
                return Mt5.TIMEFRAME_H2

            if timer == timeframes_values[4]:
                return Mt5.TIMEFRAME_H3

            if timer == timeframes_values[5]:
                return Mt5.TIMEFRAME_H4

        def get_data_function():
            timeframe = timeframe_choice.get()

            if timeframe != '':
                get_data_btn.configure(state='disabled')
                mt5_time = return_time(timeframe)
                Mt5.initialize()

                ticks = Mt5.copy_rates_from_pos("XAUUSD", mt5_time, 1, 100000)
                ticks_data = DataFrame(ticks)
                ticks_data['time'] = to_datetime(ticks_data['time'], unit='s')
                ticks_data['time'] = to_datetime(ticks_data['time'], format='%Y-%m-%d')
                self.dataframe = ticks_data
                get_data_btn.configure(state='normal')

        def start_collection():
            thread = Thread(target=get_data_function)
            thread.start()

        get_data_btn = Button(self)
        get_data_btn.configure(text="Get Data", command=start_collection)
        get_data_btn.place(x=300, y=18)

        separator = Frame(self)
        separator.configure(width=450, background="black")
        separator.place(x=10, y=50, height=2)

        to_picker = Calendar(self, selectmode='day', maxdate=datetime.today())
        to_picker.place(x=20, y=60)

        hour_var = StringVar()
        minute_var = StringVar()

        hour_label = Label(self, text="Hour:")
        hour_label.place(x=300, y=60)

        hour_entry = Combobox(self, textvariable=hour_var)
        hour_entry.configure(state="readonly")
        hour_entry.place(x=300, y=80)

        minute_label = Label(self, text="Minute:")
        minute_label.place(x=300, y=130)

        minute_entry = Combobox(self, textvariable=minute_var)
        minute_entry.configure(state="readonly")
        minute_entry.place(x=300, y=150)

        def check_date_func():
            date_result.configure(state="normal")
            dates = convert_date_format(str(to_picker.get_date()))

            if time_frame_tracer.get() == timeframes_values[0] or time_frame_tracer.get() == timeframes_values[1]:
                hour_time = hour_var.get()
                minute_time = minute_var.get()

                if hour_time == '':
                    hour_time = '00'

                if minute_time == '':
                    minute_time = '00'

            else:
                hour_time = hour_var.get()

                if hour_time == '':
                    hour_time = '00'

                minute_time = '00'

            full_time = f'{hour_time}:{minute_time}'
            display_time = f'{dates} {full_time}'

            date_result.delete(0, END)
            date_result.insert(0, display_time)
            predict_btn.configure(state="normal")
            date_result.configure(state="disabled")

        check_button = Button(self)
        check_button.configure(text="CHECK DATE", command=check_date_func, relief="groove", state="disabled")
        check_button.place(x=330, y=200)

        date_label = Label(self)
        date_label.configure(text="Candle Date:")
        date_label.place(x=20, y=275)

        date_result = Entry(self)
        date_result.configure(state="readonly", font=('yu gothic ui', 13), justify="center", relief="solid")
        date_result.place(x=110, y=270, width=330)

        def prediction():
            prediction_candle = date_result.get()
            timestamped_date = change_date_format(prediction_candle)
            datetime_obj = datetime.strptime(timestamped_date, '%Y-%m-%d %H:%M:%S')
            date_part = datetime_obj.date()
            filtered_times = self.dataframe[self.dataframe['time'].dt.date == to_datetime(date_part).date()]
            adjusted_datetime = to_datetime(timestamped_date)

            hour_adjustments = [0, 1, 2]

            listed_items = filtered_times['time'].tolist()
            index = len(filtered_times)
            for adjustment in hour_adjustments:
                try:
                    adjusted_datetime += Timedelta(hours=adjustment)

                    first_item = listed_items[0]

                    time1 = datetime.strptime(str(first_item), '%Y-%m-%d %H:%M:%S')
                    time2 = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')

                    if time2 < time1:
                        correct_time = first_item

                    else:
                        correct_time = adjusted_datetime

                    index = listed_items.index(to_datetime(correct_time))
                    break

                except ValueError:
                    continue

            calculations(filtered_times, index)

        def calculations(items, index_val: int):
            items_time = items['time'].tolist()
            items_high = items['high'].tolist()
            items_low = items['low'].tolist()

            high_slopes = []
            low_slopes = []

            for i in range(0, len(items)):
                if i < index_val:
                    high_slope = (items_high[index_val] - items_high[i]) / (items_time[index_val].timestamp() - items_time[i].timestamp())

                    low_slope = (items_low[index_val] - items_low[i]) / (items_time[index_val].timestamp() - items_time[i].timestamp())

                    high_slopes.append(high_slope)
                    low_slopes.append(low_slope)

            avg_high_slope = sum(high_slopes) / len(high_slopes)
            avg_low_slope = sum(low_slopes) / len(low_slopes)

            forward_time = get_forward_time(items_time[index_val].to_pydatetime(), time_frame_tracer.get())

            predicted_high = (avg_high_slope * (forward_time - items_time[index_val].timestamp())) + items_high[index_val]
            predicted_low = (avg_low_slope * (forward_time - items_time[index_val].timestamp())) + items_low[index_val]

            print(f'Predicted high {round(predicted_high, 2)}, predicted low {round(predicted_low, 2)}')

        predict_btn = Button(self)
        predict_btn.configure(command=prediction, text="START", foreground="#fff", background="green", relief="solid",
                              state="disabled")
        predict_btn.place(x=220, y=310, width=50)

        def timeframe_react(*args):
            time_value = time_frame_tracer.get()
            check_button.configure(state="normal")

            def generate_custom_values(start, end, step):
                return [str(i).zfill(2) for i in range(start, end + 1, step)]
            
            if time_value == timeframes_values[0]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='normal')
                minute_entry.configure(state="readonly")
                minute_values = generate_custom_values(0, 59, 15)
                hour_values = generate_custom_values(0, 23, 1)

                hour_entry["values"] = hour_values
                minute_entry["values"] = minute_values

            if time_value == timeframes_values[1]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='normal')
                minute_entry.configure(state="readonly")
                minute_values = generate_custom_values(0, 59, 30)
                hour_values = generate_custom_values(0, 23, 1)

                hour_entry["values"] = hour_values
                minute_entry["values"] = minute_values

            if time_value == timeframes_values[2]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='disabled')
                hour_values = generate_custom_values(0, 23, 1)

                hour_entry["values"] = hour_values

            if time_value == timeframes_values[3]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='disabled')
                hour_values = generate_custom_values(0, 23, 2)

                hour_entry["values"] = hour_values

            if time_value == timeframes_values[4]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='disabled')
                hour_values = generate_custom_values(0, 23, 3)

                hour_entry["values"] = hour_values

            if time_value == timeframes_values[5]:
                hour_entry.set("00")
                minute_entry.set("00")
                minute_entry.configure(state='disabled')
                hour_values = generate_custom_values(0, 23, 4)

                hour_entry["values"] = hour_values

        time_frame_tracer.trace('w', timeframe_react)


if __name__ == '__main__':
    run_window = MainWindow()
    run_window.mainloop()
