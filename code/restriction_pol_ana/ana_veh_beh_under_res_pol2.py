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

class analysis:
    def __init__(self):
        pass
    @staticmethod
    def veh_reaction(res_veh , LPR_file , dev_file,data_save_file):
        df_res_veh = pd.read_csv(res_veh , encoding='gbk')
        df_ori_day = pd.read_csv(LPR_file , encoding='gbk')
        df_ori_day['time'] = df_ori_day[['inner_rec_time']].applymap(lambda x: x[11:])
        df_ori_day = pd.merge(df_ori_day,df_res_veh[['vhc_no']],how='inner',on='vhc_no')
        dev_df = pd.read_csv(dev_file, encoding='gbk')
        df_ori_day = pd.merge(df_ori_day, dev_df, how='inner', left_on='devc_id', right_on='id')
        res_veh_set = list(set(df_res_veh['vhc_no']))
        reaction_morn_list = []
        reaction_even_list = []
        print("需处理的车辆数",len(res_veh_set))
        for i in range(len(res_veh_set)):
            if i % 5000 == 0:
                print("已经处理到{0}%".format( round(i/len(res_veh_set)*100,2) ))
            tmp_veh = res_veh_set[i]
            tmp_label = list(df_res_veh[df_res_veh['vhc_no'] == tmp_veh]['label'])[0]
            if tmp_label == 5:
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 1)]) > 0:
                    reaction_morn_list.append(0)
                else:
                    reaction_morn_list.append(999)
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 2)]) > 0:
                    reaction_even_list.append(0)
                else:
                    reaction_even_list.append(999)
            elif tmp_label == 4:
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 1)]) > 0:
                    if max(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 1)]['inner_rec_time'])[11:] >'08:00:00':
                        reaction_morn_list.append(1)
                    else:
                        reaction_morn_list.append(-1)
                else:
                    reaction_morn_list.append(999)
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 2)]) > 0:
                    if max(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 2)]['inner_rec_time'])[11:] >'17:30:00':
                        reaction_even_list.append(1)
                    else:
                        reaction_even_list.append(-1)
                else:
                    reaction_even_list.append(999)
            else:
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 1)]) > 0:
                    if len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] > '07:00:00') & (df_ori_day['time'] < '09:00:00')])>0:
                        reaction_morn_list.append(3)
                    else:
                        if len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] >= '06:00:00') & (df_ori_day['time'] <= '07:00:00')])>0:
                            reaction_morn_list.append(-1)
                        elif len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] >= '09:00:00') & (df_ori_day['time'] <= '10:00:00')])>0:
                            reaction_morn_list.append(1)
                        else:
                            reaction_morn_list.append(2)
                else:
                    reaction_morn_list.append(999)
                if len(df_res_veh[(df_res_veh['vhc_no'] == tmp_veh) & (df_res_veh['period'] == 2)]) > 0:
                    if len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] > '16:30:00') & (df_ori_day['time'] < '18:30:00')])>0:
                        reaction_even_list.append(3)
                    else:
                        if len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] >= '15:30:00') & (df_ori_day['time'] <= '16:30:00')])>0:
                            reaction_even_list.append(-1)
                        elif len(df_ori_day[(df_ori_day['vhc_no'] == tmp_veh) & (df_ori_day['time'] >= '18:30:00') & (df_ori_day['time'] <= '19:30:00')])>0:
                            reaction_even_list.append(1)
                        else:
                            reaction_even_list.append(2)
                else:
                    reaction_even_list.append(999)
        tmp_period_list = [1 for i in range(len(res_veh_set))]
        tmp_morn_df_beh = pd.DataFrame({'vhc_no':res_veh_set,'period':tmp_period_list,'reaction':reaction_morn_list})
        tmp_period_list = [2 for i in range(len(res_veh_set))]
        tmp_even_df_beh = pd.DataFrame({'vhc_no':res_veh_set,'period':tmp_period_list,'reaction':reaction_even_list})
        tmp_reac_df = tmp_morn_df_beh.append(tmp_even_df_beh,ignore_index=True)
        df_res_veh = pd.merge(df_res_veh,tmp_reac_df,how='inner',on=['vhc_no','period'])
        df_res_veh.drop_duplicates(subset=['vhc_no','period','label'], inplace=True)
        # print(df_res_veh)
        df_res_veh.to_csv(data_save_file,index=False,encoding='gbk')

    @staticmethod
    def get_reaction_ratio(reaction_file,morn_reaction_file,even_reaction_file):
        df = pd.read_csv(reaction_file , encoding='gbk')
        # 早高峰情况分析
        tmp_morn_df = df[(df['period'] == 1) & (df['reaction'] !=999)]
        # print(tmp_morn_df[tmp_morn_df['reaction']==0])
        morn_ratio_df = tmp_morn_df.groupby(['reaction'])[['vhc_no']].count().reset_index().rename(columns={'vhc_no':'veh_num'})
        morn_ratio_df['ratio'] = morn_ratio_df['veh_num'] / len(tmp_morn_df)
        print(morn_ratio_df)
        morn_ratio_df.to_csv(morn_reaction_file,index=False,encoding='gbk')
        tmp_even_df = df[(df['period'] == 2) & (df['reaction'] != 999)]
        even_ratio_df = tmp_even_df.groupby(['reaction'])[['vhc_no']].count().reset_index().rename(
            columns={'vhc_no': 'veh_num'})
        even_ratio_df['ratio'] = even_ratio_df['veh_num'] / len(tmp_even_df)
        print(even_ratio_df)
        even_ratio_df.to_csv(even_reaction_file,index=False,encoding='gbk')

if __name__ == "__main__":
    # analysis.veh_reaction(res_veh="../../data/restriction_pol/4月25日限行时段可能受限行影响的车辆.csv" ,
    #                       LPR_file="E:\\study_e\\HZMultiSourceData\\LPRData_after_process\\HZ_LPRdata_423.csv" ,
    #                       dev_file="../../data/restriction_pol/严格清洗版限行区内电警卡口设备.csv",
    #                       data_save_file="../../data/restriction_pol/4月25日可能受到限行影响车辆反应.csv")

    analysis.get_reaction_ratio(reaction_file="../../data/restriction_pol/4月25日可能受到限行影响车辆反应.csv",
                                morn_reaction_file="../../data/restriction_pol/限行下的车辆反应比例/早高峰限行反应比例.csv",
                                even_reaction_file="../../data/restriction_pol/限行下的车辆反应比例/晚高峰限行反应比例.csv")