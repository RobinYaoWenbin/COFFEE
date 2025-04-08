import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
import matplotlib.pyplot as plt
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

class analysis:
    def __init__(self):
        pass
    @staticmethod
    def plot_netload(file,save_file,ts,opti_after):
        df = pd.read_csv(file , encoding='gbk')
        if opti_after:
            df['tss'] = df['tss']+df['delay']
            df['tso'] = df['tso'] + df['delay']
        netload_list = utils.get_ts_netload(df=df, ts=ts)
        tmp = {'x': list(range(int(24 * 60 / ts))),
               'netload':netload_list}
        df_load = pd.DataFrame(tmp)
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Network load')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df_load['x'], df_load['netload'], '.-', color='black',linewidth=2,markersize=4.8)
        plt.show()
        df_load.to_csv(save_file,index=False,encoding='gbk')
    @staticmethod
    def plot_load_together(file,save_file,ts):
        df = pd.read_csv(file, encoding='gbk')
        tra_before = len(df[df['delay'] == -1]) ; tra_after = len(df[df['delay'] == 1]) ; tra_same =  len(df[df['delay'] == 0])
        print("提早出行人数{0}，占比为{1}，延迟出行人数{2}，占比为{3},保持不变的人数{4}，占比为{5}".format(tra_before , tra_before / len(df) ,
                                                                           tra_after,tra_after / len(df) , tra_same , tra_same / len(df) ))
        netload_list_before = utils.get_ts_netload(df=df, ts=ts)
        df['tss'] = df['tss'] + df['delay']
        df['tso'] = df['tso'] + df['delay']
        netload_list_after = utils.get_ts_netload(df=df, ts=ts)
        tmp = {'x': list(range(int(24 * 60 / ts))),
               'load_before':netload_list_before,
               'load_after':netload_list_after}
        df_load = pd.DataFrame(tmp)
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Network load')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df_load['x'], df_load['load_before'], '.-', color='black', linewidth=2, markersize=4.8,label='original network load')
        plt.plot(df_load['x'], df_load['load_after'], '.-', color='blue', linewidth=2, markersize=4.8,label='network load after optimization')
        plt.legend(fontsize='small',loc='best',frameon=False)
        plt.show()
        df_load.to_csv(save_file, index=False, encoding='gbk')
    @staticmethod
    def plot_load_together_cons_tra(file, save_file, ts):
        df = pd.read_csv(file, encoding='gbk')
        tra_before = len(df[df['delay'] < 0]);
        tra_after = len(df[df['delay'] > 0]);
        tra_same = len(df[df['delay'] == 0])
        print("提早出行人数{0}，占比为{1}，延迟出行人数{2}，占比为{3},保持不变的人数{4}，占比为{5}".format(tra_before, tra_before / len(df),
                                                                           tra_after, tra_after / len(df), tra_same,
                                                                           tra_same / len(df)))
        netload_list_before = utils.get_ts_netload(df=df, ts=ts)
        df['tss'] = df['tss'] + df['delay']
        df['tso'] = df['tso'] + df['delay']
        netload_list_after = utils.get_ts_netload(df=df, ts=ts)
        tmp = {'x': list(range(int(24 * 60 / ts))),
               'load_before': netload_list_before,
               'load_after': netload_list_after}
        df_load = pd.DataFrame(tmp)
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Network load')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df_load['x'], df_load['load_before'], '.-', color='black', linewidth=2, markersize=4.8,
                 label='original network load')
        plt.plot(df_load['x'], df_load['load_after'], '.-', color='blue', linewidth=2, markersize=4.8,
                 label='network load after optimization')
        plt.legend(fontsize='small', loc='best', frameon=False)
        plt.show()
        df_load.to_csv(save_file, index=False, encoding='gbk')


if __name__ == "__main__":
    # analysis.plot_netload(file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\merge_solution_optim_trips_morning_419.csv",
    #                       save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\networkloadplot\\merge_solution_netload_plot.csv",
    #                       ts=15,opti_after=True)
    analysis.plot_load_together(file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\merge_solution_optim_trips_morning_419.csv",
                                save_file="E:\\study_e\\analysis_of_IBTDM\\data\optim_data\\networkloadplot\\netload_plot_together.csv", ts=15)