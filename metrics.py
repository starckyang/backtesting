import pandas
import matplotlib.pyplot as plt
import pandas as pd

from data_grabber import Grabber

tsmc = Grabber("2330", "2020-01-01", "2020-03-31")
tsmc_df = tsmc.df

tsmc_data = tsmc_df[["成交股數", "開盤價", "最高價", "最低價", "收盤價"]].copy()
tsmc_data.index.rename("Date")
tsmc_data.columns = ["Vol", "Open", "High", "Low", "Close"]
for col in tsmc_data.columns:
    tsmc_data[col] = tsmc_data[col].apply(lambda x: x.replace(",", "") if isinstance(x, str) else None)
    tsmc_data[col] = pd.to_numeric(tsmc_data[col])

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
print(tsmc_data[tsmc_data.columns[-3:]])

# draw

fig, ax = plt.subplots(3, 1, figsize=(10,10))
plt.subplots_adjust(hspace=0.8)
tsmc_data["MA_7"].plot(ax=ax[0])
tsmc_data["MA_30"].plot(ax=ax[0])
tsmc_data["Close"].plot(ax=ax[0])
ax[0].title.set_text("MA")
ax[0].set_xlabel('')
ax[0].legend()
tsmc_data["EMA_12"].plot(ax=ax[1])
tsmc_data["EMA_26"].plot(ax=ax[1])
tsmc_data["Close"].plot(ax=ax[1])
ax[1].title.set_text("EMA")
ax[1].set_xlabel('')
ax[1].legend()
tsmc_data["DIF"].plot(ax=ax[2])
tsmc_data["DEM"].plot(ax=ax[2])
ax[2].fill_between(tsmc_data.index, tsmc_data["OSC"])
ax[2].title.set_text("MACD")
ax[2].set_xlabel('')
ax[2].legend()
plt.show()



