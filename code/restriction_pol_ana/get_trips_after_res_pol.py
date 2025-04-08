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

def get_tag_morn_advance(ser):
    if ser['des_sec'] <= 28800 and ser['ori_sec'] >= 25200:
        return 1
    else:
        return 0

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

def get_morn_advance_delay(ser):
    if ser['tag_morn_advance2'] == 1 and ser['tag_morn_advance'] == 1:
        if ser['tso'] - 27 >= 0:
            return  27 - ser['tso']
        else:
            return 0
    else:
        return 0

def get_tag_even_cancel(ser):
    if ser['des_sec'] <= 59400 and ser['ori_sec'] >= 55800:
        return 1
    else:
        return 0

def get_even_cancel_delay(ser):
    if ser['tag_even_cancel2'] == 1 and ser['tag_even_cancel'] == 1:
        return 9999
    else:
        return ser['delay']

def get_all_other_delay(ser,res_plate1,res_plate2):
    if ser['delay'] != 0:
        return ser['delay']
    else:
        if (ser['tss'] > 35 or ser['tso'] < 28) and (ser['tss'] > 73 or ser['tso'] < 66):
            return ser['delay']
        else:
            if ser['final_num']!=res_plate1 and ser['final_num']!=res_plate2 :
                return ser['delay']
            else:
                if ser['tss']>35:# 晚高峰
                    return 9998
                else: # 早高峰
                    return 9997

def change_tag(ser):
    if (ser['tag_morn'] == 1 or ser['tag_even'] == 1) and (ser['delay']==9998 or ser['delay']==9997):
        return 0
    else:
        return ser['delay']

class get_trips_after_pol:
    def __init__(self):
        pass
    @staticmethod
    def change_travel(OD_file,morn_illegal,even_illegal,morn_advance,even_cancel,ts,res_plate1,res_plate2,data_save_file):
        df = pd.read_csv(OD_file,encoding='gbk')
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df = df[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df['M'] = df[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df['tss'] = df['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df['tso'] = df['des_sec'].apply(utils.get_timeslots, args=(ts,))
        df['tag_morn_advance'] = df.apply(get_tag_morn_advance , axis=1)
        df['final_num'] = df[['vhc_no']].applymap(get_final_num)
        df = df.sample(frac=1.0)
        veh_advance = list(set(df[(df['tag_morn_advance'] == 1) & ( (df['final_num'] == res_plate1) | (df['final_num'] == res_plate2) ) ]['vhc_no']))[0:morn_advance]
        print("共有这么多辆车会提前出行：" , len(veh_advance))
        veh_advance = pd.DataFrame({'vhc_no':veh_advance})
        veh_advance['tag_morn_advance2'] = 1
        df = pd.merge(df,veh_advance,how='left',on='vhc_no')
        df.fillna(0,inplace=True)
        df['delay'] = df.apply(get_morn_advance_delay , axis=1)
        df.drop(columns=['tag_morn_advance','tag_morn_advance2'],inplace=True)
        df['tag_even_cancel'] = df.apply(get_tag_even_cancel, axis=1)
        veh_cancel = list(set(df[(df['tag_even_cancel'] == 1) & ( (df['final_num'] == res_plate1) | (df['final_num'] == res_plate2) ) ]['vhc_no']))[0:even_cancel]
        print("晚高峰限行前一小时取消出行的车辆数为",len(veh_cancel))
        veh_cancel = pd.DataFrame({'vhc_no': veh_cancel})
        veh_cancel['tag_even_cancel2'] = 1
        df = pd.merge(df, veh_cancel, how='left', on='vhc_no')
        df.fillna(0, inplace=True)
        df['delay'] = df.apply(get_even_cancel_delay, axis=1)
        df.drop(columns=['tag_even_cancel','tag_even_cancel2'],inplace=True)
        df['delay'] = df.apply(get_all_other_delay , args=(res_plate1,res_plate2,) ,axis=1)
        veh_even_illegal = list(set(df[df['delay'] == 9998]['vhc_no']))[0:even_illegal]
        veh_even_illegal = pd.DataFrame({'vhc_no': veh_even_illegal})
        veh_even_illegal['tag_even'] = 1
        df = pd.merge(df , veh_even_illegal , how='left',on='vhc_no')
        df.fillna(0, inplace=True)
        veh_morn_illegal = list(set(df[df['delay'] == 9997]['vhc_no']))[0:morn_illegal]
        veh_morn_illegal = pd.DataFrame({'vhc_no': veh_morn_illegal})
        veh_morn_illegal['tag_morn'] = 1
        df = pd.merge(df, veh_morn_illegal, how='left', on='vhc_no')
        df.fillna(0, inplace=True)
        df['delay'] = df.apply(change_tag , axis=1)
        df = df[df['delay']<9000]
        df.drop(columns=['tag_morn','tag_even','final_num'],inplace=True)
        df.to_csv(data_save_file,index=False,encoding='gbk')

if __name__ == "__main__":
    get_trips_after_pol.change_travel(OD_file="../../data/ODFile/OD_425.csv",
                                      morn_illegal=3290,even_illegal=3712,morn_advance=1008,even_cancel=1281,ts=15,
                                      res_plate1='5', res_plate2='0',
                                      data_save_file="../../data/restriction_pol/trips_after_res_pol.csv")