import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
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

class induce:
    def __init__(self):
        pass
    @staticmethod
    def change_travel(OD_file,time_start,time_end,time_thre,adj_tag,sample_rate,data_save_file,ts):
        '''
        对出行进行诱导
        :param OD_file:出行文件
        :param time_start:分析时段的起始时刻，单位为秒
        :param time_end:分析时段的结束时候，单位为秒
        :param time_thre:调整时间阈值，单位为time slots，即调整time thre个time slots
        :param adj_tag:调整策略为提早还是延后，提早则为0，延后则为1
        :param sample_rate:抽样率，该值是一个0到1的值
        :param data_save_file:调整后的文件的保存路径
        :param ts:time slot长度，单位为分钟
        :return:
        '''
        df = pd.read_csv(OD_file,encoding='gbk')
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df = df[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df['M'] = df[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df['tss'] = df['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df['tso'] = df['des_sec'].apply(utils.get_timeslots, args=(ts,))
        df_adj = df[(df['ori_sec']>=time_start) & (df['ori_sec']<=time_end)]
        df_other = df[(df['ori_sec']<time_start) | (df['ori_sec']>time_end)]
        df_adj = df_adj.sample(frac=1.0) # 乱序重排
        df_adj.reset_index(drop=True,inplace=True)
        df_adj_sample = df_adj.iloc[ 0:int(len(df_adj)*sample_rate) , : ]
        df_adj_other =df_adj.iloc[ int(len(df_adj)*sample_rate): , : ]
        if adj_tag == 0:
            df_adj_sample['delay'] = -time_thre
        elif adj_tag == 1:
            df_adj_sample['delay'] = time_thre
        else:
            print("并未进行出行时间的调整，若需调整，请输入adj_tag为0或1")
        df_adj_other['delay'] = 0
        df_other['delay'] = 0
        df_after_adj = df_adj_sample.append(df_adj_other,ignore_index=True)
        df_after_adj = df_after_adj.append(df_other , ignore_index=True)
        df_after_adj.to_csv(data_save_file,index=False,encoding='gbk')
        return df_after_adj
    @staticmethod
    def change_travel_with_induce_file(induce_file,time_start,time_end,time_thre,adj_tag,sample_rate,data_save_file):
        '''
        对出行进行诱导
        :param induce_file:该文件为change_travel函数或change_travel_with_induce_file函数的输出文件，即该函数对已经进行诱导的出行再次诱导(需在不同时段)
        :param time_start:分析时段的起始时刻，单位为秒
        :param time_end:分析时段的结束时候，单位为秒
        :param time_thre:调整时间阈值，单位为time slots，即调整time thre个time slots
        :param adj_tag:调整策略为提早还是延后，提早则为0，延后则为1
        :param sample_rate:抽样率，该值是一个0到1的值
        :param data_save_file:调整后的文件的保存路径
        :return:
        '''
        df = pd.read_csv(induce_file,encoding='gbk')
        df_adj = df[(df['ori_sec']>=time_start) & (df['ori_sec']<=time_end)]
        df_other = df[(df['ori_sec']<time_start) | (df['ori_sec']>time_end)]
        df_adj = df_adj.sample(frac=1.0) # 乱序重排
        df_adj.reset_index(drop=True,inplace=True)
        df_adj_sample = df_adj.iloc[ 0:int(len(df_adj)*sample_rate) , : ]
        df_adj_other =df_adj.iloc[ int(len(df_adj)*sample_rate): , : ]
        if adj_tag == 0:
            df_adj_sample['delay'] = -time_thre
        elif adj_tag == 1:
            df_adj_sample['delay'] = time_thre
        else:
            print("并未进行出行时间的调整，若需调整，请输入adj_tag为0或1")
        df_after_adj = df_adj_sample.append(df_adj_other,ignore_index=True)
        df_after_adj = df_after_adj.append(df_other , ignore_index=True)
        df_after_adj.to_csv(data_save_file,index=False,encoding='gbk')
        return df_after_adj
    @staticmethod
    def get_trip_file_diff_samplerate(sample_list,time_thre,OD_file,save_file_path,ts,time_start_morn,time_end_morn,time_start_even,time_end_even):
        for i in range(len(sample_list)):
            tmp_sample_rate = sample_list[i]
            print("正在处理抽样率{0}".format(tmp_sample_rate))
            tmp_save_file = save_file_path+'adj_trips_'+str(int(tmp_sample_rate*100))+'.csv'
            induce.change_travel(OD_file=OD_file,time_start=time_start_morn,time_end=time_end_morn,time_thre=time_thre,
                                 adj_tag=0,sample_rate=tmp_sample_rate,
                                 data_save_file=tmp_save_file,ts=ts)
            print("抽样率{0}下早高峰已完成随机诱导".format(tmp_sample_rate))
            induce.change_travel_with_induce_file(induce_file=tmp_save_file, time_start=time_start_even, time_end=time_end_even,
                                        time_thre=time_thre, adj_tag=1, sample_rate=tmp_sample_rate,
                                        data_save_file=tmp_save_file)



if __name__ == "__main__":
    # induce.change_travel(OD_file="E:\\study_e\\analysis_of_IBTDM\\data\\ODFile\\OD_419.csv",
    #                      time_start=26100,time_end=38700,time_thre=1,adj_tag=0,sample_rate=0.05,
    #                     data_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\OD_induce_morning.csv",
    #                      ts=15)
    # df = induce.change_travel_with_induce_file(induce_file="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\OD_induce_morning.csv",
    #                      time_start=57600,time_end=68400,time_thre=1,adj_tag=1,sample_rate=0.05,
    #                     data_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\OD_induce_allday.csv")
    # print(df)
    induce.get_trip_file_diff_samplerate(sample_list=[0.05,0.1,0.2,0.3,0.4,0.5],time_thre=1,
                                         OD_file="E:\\study_e\\analysis_of_IBTDM\\data\\ODFile\\OD_419.csv",
                                         save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\adjust_diff_sample_15\\",
                                         ts=15,time_start_morn=26100,time_end_morn=38700,time_start_even=57600,time_end_even=68400)