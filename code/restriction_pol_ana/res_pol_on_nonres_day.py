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

def get_period(ser):
    if  not (ser['cap_date_des'][11:]<'07:00:00' or ser['cap_date_ori'][11:]>'09:00:00') :
        return 1 # 包括早高峰限行时段
    elif not (ser['cap_date_des'][11:]<'16:30:00' or ser['cap_date_ori'][11:]>'18:30:00'):
        return 2 # 包括晚高峰限行时段
    else:
        return 0 # 其他时段
def get_period2(ser):
    if not (ser['cap_date_des'][11:]<'06:00:00' or ser['cap_date_ori'][11:]>'07:00:00') :
        return 1 # 包括早高峰限行时段前一个小时
    elif not (ser['cap_date_des'][11:]<'15:30:00' or ser['cap_date_ori'][11:]>'16:30:00'):
        return 2 # 包括晚高峰限行时段前一个小时
    else:
        return 0 # 其他时段

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

def get_tag(x):
    if len(x)==8:
        return 1
    else:
        return 0

class analysis:
    def __init__(self):
        pass
    @staticmethod
    def tra_change(OD_file,morn_illegal,even_illegal,morn_advance,even_cancel,res_plate1,res_plate2):
        df = pd.read_csv(OD_file,  encoding='gbk')
        df['period'] = df.apply(get_period,axis=1)
        morn_illegal_num = len(set(df[df['period'] == 1]['vhc_no_ori'])) * morn_illegal
        even_illegal_num = len(set(df[df['period'] == 2]['vhc_no_ori'])) * even_illegal
        df['period2'] = df.apply(get_period2,axis=1)
        df['tag'] = df[['vhc_no_ori']].applymap(get_tag)
        df['final_num'] = df[['vhc_no_ori']].applymap(get_final_num)
        tmp_df =  df[(df['tag'] == 0) & (df['period2'] == 1)]
        tmp_df = tmp_df[(tmp_df['final_num']!=res_plate1) & (tmp_df['final_num']!=res_plate2) & (tmp_df['final_num']!='-1')
                        & (tmp_df['final_num']!='-2')]
        morn_advance_num = len(set(tmp_df['vhc_no_ori']))*morn_advance
        tmp_df = df[(df['tag'] == 0) & (df['period2'] == 2)]
        tmp_df = tmp_df[
            (tmp_df['final_num'] != res_plate1) & (tmp_df['final_num'] != res_plate2) & (tmp_df['final_num'] != '-1')
            & (tmp_df['final_num']!='-2')]
        even_cancel_num = len(set(tmp_df['vhc_no_ori'])) * even_cancel
        print("早高峰违规出行车辆数为{0}辆，晚高峰违规出行车辆数为{1}辆。早高峰提前出行车辆数为{2}辆,晚高峰前一小时取消出行车辆数为{3}辆".format(
            morn_illegal_num,even_illegal_num,morn_advance_num,even_cancel_num
        ))

if __name__ == "__main__":
    analysis.tra_change(OD_file="../../data/ODFile/OD_425.csv",
                        morn_illegal=0.0216,even_illegal=0.0231,morn_advance=0.0507,even_cancel=0.0296,
                        res_plate1='0', res_plate2='5')