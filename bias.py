import pandas as pd
import matplotlib.pyplot as plt
from data_grabber import Grabber

starting_date = "2020-05-25"
end_date = "2023-07-01"
stock_number = "2303"

print(repr(Grabber(stock_number, starting_date, end_date)))
