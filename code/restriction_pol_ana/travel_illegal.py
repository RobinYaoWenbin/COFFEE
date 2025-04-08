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

def get_period(x):
    # 0:不限行；1：早高峰限行；2：晚高峰限行
    x=x[11:]
    if x>='07:10:00' and x<='08:50:00':
        return 1
    elif x>='16:40:00' and x<='18:20:00':
        return 2
    else:
        return 0

def get_tag(x):
    if len(x)==8:
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

class travel_illegal:
    def __init__(self):
        pass
    @staticmethod
    def get_illegal_ratio(LPR_file,dev_file,res_plate1,res_plate2):
        df = pd.read_csv(LPR_file,encoding='gbk')
        dev_df = pd.read_csv(dev_file,encoding='gbk')
        df = pd.merge(df,dev_df,how='inner',left_on='devc_id',right_on='id')
        df['period'] = df[['inner_rec_time']].applymap(get_period)
        df['tag'] = df[['vhc_no']].applymap(get_tag)
        tmp_morn_df = df[ (df['period'] == 1) & (df['tag'] == 0) ]
        tmp_morn_df['final_num'] = tmp_morn_df[['vhc_no']].applymap(get_final_num)
        tmp_morn_illegal_df = tmp_morn_df[(tmp_morn_df['final_num'] == res_plate1) | (tmp_morn_df['final_num'] == res_plate2)]
        tmp_morn_df.drop_duplicates(subset=['vhc_no'],keep='first',inplace=True)
        tmp_morn_illegal_df.drop_duplicates(subset=['vhc_no'],keep='first',inplace=True)
        tmp_even_df = df[(df['period'] == 2) & (df['tag'] == 0)]
        tmp_even_df['final_num'] = tmp_even_df[['vhc_no']].applymap(get_final_num)
        tmp_even_illegal_df = tmp_even_df[(tmp_even_df['final_num'] == res_plate1) | (tmp_even_df['final_num'] == res_plate2)]
        tmp_even_df.drop_duplicates(subset=['vhc_no'], keep='first', inplace=True)
        tmp_even_illegal_df.drop_duplicates(subset=['vhc_no'], keep='first', inplace=True)
        morn_veh_num = len( list( set( df[df['period']==1]['vhc_no'] ) ) )
        even_veh_num = len(list(set(df[df['period'] == 2]['vhc_no'])))
        print("早高峰违规出行车辆数{0}辆,可能被限行影响的车辆共{1}辆,总车辆数{2}辆."
              "晚高峰违规出行车辆数{3}辆,可能被限行影响的车辆共{4}辆,总车辆数{5}辆.".format(len(tmp_morn_illegal_df) ,len(tmp_morn_df),
                                                                morn_veh_num,len(tmp_even_illegal_df) , len(tmp_even_df) , even_veh_num))

if __name__ == "__main__":
    travel_illegal.get_illegal_ratio(LPR_file="E:\\study_e\\HZMultiSourceData\\LPRData_after_process\\HZ_LPRdata_419.csv",
                                     dev_file="../../data/restriction_pol/严格清洗版限行区内电警卡口设备.csv",
                                     res_plate1='1', res_plate2='9')









