import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
import copy
import time, datetime
from matplotlib.pyplot import MultipleLocator
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class merge_solution:
    def __init__(self):
        pass
    @staticmethod
    def merge(morn_file,even_file,remain_file,ts,save_file):
        df_morn = pd.read_csv(morn_file,encoding='gbk')
        df_even = pd.read_csv(even_file, encoding='gbk')
        df_remain = pd.read_csv(remain_file,encoding='gbk')
        df_remain['M'] = df_remain[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df_remain['tss'] = df_remain['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df_remain['tso'] = df_remain['des_sec'].apply(utils.get_timeslots, args=(ts,))
        df_remain['delay']=0
        df_all = df_morn.append(df_even,ignore_index=True)
        df_all = df_all[['vhc_no','cap_date_ori','ori_sec','origin','cap_date_des','des_sec','destination','tratime','M','tss','tso','delay']]
        df_all = df_all.append(df_remain,ignore_index=True)
        df_all.to_csv(save_file,index=False,encoding='gbk')
    @staticmethod
    def plot_all_day_load(all_day_solu,save_file,ts):
        df = pd.read_csv(all_day_solu,encoding='gbk')
        tra_before = len(df[df['delay'] == -1])
        tra_after = len(df[df['delay'] == 1])
        tra_same = len(df[df['delay'] == 0])
        print("全天提早出行人数{0}，占比为{1}，延迟出行人数{2}，占比为{3},保持不变的人数{4}，占比为{5}".format(tra_before, tra_before / len(df),
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
        plt.legend()
        plt.show()
        df_load.to_csv(save_file, index=False, encoding='gbk')

if __name__ == "__main__":
    merge_solution.merge(morn_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\merge_solution_optim_trips_morning_419.csv",
                         even_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\merge_solution_optim_trips_morning_419.csv",
                         remain_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\remaining_trips_419.csv",
                         ts=15,save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\OD_419_solution.csv")
    merge_solution.plot_all_day_load(all_day_solu="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\OD_419_solution.csv",
                                     save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\全天优化前后网络载荷情况.csv",
                                     ts=15)