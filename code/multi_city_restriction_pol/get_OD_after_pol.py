import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import sys
from matplotlib.pyplot import MultipleLocator
import random
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import copy
import time, datetime
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class get_OD:
    def __init__(self):
        pass
    @staticmethod
    def change_travel(OD_file,ts,data_save_file):
        df = pd.read_csv(OD_file,encoding='gbk')
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df = df[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df['M'] = df[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df['tss'] = df['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df['tso'] = df['des_sec'].apply(utils.get_timeslots, args=(ts,))
        print("原始OD文件共有{0}行".format(len(df)))
        tmp_df_morning = df[(df['ori_sec']>=25200) & (df['ori_sec']<=32400)]
        tmp_df_evening = df[(df['ori_sec'] >= 59400) & (df['ori_sec'] <= 66600)]
        tmp_df_other = df[(df['ori_sec'] < 25200) | ((df['ori_sec'] > 32400) & (df['ori_sec'] < 59400)) | (df['ori_sec'] > 66600)]
        print("文件分割后共{0}行。".format(len(tmp_df_morning) + len(tmp_df_evening) + len(tmp_df_other)))
        tmp_df_morning = tmp_df_morning.sample(frac=0.8)
        tmp_df_evening = tmp_df_evening.sample(frac=0.8)
        df_new = tmp_df_morning.append(tmp_df_evening,ignore_index=False)
        df_new = df_new.append(tmp_df_other, ignore_index=False)
        df_new['delay'] = 0
        df_new = df_new[['vhc_no', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime','M','tss','tso','delay']]
        df_new.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def plot_together(file_after_policy,file_before_policy):
        df_before = pd.read_csv(file_before_policy,encoding='gbk')
        df_before.rename(columns={'netload':'ori_netload','speed':'ori_speed'},inplace=True)
        df_after = pd.read_csv(file_after_policy,encoding='gbk')
        df_after.rename(columns={'netload': 'after_netload', 'speed': 'after_speed'}, inplace=True)
        df = pd.merge(df_before,df_after,how='inner',on='ts')
        fontsize = 15
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        fig, axes = plt.subplots()
        fig.set_size_inches(10, 8)
        lns1 = axes.plot(df['ts'], df['ori_speed'], '.-', color='black', label='original average speed',
                         linewidth=2,
                         markersize=4.8)
        lns = lns1
        lns2 = axes.plot(df['ts'], df['after_speed'], '.-', label='average speed after policy',
                         linewidth=2, markersize=4.8)
        lns += lns2
        twin_axes = axes.twinx()
        lns2 = twin_axes.plot(df['ts'], df['ori_netload'], '.-', color='green', label='original network load',
                              linewidth=2,
                              markersize=4.8)
        lns += lns2
        lns2 = twin_axes.plot(df['ts'], df['after_netload'], '.-', color='red', label='network load after policy',
                              linewidth=2,
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
        print("original network load is {0}，network load after policy is {1}，reduced {2}".format( max(df['ori_netload']),max(df['after_netload']),
                                                       (max(df['ori_netload']) - max(df['after_netload']))/max(df['ori_netload'])  ))


if __name__ == "__main__":
    # get_OD.change_travel(OD_file="../../data/IBTDM_multi_city/Xiaoshan/ODFile/OD_0321.csv",ts=15,
    #                      data_save_file="../../data/multi_city_restriction_pol/Xiaoshan/trips_after_res_pol.csv")

    get_OD.plot_together(file_after_policy="../../data/multi_city_restriction_pol/Xiaoshan/萧山区限行政策作用后的交通状态仿真.csv",
                         file_before_policy="../../data/IBTDM_multi_city/Xiaoshan/simu_pol_eva_data/萧山区交通状态仿真.csv")



