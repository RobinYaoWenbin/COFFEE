import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib.pyplot import MultipleLocator
import statsmodels.formula.api as smf
import copy
import time, datetime
import osmnx as ox
from sklearn.cluster import KMeans
import logging
import time
import utils
import seaborn as sns
import math
import geopandas as gpd
from mpl_toolkits.mplot3d import Axes3D
from math import radians, cos, sin, asin, sqrt
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def get_L_speed(speed_load_file,supply_value,data_save_file):
    df = pd.read_csv(speed_load_file,encoding='gbk')
    df['L'] = df['netload'] / (supply_value * 1000 / 7)
    df.to_csv(data_save_file, index=False, encoding='gbk')
    plt.rcParams['figure.dpi'] = 300  # 分辨率
    ax = plt.gca()
    plt.xlabel('Time slots')
    plt.ylabel('Demand-to-supply ratio')
    x_major_locator = MultipleLocator(5)
    ax.xaxis.set_major_locator(x_major_locator)
    plt.plot(df['ts'], df['L'], '.-', color='black')
    plt.show()

if __name__ == "__main__":
    get_L_speed(speed_load_file="../../data/speed_load_data/speed_load_data_0425.csv",
                supply_value=1375.74,
                data_save_file="../../data/congestion_multi_city/Hangzhou/new_demand_supply_ratio_speed_data.csv")