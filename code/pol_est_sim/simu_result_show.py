import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import utils
import copy
import time, datetime
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class plot_show:
    def __init__(self):
        pass
    @staticmethod
    def simu_real_data_show(simu_result_file,real_data_file):
        df_simu = pd.read_csv(simu_result_file , encoding='gbk')
        df_real = pd.read_csv(real_data_file , encoding='gbk')
        fontsize = 15
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        fig, axes = plt.subplots()
        fig.set_size_inches(10, 8)
        lns1 = axes.plot(df_simu['ts'], df_simu['speed'], '.-', color='black', label='simulated average speed', linewidth=2,
                         markersize=4.8)
        lns = lns1
        lns2 = axes.plot(df_real['ts'], df_real['speed'], '.-', label='real average speed',
                         linewidth=2,markersize=4.8)
        lns += lns2
        twin_axes = axes.twinx()
        lns2 = twin_axes.plot(df_simu['ts'], df_simu['netload'], '.-',color='green', label='simulated network load', linewidth=2,
                              markersize=4.8)
        lns += lns2
        lns2 = twin_axes.plot(df_real['ts'], df_real['netload'], '.-', color='red',label='real network load', linewidth=2,
                              markersize=4.8)
        lns += lns2
        axes.set_xlabel("Time slots", fontsize=fontsize)
        axes.set_ylabel("Average speed (km/h)", fontsize=fontsize)
        twin_axes.set_ylabel("Network load", fontsize=fontsize)
        plt.setp(axes.get_xticklabels(), fontsize=fontsize)
        plt.setp(axes.get_yticklabels(), fontsize=fontsize)
        plt.setp(twin_axes.get_yticklabels(), fontsize=fontsize)
        labs = [l.get_label() for l in lns]
        axes.legend(lns, labs, fontsize=fontsize, frameon=False, loc=0)
        plt.show()

if __name__ == "__main__":
    plot_show.simu_real_data_show(simu_result_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv",
                                  real_data_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv")