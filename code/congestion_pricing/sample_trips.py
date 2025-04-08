import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
from matplotlib.pyplot import MultipleLocator
import copy
import time, datetime
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class sample:
    def __init__(self):
        pass
    @staticmethod
    def start(OD_file,ratio,data_save_file):
        df = pd.read_csv(OD_file , encoding='gbk')
        df = df.sample(frac = ratio)
        df.to_csv(data_save_file , index=False ,encoding='gbk')

if __name__ == "__main__":
    sample.start(OD_file = "../../data/ODFile/OD_425.csv",ratio = 0.846,
                 data_save_file="../../data/congestion_pricing/OD_sample_425.csv")
