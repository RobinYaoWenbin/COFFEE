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

def get_tag(x):
    if len(x)==8:
        return 1
    else:
        return 0

def get_period(x,research_hour_start,research_hour_end):
    x = x[11:]
    if x >= research_hour_start and x <= research_hour_end:
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

def adj_ratio(x):
    return (2/(1/x - 2))

class tra_time_adj:
    def __init__(self):
        pass
    @staticmethod
    def get_vehnum_with_dif_tailplate(LPR_file,research_hour_start,research_hour_end,data_save_file):
        df = pd.read_csv(LPR_file, encoding='gbk')
        df['tag'] = df[['vhc_no']].applymap(get_tag)
        df['period'] = df['inner_rec_time'].apply(get_period,args=(research_hour_start,research_hour_end,))
        tmp_df = df[(df['tag'] == 0) & (df['period'] == 1)]
        tmp_df['final_num'] = tmp_df[['vhc_no']].applymap(get_final_num)
        tmp_df.drop_duplicates(subset=['vhc_no'], keep='first', inplace=True)
        tmp_df = tmp_df.groupby(['final_num'])['vhc_no'].count().reset_index().rename(columns={'vhc_no':'count'})
        tmp_df = tmp_df[tmp_df['final_num']>='0']
        sum_value = sum(tmp_df['count'])
        tmp_df['ratio'] = tmp_df['count'] / sum_value
        tmp_df.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def ana_tra_adj(res_day_file,unres_day_file,res_plate1,res_plate2):
        df_res = pd.read_csv(res_day_file,encoding='gbk')
        df_res.rename(columns={'count':'res_count','ratio':'res_ratio'},inplace=True)
        df_unres = pd.read_csv(unres_day_file,encoding='gbk')
        df_unres.rename(columns={'count': 'unres_count', 'ratio': 'unres_ratio'}, inplace=True)
        df = pd.merge(df_res,df_unres,how='inner',on='final_num')
        resplate_num_in_res_day = sum(df[df['final_num'] == res_plate1]['res_count']) + sum(df[df['final_num'] == res_plate2]['res_count'])
        resplate_num_in_nonres_day = sum(df[df['final_num'] == res_plate1]['unres_count']) + sum(df[df['final_num'] == res_plate2]['unres_count'])
        unresplate_num_in_res_day = sum(df[(df['final_num'] != res_plate1) & (df['final_num'] != res_plate2)]['res_count'])
        unresplate_num_in_nonres_day = sum(df[(df['final_num'] != res_plate1) & (df['final_num'] != res_plate2)]['unres_count'])
        print("在限行日该时间段,限行车牌和不限行车牌的比例为{0}。在非限行日该时间段，限行车牌和不限行车牌的比例为{1}。比例差值为{2}".format(
            resplate_num_in_res_day/unresplate_num_in_res_day , resplate_num_in_nonres_day/unresplate_num_in_nonres_day ,
             resplate_num_in_res_day/unresplate_num_in_res_day - resplate_num_in_nonres_day/unresplate_num_in_nonres_day
        ))
        df['unres_ratio'] = df[['unres_ratio']].applymap(adj_ratio)
        df['res_ratio'] = df[['res_ratio']].applymap(adj_ratio)
        df['diff'] = (df['res_ratio'] - df['unres_ratio'])
        # df['diff'] = df['diff'].abs()
        dif_std = (df[(df['final_num'] != res_plate1) & (df['final_num'] != res_plate2)]['diff'].std())
        dif_mean = (df[(df['final_num'] != res_plate1) & (df['final_num'] != res_plate2)]['diff'].mean())
        print("不限行车牌在限行日和非限行日的差值的标准差为{0}，均值为{1}".format(dif_std , dif_mean))

if __name__ == "__main__":
    # tra_time_adj.get_vehnum_with_dif_tailplate(LPR_file="E:\\study_e\\HZMultiSourceData\\LPRData_after_process\\HZ_LPRdata_419.csv",
    #                                            research_hour_start='06:00:00',
    #                                            research_hour_end='07:00:00',
    #                                            data_save_file="../../data/restriction_pol/各尾号车辆数量/morning67_419.csv")

    tra_time_adj.ana_tra_adj(res_day_file="../../data/restriction_pol/各尾号车辆数量/419_06_07.csv",
                             unres_day_file="../../data/restriction_pol/各尾号车辆数量/425_06_07.csv",
                            res_plate1=1, res_plate2=9)

