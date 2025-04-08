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

class cal_ratio:
    def __init__(self):
        pass
    @staticmethod
    def L_cal(demand_file,supply_value,data_save_file):
        df = pd.read_csv(demand_file,encoding='gbk')
        df['L'] = df['netload'] / (supply_value * 1000 / 7)
        df.to_csv(data_save_file , index=False , encoding='gbk')
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Demand-to-supply ratio')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df['timeslot'], df['L'], '.-', color='black')
        plt.show()
    @staticmethod
    def L_cal_kunming(demand_file,supply_value,data_save_file):
        df = pd.read_csv(demand_file, encoding='gbk')
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
    @staticmethod
    def L_speed_relation(demand_supply_ratio_file,speed_file,data_save_file):
        df1 = pd.read_csv(demand_supply_ratio_file,encoding='gbk')
        df2 = pd.read_csv(speed_file,encoding='gbk')
        df2.rename(columns={'ts':'timeslot'},inplace=True)
        df = pd.merge(df1[['timeslot','L']],df2,how='inner',on='timeslot')
        df.to_csv(data_save_file,index=False,encoding='gbk')
        plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
        ax = plt.subplot(1, 1, 1)
        sns.regplot(x='L', y='speed', data=df, ax=ax,
                    scatter_kws={'marker': '.', 's': 3, 'alpha': 0.3},
                    line_kws={'color': 'g'})
        plt.xlabel('Demand-to-supply ratio')
        plt.ylabel('Speed')
        plt.legend(['Hangzhou'])
        plt.show()
        # 计算r2
        results = smf.ols('speed ~ L', data=df).fit()
        print(results.summary())
    @staticmethod
    def L_speed_relation_input2(demand_supply_ratio_file,legend):
        df = pd.read_csv(demand_supply_ratio_file)
        plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
        ax = plt.subplot(1, 1, 1)
        sns.regplot(x='L', y='avg_speed', data=df, ax=ax,
                    scatter_kws={'marker': '.', 's': 3, 'alpha': 0.3},
                    line_kws={'color': 'g'})
        plt.xlabel('Demand-to-supply ratio')
        plt.ylabel('Speed')
        plt.legend([legend])
        plt.show()
        # 计算r2
        results = smf.ols('avg_speed ~ L', data=df).fit()
        print(results.summary())


if __name__ == "__main__":
    # cal_ratio.L_cal(demand_file="../../data/网络载荷随时间变化数据_0425.csv",
    #                 supply_value=1375.74,
    #                 data_save_file="../../data/congestion_multi_city/Hangzhou/demand_supply_ratio_data.csv")

    cal_ratio.L_speed_relation(demand_supply_ratio_file="../../data/congestion_multi_city/Hangzhou/demand_supply_ratio_data.csv",
                               speed_file="../../data/speedfile/speed_0425.csv",
                               data_save_file="../../data/congestion_multi_city/Hangzhou/dsr_speed_relation_data.csv")







