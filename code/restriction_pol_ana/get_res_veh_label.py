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

def get_period(x):
    # 0:不限行；1：早高峰限行；2：晚高峰限行
    x=x[11:]
    if x>='07:00:00' and x<='09:00:00':
        return 1
    elif x>='16:30:00' and x<='18:30:00':
        return 2
    else:
        return 0

def get_tag(x):
    if len(x)==8:
        return 1
    else:
        return 0

class get_res_veh_label:
    def __init__(self):
        pass
    @staticmethod
    def start(LPR_file,dev_file,res_plate1,veh_por_file,res_plate2,data_save_file):
        df = pd.read_csv(LPR_file, encoding='gbk')
        dev_df = pd.read_csv(dev_file, encoding='gbk')
        df = pd.merge(df, dev_df, how='inner', left_on='devc_id', right_on='id')
        df['period'] = df[['inner_rec_time']].applymap(get_period)
        df['tag'] = df[['vhc_no']].applymap(get_tag)
        df['final_num'] = df[['vhc_no']].applymap(get_final_num)
        df = df[( (df['period'] == 1) | (df['period'] == 2)) & (df['tag'] == 0) &
                          ( (df['final_num'] == '-2') | (df['final_num'] == res_plate1) | (df['final_num'] == res_plate2) ) ]
        df = df[['devc_id','vhc_no','inner_rec_time','final_num','period']]
        df_veh_por = pd.read_csv(veh_por_file,encoding='gbk')
        df = pd.merge(df , df_veh_por[['vhc_no','label']] , how='inner', on='vhc_no')
        df.to_csv(data_save_file,index=False,encoding='gbk')

if __name__  == "__main__":
    get_res_veh_label.start(LPR_file="E:\\study_e\\HZMultiSourceData\\LPRData_after_process\\HZ_LPRdata_425.csv",
                            dev_file="../../data/restriction_pol/严格清洗版限行区内电警卡口设备.csv",
                            veh_por_file="E:\\study_e\\analysis_of_IBTDM\\data\\veh_portrait\\veh_all_sam_portrait.csv",
                            res_plate1='0',res_plate2='5',
                            data_save_file="../../data/restriction_pol/4月25日限行时段可能受限行影响的车辆.csv")




