import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
import copy
import time, datetime
import geopandas as gpd
import transbigdata as tbd
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class vis:
    def __init__(self):
        pass
    @staticmethod
    def speed_vis(speed_file):
        df = pd.read_csv(speed_file,encoding='gbk')
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Average speed (km/h)')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df['ts'], df['speed'], '.-', color='black', linewidth=2, markersize=4.8)
        plt.legend(fontsize='small', loc='best', frameon=False)
        plt.show()
    @staticmethod
    def speed_load_vis(speed_file,load_file,data_save_file):
        df_speed = pd.read_csv(speed_file,encoding='gbk')
        df_load = pd.read_csv(load_file,encoding='gbk')
        df_all = pd.merge(df_speed,df_load,how='inner',left_on='ts',right_on='timeslot')
        df_all = df_all[['ts','speed','netload']]
        fontsize = 20
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        fig, axes = plt.subplots()
        fig.set_size_inches(10, 8)
        lns1 = axes.plot(df_all['ts'], df_all['speed'], '.-', color='black', label='average speed', linewidth=3.8, markersize=8.8)
        lns = lns1
        twin_axes = axes.twinx()
        lns2 = twin_axes.plot(df_all['ts'], df_all['netload'], '.-',label='network load', linewidth=3.8, markersize=8.8)
        lns += lns2
        axes.set_xlabel("Time slots", fontsize=fontsize)
        axes.set_ylabel("Average speed (km/h)", fontsize=fontsize)
        twin_axes.set_ylabel("Network load", fontsize=fontsize)
        plt.setp(axes.get_xticklabels(), fontsize=fontsize)
        plt.setp(axes.get_yticklabels(), fontsize=fontsize)
        plt.setp(twin_axes.get_yticklabels(), fontsize=fontsize)
        labs = [l.get_label() for l in lns]
        num1 = 1.05;
        num2 = 1;
        num3 = 3;
        num4 = 0
        axes.legend(lns, labs, fontsize=fontsize, frameon=False, loc=0)
        plt.show()
        df_all.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def speed_load_scatter(speed_load_file):
        df = pd.read_csv(speed_load_file,encoding='gbk')
        x = np.array(df['netload'], dtype='float64')
        y = np.array(df['speed'], dtype="float64")
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        plt.scatter(x, y, s=2)
        plt.xlabel("Network load")
        plt.ylabel("Average speed (km/h)")
        # plt.legend()
        plt.show()

if __name__ == "__main__":
    # vis.speed_vis(speed_file="E:\\study_e\\analysis_of_IBTDM\\data\\speedfile\\speed_0419.csv")
    # vis.speed_load_vis(speed_file="E:\\study_e\\analysis_of_IBTDM\\data\\speedfile\\speed_0419.csv",
    #                    load_file="E:\\study_e\\analysis_of_IBTDM\\data\\网络载荷随时间变化数据_0419.csv",
    #                    data_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv")
    vis.speed_load_scatter(speed_load_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv")