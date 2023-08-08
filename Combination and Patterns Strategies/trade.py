import time
import MetaTrader5 as Metatrader


def initiate_trade(symbol_type, trade_type, stop_loss, pips):
    if trade_type.lower() == "buy":
        volume = 1.0
        price = Metatrader.symbol_info_tick(symbol_type).ask
        take_profit = price + pips

        send_request = {"action": Metatrader.TRADE_ACTION_DEAL,
                        "symbol": symbol_type,
                        "volume": volume,
                        "type": Metatrader.ORDER_TYPE_BUY,
                        "price": Metatrader.symbol_info_tick(symbol_type).ask,
                        "sl": stop_loss,
                        "tp": take_profit,
                        "type_time": Metatrader.ORDER_TIME_GTC,
                        "type_filling": Metatrader.ORDER_FILLING_IOC}
        res = Metatrader.order_send(send_request)
        time.sleep(5)
        print(res)

    elif trade_type.lower() == "sell":
        volume = 1.0
        price = Metatrader.symbol_info_tick(symbol_type).bid
        take_profit = price - pips

        send_request = {"action": Metatrader.TRADE_ACTION_DEAL,
                        "symbol": symbol_type,
                        "volume": volume,
                        "type": Metatrader.ORDER_TYPE_SELL,
                        "price": Metatrader.symbol_info_tick(symbol_type).bid,
                        "sl": stop_loss,
                        "tp": take_profit,
                        "type_time": Metatrader.ORDER_TIME_GTC,
                        "type_filling": Metatrader.ORDER_FILLING_IOC}
        res = Metatrader.order_send(send_request)
        time.sleep(5)
        print(res)
