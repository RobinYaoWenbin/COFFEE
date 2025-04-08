import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import utils
import copy
import time, datetime
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def get_real_speed(ser,df_speed):
    tss = ser['tss'] ; tso = ser['tso']
    real_speed = df_speed[(df_speed['ts']>=tss) & (df_speed['ts']<=tso)]['speed'].mean()
    return real_speed

class trips_dis:
    def __init__(self):
        pass
    @staticmethod
    def get_free_speed_trip_file(OD_file,speed_file,free_speed,output_file,ts):
        df_OD = pd.read_csv(OD_file,encoding='gbk')
        df_speed = pd.read_csv(speed_file,encoding='gbk')
        df_OD['ori_sec'] = df_OD[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df_OD['des_sec'] = df_OD[['cap_date_des']].applymap(utils.t2s_fulltime)
        df_OD = df_OD[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df_OD.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df_OD['M'] = df_OD[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df_OD['tss'] = df_OD['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df_OD['tso'] = df_OD['des_sec'].apply(utils.get_timeslots, args=(ts,))
        df_OD['real_speed'] = df_OD[['tss','tso']].apply(get_real_speed,args=(df_speed,),axis=1)
        df_OD['coef'] = df_OD['real_speed'] / free_speed
        df_OD['free_tratime'] = df_OD['tratime'] * df_OD['coef']
        df_OD.to_csv(output_file,index=False,encoding='gbk')
    @staticmethod
    def get_distribution(OD_file_free_speed,ts,trip_distribution_file):
        df = pd.read_csv(OD_file_free_speed,encoding='gbk')
        trip_dis = {}  # 存储各个time slot的出行关于自由流行程时间的分布
        for ith in range(int(24*60/ts)):
            tmp_df = df[df['tss'] == ith]
            tmp_df = tmp_df[['vhc_no','tss','free_tratime']]
            tmp_df.reset_index(drop=True,inplace=True)
            trip_dis[ith]=tmp_df
        np.save(trip_distribution_file, trip_dis)


if __name__ == "__main__":
    # trips_dis.get_free_speed_trip_file(OD_file="E:\\study_e\\analysis_of_IBTDM\\data\\ODFile\\OD_419.csv",
    #                                    speed_file="E:\\study_e\\analysis_of_IBTDM\\data\\speedfile\\speed_0419.csv",
    #                                    free_speed=39.75,output_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\OD_with_freespeed_0419.csv",
    #                                    ts=15)
    trips_dis.get_distribution(OD_file_free_speed="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\OD_with_freespeed_0419.csv",
                               ts=15,trip_distribution_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\trip_distribution_0419.npy")