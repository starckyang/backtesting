import pandas as pd
import requests
import datetime
from dateutil.relativedelta import relativedelta


class Grabber:

    def __init__(self, stock_number, starting_date, end_date):
        """
        :param stock_number:
        :param starting_date (in the format of YYYY-MM-DD):
        :param end_date (in the format of YYYY-MM-DD):
        """
        self.date_formatter(starting_date, end_date)
        self.stock = ""
        dfs = []
        for single_date in [self.starting + relativedelta(months=n) for n in range((self.end.year - self.starting.year)
                                                                                   * 12 + (self.end.month -
                                                                                           self.starting.month) + 1)]:
            if single_date == self.starting:
                formatted_date = single_date.strftime("%Y%m%d")
                response = requests.get("https://www.twse.com.tw/exchangeReport/STOCK_DAY?response="
                                        "json&date={}&stockNo={}".format(formatted_date, stock_number)).json()
                df = pd.DataFrame(data=response["data"], columns=response["fields"])
                dfs.append(df)
                print("First Complete")
                self.stock = response["title"].split(" ")[2]
            else:
                formatted_date = single_date.strftime("%Y%m%d")
                response = requests.get(
                    "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}"
                    .format(formatted_date,stock_number)).json()
                try:
                    df = pd.DataFrame(data=response["data"], columns=response["fields"])
                    dfs.append(df)
                finally:
                    print("{} Completed".format(single_date.month))

        df = pd.concat(dfs, ignore_index=True)
        df["日期"] = df['日期'].apply(lambda _: datetime.datetime(int(_.split("/")[0])+1911, int(_.split("/")[1]), int(_.split("/")[2])))
        df.set_index(df["日期"], inplace=True)
        df.drop("日期", axis=1, inplace=True)
        self.df = df

    def __repr__(self):
        return ("This is a generator aims to retrieve the stock price data for {} from {} to {}".format(self.stock,
                                                                                                      self.starting,
                                                                                                      self.end))

    def __str__(self):
        return("This is a generator aims to retrieve the stock price data for {} from {} to {}".format(self.stock,
                                                                                                      self.starting,
                                                                                                      self.end))

    def date_formatter(self, s_day, e_day):
        sy, sm, sd = [int(item) for item in s_day.split("-")]
        ey, em, ed = [int(item) for item in e_day.split("-")]
        self.starting = datetime.date(sy, sm, sd)
        self.end = datetime.date(ey, em, ed)