import pandas as pd
import requests
import datetime
from dateutil.relativedelta import relativedelta


code = "2308"
s_date = datetime.date(2020, 1, 1)
f_date = datetime.date(2022, 3, 31)
duration = (f_date - s_date).days
FEE = 0.004425


dfs = []
for single_date in [s_date + relativedelta(months=n) for n in range((f_date.year - s_date.year) * 12 + (f_date.month - s_date.month) + 1)]:
    if single_date == s_date:
        formatted_date = single_date.strftime("%Y%m%d")
        response = requests.get("https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}".format(formatted_date, code)).json()
        df = pd.DataFrame(data=response["data"], columns=response["fields"])
        dfs.append(df)
        print("First Complete")
    else:
        formatted_date = single_date.strftime("%Y%m%d")
        response = requests.get(
            "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}".format(formatted_date,
                                                                                                       code)).json()
        try:
            df = pd.DataFrame(data=response["data"], columns=response["fields"])
            dfs.append(df)
        finally:
            print("{} Completed".format(single_date.month))
df = pd.concat(dfs, ignore_index=True)
df['日期'].apply(lambda _: datetime.datetime(int(_.split("/")[0]), int(_.split("/")[1]), int(_.split("/")[2])))
df.set_index(df["日期"], inplace=True)
df.drop("日期", axis=1, inplace=True)


new_df = pd.DataFrame()
new_df["close"] = pd.to_numeric(df["收盤價"])
new_df["5ma"] = new_df["close"].rolling(5).mean()
new_df["20ma"] = new_df["close"].rolling(20).mean()
new_df.dropna(inplace=True)

units = []
remain = []
capital = 1000000
close = 0
for (index, (close, sma, lma)) in new_df.iterrows():
    if not units:
        if sma > lma:
            units.append(capital // close)
            remain.append(capital - (capital // close)*(close+FEE))
        else:
            units.append(0)
            remain.append(capital)
    else:
        if units[-1] != 0:
            if lma < sma:
                remain.append(units[-1]*close+remain[-1])
                units.append(0)
            else:
                remain.append(remain[-1])
                units.append(units[-1])
        else:
            if sma > lma:
                units.append(capital // close)
                remain.append(capital - (capital // close)*(close+FEE))
            else:
                remain.append(remain[-1])
                units.append(units[-1])
    close = close
if units[-1] != 0:
    final_sell = units[-1] * close
    units[-1] = 0
    remain[-1] = remain[-1] + final_sell

new_df["units"] = units
new_df["capital"] = remain

print("low point: {}".format(new_df[new_df["capital"] > 20000].min()))
print("high point: {}".format(new_df[new_df["capital"] > 20000].max()))

# new_df.plot()
# pd.to_datetime(df['日期'], format="%m/%d/%Y")
# df = df.sort_values(by='日期', ascending=False)









