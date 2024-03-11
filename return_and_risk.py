import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from data_grabber import Grabber
import math
import scipy.stats as stats

tsmc_data = Grabber("2330", "2020-01-01", "2023-3-31")
print("We are currently dealing with data from {}".format(tsmc_data.stock))
tsmc_df = tsmc_data.df
tsmc_df["收盤價"] = tsmc_df["收盤價"].astype(float)
# Grabber already helped us convert the index to actual datetime object
tsmc_df = tsmc_df["收盤價"]
# we can use tsmc_df = tsmc_df.apply(lambda x:x.replace(",", "") if there's notation errors
tsmc_df.index.names = ["date"]
tsmc_df.name = "close"
# fig, ax = plt.subplots()
# ax.plot(tsmc_df.index, tsmc_df)
# ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))
# plt.show()

change_df = tsmc_df.pct_change()
change_df.dropna(inplace=True)
change_df.apply(lambda x:math.log(x) if x>0 else None)
# ch_l = change_df.iloc[:-1]
# ch_f = change_df.iloc[1:]
# plt.scatter(ch_f.values, ch_l.values)
# plt.show()

# after checking, we can see that the changes every day is more like independent than dependent

# assuming that ln(Pt - Pt-1) ~ N(mu, sigma^2) -> we can use MLE to find the parameters

def MLE_mu(data):
    n = data.shape[0]
    return data.sum()/n

def MLE_sigmasq(data):
    n = data.shape[0]
    mu_hat = MLE_mu(data)
    temp_data = data.apply(lambda x: (x-mu_hat)**2)
    return temp_data.sum()/n


h = change_df.sort_values(ascending=True)
x_axis = np.arange(h.iloc[0], h.iloc[-1], 0.0001)
pdf_values = stats.norm.pdf(x_axis, MLE_mu(change_df), math.sqrt(MLE_sigmasq(change_df)))

plt.plot(x_axis, pdf_values)
plt.hist(h, density=True)  # Normalize the histogram
plt.show()
