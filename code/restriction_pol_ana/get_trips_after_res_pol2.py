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
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def get_final_num(x):
    if x[0:3] == '浙AT':
        return '-1'
    elif x[0:2] != '浙A':
        return '-2'
    tmp = re.findall('(\\d)[^0-9]*$', x)
    if len(tmp)!=1:
        return str( random.randint(0,10) )
    else:
        return tmp[0]

def get_period(ser):
    if  not (ser['cap_date_des'][11:]<'07:00:00' or ser['cap_date_ori'][11:]>'09:00:00') :
        return 1 # 包括早高峰限行时段
    elif not (ser['cap_date_des'][11:]<'16:30:00' or ser['cap_date_ori'][11:]>'18:30:00'):
        return 2 # 包括晚高峰限行时段
    else:
        return 0 # 其他时段

def get_delay(ser,res_plate1,res_plate2):
    if ser['period'] == 0:
        return 0
    elif ser['final_num'] != res_plate1 and ser['final_num'] != res_plate2 and ser['final_num'] != '-2':
        return 0
    else:
        return 999

def morn_advance_determine(ser):
    if ser['tso'] - 27 >= 0:
        return 27 - ser['tso']
    else:
        return 0
def morn_delay_determine(ser):
    if ser['tss'] - 36 < 0:
        return 36 - ser['tss']
    else:
        return 0
def even_advance_determine(ser):
    if ser['tso'] - 65 >= 0:
        return 65 - ser['tso']
    else:
        return 0
def even_delay_determine(ser):
    if ser['tss'] - 74 < 0:
        return 74 - ser['tss']
    else:
        return 0

class get_trips_after_pol2:
    def __init__(self):
        pass
    @staticmethod
    def res_pol_effect(OD_file,ts,res_plate1,res_plate2,morn_advance_ratio,morn_delay_ratio,
                       morn_unchange_ratio,even_advance_ratio,even_delay_ratio,even_unchange_ratio,
                       data_save_file):
        df = pd.read_csv(OD_file, encoding='gbk')
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df = df[
            ['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df['M'] = df[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df['tss'] = df['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df['tso'] = df['des_sec'].apply(utils.get_timeslots, args=(ts,))
        df['final_num'] = df[['vhc_no']].applymap(get_final_num)
        df['period'] = df.apply(get_period , axis=1)
        df['delay'] = df.apply(get_delay,args=(res_plate1,res_plate2,) , axis=1)
        df_no_res = df[df['delay'] == 0]
        df_res = df[df['delay'] == 999]
        morn_res_df = df_res[df_res['period'] == 1]
        even_res_df = df_res[df_res['period'] == 2]
        morn_number = len(morn_res_df)
        even_number = len(even_res_df)
        # 对早高峰进行限行政策模拟
        # 早高峰提前
        morn_res_df.sort_values(by=['cap_date_des'],ascending=True,inplace=True)
        morn_res_df.reset_index(drop=True,inplace=True)
        morn_advance_df = morn_res_df.iloc[:int(morn_number*morn_advance_ratio), :]
        morn_remain_df = morn_res_df.iloc[int(morn_number*morn_advance_ratio):, :]
        morn_advance_df['delay'] = morn_advance_df.apply(morn_advance_determine , axis=1)
        # 早高峰延后
        morn_remain_df.sort_values(by=['cap_date_ori'],ascending=False,inplace=True)
        morn_remain_df.reset_index(drop=True, inplace=True)
        morn_delay_df = morn_remain_df.iloc[:int(morn_number*morn_delay_ratio),:]
        morn_remain_df = morn_remain_df.iloc[int(morn_number*morn_delay_ratio):,:]
        morn_delay_df['delay'] = morn_delay_df.apply(morn_delay_determine , axis=1)
        # 早高峰不改变
        morn_remain_df = morn_remain_df.sample(frac=1.0)
        morn_remain_df.reset_index(drop=True,inplace=True)
        morn_unchange_df = morn_remain_df.iloc[:int(morn_number*morn_unchange_ratio),:]
        morn_unchange_df['delay'] = 0
        # 对晚高峰进行限行政策模拟
        # 晚高峰提前
        even_res_df.sort_values(by=['cap_date_des'], ascending=True, inplace=True)
        even_res_df.reset_index(drop=True, inplace=True)
        even_advance_df = even_res_df.iloc[:int(even_number * even_advance_ratio), :]
        even_remain_df = even_res_df.iloc[int(even_number * even_advance_ratio):, :]
        even_advance_df['delay'] = even_advance_df.apply(even_advance_determine, axis=1)
        # 晚高峰延后
        even_remain_df.sort_values(by=['cap_date_ori'], ascending=False, inplace=True)
        # even_remain_df = even_remain_df.sample(frac=1.0)
        even_remain_df.reset_index(drop=True, inplace=True)
        even_delay_df = even_remain_df.iloc[:int(even_number * even_delay_ratio), :] 
        even_remain_df = even_remain_df.iloc[int(even_number * even_delay_ratio):, :]
        even_delay_df['delay'] = even_delay_df.apply(even_delay_determine, axis=1)
        # 晚高峰不改变
        even_remain_df = even_remain_df.sample(frac=1.0)
        even_remain_df.reset_index(drop=True, inplace=True)
        even_unchange_df = even_remain_df.iloc[:int(even_number * even_unchange_ratio), :]
        even_unchange_df['delay'] = 0
        # 合并
        df = df_no_res.append(morn_advance_df,ignore_index=True)
        df = df.append(morn_delay_df, ignore_index=True)
        df = df.append(morn_unchange_df, ignore_index=True)
        df = df.append(even_advance_df, ignore_index=True)
        df = df.append(even_delay_df, ignore_index=True)
        df = df.append(even_unchange_df, ignore_index=True)
        df.to_csv(data_save_file,index=False,encoding='gbk')

if __name__ == "__main__":
    get_trips_after_pol2.res_pol_effect(OD_file="../../data/ODFile/OD_425.csv",
                                        ts=15,res_plate1='0',res_plate2='5',
                                        morn_advance_ratio=0.137, morn_delay_ratio=0.178,
                                        morn_unchange_ratio=0.227, even_advance_ratio=0.127,
                                        even_delay_ratio=0.145, even_unchange_ratio=0.321,
                                        data_save_file="../../data/restriction_pol/simulation_data_2/trips_after_res_pol2.csv")








