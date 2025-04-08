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

def get_speed_ratio(ser,origin_speed_df,after_speed_df):
    # 得到原始的平均速度
    tss = ser['tss']
    tso = ser['tso']
    origin_avg_speed = np.mean(origin_speed_df[(origin_speed_df['ts']>=tss)&(origin_speed_df['ts']<=tso)]['speed'])
    # 得到出发时间调整策略之后的平均速度
    tss = tss + ser['delay']
    tso = tso + ser['delay']
    after_avg_speed = np.mean(after_speed_df[(after_speed_df['ts'] >= tss) & (after_speed_df['ts'] <= tso)]['speed'])
    speed_ratio = after_avg_speed / origin_avg_speed
    return speed_ratio

class get_speed:
    def __init__(self):
        pass
    @staticmethod
    def get(trip_file_after_DTAS,original_speed_file,after_speed_file,data_save_file):
        df = pd.read_csv(trip_file_after_DTAS,encoding='gbk')
        origin_speed_df = pd.read_csv(original_speed_file,encoding='gbk')
        after_speed_df = pd.read_csv(after_speed_file,encoding='gbk')
        # 得到出发时间调整策略之后的平均速度/原始的平均速度
        df['speed_ratio'] = df.apply(get_speed_ratio,args=(origin_speed_df,after_speed_df,),axis=1)
        df['new_tratime'] = df['tratime'] / df['speed_ratio']
        df.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def new_arrival_time(new_tratime_file,data_save_file):
        df = pd.read_csv(new_tratime_file,encoding='gbk')
        df['delta_arrival_time'] = df['delay']*15+df['new_tratime']/60-df['tratime']/60
        df.to_csv(data_save_file,index=False,encoding='gbk')

if __name__ == "__main__":
    get_speed.get(trip_file_after_DTAS="../../data/multi_city_DTASCTB_data/Xiaoshan/merge_trip_solu_10.csv",
                  original_speed_file="../../data/IBTDM_multi_city/Xiaoshan/simu_pol_eva_data/萧山区交通状态仿真.csv",
                  after_speed_file='../../data/multi_city_DTASCTB_data/Xiaoshan/仿真结果_cons_100.csv',
                  data_save_file="../../data/multi_city_arrival_time_data/Xiaoshan_new_tratime.csv")

