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

def get_summary(L_speed_file):
    df = pd.read_csv(L_speed_file,encoding='gbk')
    results = smf.ols('speed ~ L', data=df).fit()
    print(results.summary())

if __name__ == "__main__":
    get_summary(L_speed_file="../../data/congestion_multi_city/Hangzhou/new_demand_supply_ratio_speed_data.csv")