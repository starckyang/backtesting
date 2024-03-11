import pandas
import matplotlib.pyplot as plt
import pandas as pd
from prettytable import PrettyTable
from data_grabber import Grabber
import math

tsmc = Grabber("006208", "2020-01-01", "2022-12-31")
tsmc_df = tsmc.df
stock_name = tsmc.stock

tsmc_data = tsmc_df[["成交股數", "開盤價", "最高價", "最低價", "收盤價"]].copy()
tsmc_data.index.rename("Date")
tsmc_data.columns = ["Vol", "Open", "High", "Low", "Close"]
for col in tsmc_data.columns:
    tsmc_data[col] = tsmc_data[col].apply(lambda x: x.replace(",", "").replace("--", "0") if isinstance(x, str) else None)
    tsmc_data[col] = pd.to_numeric(tsmc_data[col])

tsmc_data = tsmc_data.loc[tsmc_data["Close"] != 0]
tsmc_data.dropna()

# compute the MA lines

tsmc_data["MA_7"] = tsmc_data["Close"].rolling(7).mean()
tsmc_data["MA_15"] = tsmc_data["Close"].rolling(15).mean()
tsmc_data["MA_30"] = tsmc_data["Close"].rolling(30).mean()

# compute EMA

tsmc_data["EMA_12"] = tsmc_data["Close"].ewm(span=12).mean()
tsmc_data["EMA_26"] = tsmc_data["Close"].ewm(span=26).mean()

# MACD
# DIF = EMA12 - EMA26
# DEM = EMD9(DIF)
# OSC = DIF - DEM

tsmc_data["DIF"] = tsmc_data["EMA_12"] - tsmc_data["EMA_26"]
tsmc_data["DEM"] = tsmc_data["DIF"].ewm(span=9).mean()
tsmc_data["OSC"] = tsmc_data["DIF"] - tsmc_data["DEM"]
# print(tsmc_data[tsmc_data.columns[-3:]])

# draw

# fig, ax = plt.subplots(3, 1, figsize=(10,10))
# plt.subplots_adjust(hspace=0.8)
# tsmc_data["MA_7"].plot(ax=ax[0])
# tsmc_data["MA_30"].plot(ax=ax[0])
# tsmc_data["Close"].plot(ax=ax[0])
# ax[0].title.set_text("MA")
# ax[0].set_xlabel('')
# ax[0].legend()
# tsmc_data["EMA_12"].plot(ax=ax[1])
# tsmc_data["EMA_26"].plot(ax=ax[1])
# tsmc_data["Close"].plot(ax=ax[1])
# ax[1].title.set_text("EMA")
# ax[1].set_xlabel('')
# ax[1].legend()
# tsmc_data["DIF"].plot(ax=ax[2])
# tsmc_data["DEM"].plot(ax=ax[2])
# ax[2].fill_between(tsmc_data.index, tsmc_data["OSC"])
# ax[2].title.set_text("MACD")
# ax[2].set_xlabel('')
# ax[2].legend()
# plt.show()

# MACD testing

new_df = tsmc_data[["Close", "OSC"]].copy()
capital = 1000000
units = None
for (index, (close, osc)) in new_df.iterrows():
    if not units:
        if osc > 0:
            units = capital // close
            capital = capital - (capital // close)*close
            print("Buy {} units at {} on {}".format(units, close, index))
            print("Current Balance : {}".format(capital))
        else:
            units = 0
            capital = capital
    else:
        if units != 0:
            if osc < 0:
                print("Sell {} units at {} on {}".format(units, close, index))
                capital = capital + units * close
                units = 0
                print("Current Balance : {}".format(capital))

        else:
            if osc > 0:
                units = capital // close
                capital = capital - (capital // close) * close
                print("Buy {} units at {} on {}".format(units, close, index))
                print("Current Balance : {}".format(capital))
    close = close
    date = index
if units != 0:
    print("Sell {} units at {} on {}".format(units, close, date))
    capital = capital + units * close
    units = 0
    print("Current Balance : {}".format(capital))

# just buy and sell

comp_capital = 1000000
start_price = new_df["Close"].iloc[0]
units = comp_capital//start_price
remain_comp_cap = comp_capital - start_price * units
final_price = new_df["Close"].iloc[-1]
comp_final_cap = remain_comp_cap + units * final_price
return_ = comp_final_cap/comp_capital

# MA crossing

ma_units = []
ma_remain = []
ma_capital = 1000000
close = 0
new_df = tsmc_data[["Close", "MA_7", "MA_30"]].copy()
for (index, (close, sma, lma)) in new_df.iterrows():
    if not ma_units:
        if sma > lma:
            ma_units.append(ma_capital // close)
            ma_remain.append(ma_capital - (ma_capital // close)*(close))
        else:
            ma_units.append(0)
            ma_remain.append(ma_capital)
    else:
        if ma_units[-1] != 0:
            if lma < sma:
                ma_remain.append(ma_units[-1]*close+ma_remain[-1])
                ma_units.append(0)
            else:
                ma_remain.append(ma_remain[-1])
                ma_units.append(ma_units[-1])
        else:
            if sma > lma:
                ma_units.append(ma_capital // close)
                ma_remain.append(ma_capital - (ma_capital // close)*(close))
            else:
                ma_remain.append(ma_remain[-1])
                ma_units.append(ma_units[-1])
    close = close
if ma_units[-1] != 0:
    final_sell = ma_units[-1] * close
    ma_units[-1] = 0
    ma_remain[-1] = ma_remain[-1] + final_sell
MA_final = ma_remain[-1]

# results

print("=============================================================================")
print("Final Results:")
print("Target Stock: {}".format(stock_name))
tb = PrettyTable(["Method", "Final Capital", "RoR", "ROI (yearly)"])
tb.add_row(["MACD", capital, capital/comp_capital, math.log(capital/comp_capital, 5)])
tb.add_row(["BNH", comp_final_cap, return_, math.log(return_, 5)])
tb.add_row(["MA", MA_final, MA_final/comp_capital, math.log(MA_final/comp_capital, 5)])
print(tb)






