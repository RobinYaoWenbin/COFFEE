import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import transbigdata as tbd
import geopandas as gpd
import networkx as nx
from tqdm import tqdm
import json
import gc
from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge
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
import fiona
from mpl_toolkits.mplot3d import Axes3D
from math import radians, cos, sin, asin, sqrt
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def speed_load_plot(input_file_list,legend_list):
    plt.rcParams['figure.dpi'] = 300
    plt.xlabel('Time')
    plt.ylabel('Demand-to-supply ratio')
    plt.xticks(ticks=np.arange(0, 97, 16), labels=[str(_) + ':00' for _ in range(0, 25, 4)])
    for i in range(len(input_file_list)):
        tmp_file = input_file_list[i]
        df = pd.read_csv(tmp_file,encoding='gbk')
        plt.plot(df['ts'], df['L'], '.-')
    plt.legend(legend_list)
    plt.show()
    plt.xlabel('Time')
    plt.ylabel('Average speed')
    plt.xticks(ticks=np.arange(0, 97, 16), labels=[str(_) + ':00' for _ in range(0, 25, 4)])
    for i in range(len(input_file_list)):
        tmp_file = input_file_list[i]
        df = pd.read_csv(tmp_file, encoding='gbk')
        plt.plot(df['ts'], df['speed'], '.-')
    plt.legend(legend_list)
    plt.show()

def plot_relation(input_file_list,legend_list):
    plt.rcParams['figure.dpi'] = 300
    plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
    ax = plt.subplot(1, 1, 1)
    for i in range(len(input_file_list)):
        tmp_file = input_file_list[i]
        df = pd.read_csv(tmp_file)
        sns.regplot(x='L', y='speed', data=df, ax=ax,
                scatter_kws={'marker': '.', 's': 3, 'alpha': 0.3},
                # line_kws={'color': 'g'}
                    )
    plt.xlabel('Demand-to-supply ratio')
    plt.ylabel('Average speed')
    plt.legend(legend_list)
    plt.show()

if __name__ == "__main__":
    input_file_list=['../../data/congestion_multi_city/Hangzhou/dsr_speed_relation_data.csv',
                     '../../data/congestion_multi_city/Kunming/demand_supply_ratio_data.csv',
                     '../../data/congestion_multi_city/Xiaoshan/demand_supply_ratio_data.csv',
                     '../../data/congestion_multi_city/Yiwu/demand_supply_ratio_data.csv'
                     ]
    legend_list = ['Hangzhou','Kunming','Xiaoshan','Yiwu']
    # speed_load_plot(input_file_list,legend_list)
    plot_relation(input_file_list, legend_list)