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
import copy
import time, datetime
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class get_trips:
    def __init__(self):
        pass
    @staticmethod
    def filt(OD_file,opt_trips_data_save_file,other_data_save_path):
        df = pd.read_csv(OD_file,encoding='gbk')
        #将行程的开始时间和结束时间转化为分钟
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df_opt = df[(df['des_sec'] >= 23400) & (df['ori_sec'] <= 38700) & (df['ori_sec'] >= 1800) & (df['des_sec'] <= 84600)]
        df_opt = df_opt[['vhc_no_ori','cap_date_ori','ori_sec','origin','cap_date_des','des_sec','destination','tratime']]
        df_opt.rename(columns={'vhc_no_ori':'vhc_no'},inplace=True)
        df_opt.to_csv(opt_trips_data_save_file,encoding='gbk',index=False)
        df_other = df[(df['des_sec'] < 23400) | (df['ori_sec'] > 38700) | (df['ori_sec'] < 1800) | (df['des_sec'] > 84600)]
        df_other = df_other[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df_other.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df_other.to_csv(other_data_save_path, encoding='gbk', index=False)
        return df_opt

    @staticmethod
    def filt_afternoon(OD_file, opt_trips_data_save_file, other_data_save_path):
        df = pd.read_csv(OD_file, encoding='gbk')
        df_opt = df[(df['des_sec'] >= 48600) & (df['ori_sec'] <= 68400) & (df['ori_sec'] >= 1800) & (df['des_sec'] <= 84600)]
        df_opt.to_csv(opt_trips_data_save_file, encoding='gbk', index=False)
        df_other = df[(df['des_sec'] < 48600) | (df['ori_sec'] > 68400) | (df['ori_sec'] < 1800) | (df['des_sec'] > 84600)]
        df_other.to_csv(other_data_save_path, encoding='gbk', index=False)
        return df_opt

    @staticmethod
    def format_convert(OD_file, data_save_file):
        df = pd.read_csv(OD_file, encoding='gbk')
        df['ori_sec'] = df[['cap_date_ori']].applymap(utils.t2s_fulltime)
        df['des_sec'] = df[['cap_date_des']].applymap(utils.t2s_fulltime)
        df = df[['vhc_no_ori', 'cap_date_ori', 'ori_sec', 'origin', 'cap_date_des', 'des_sec', 'destination', 'tratime']]
        df.rename(columns={'vhc_no_ori': 'vhc_no'}, inplace=True)
        df.to_csv(data_save_file, encoding='gbk', index=False)
        return df

if __name__ == "__main__":
    get_trips.filt(OD_file="E:\\study_e\\analysis_of_IBTDM\\data\\ODFile\\OD_419.csv",
                   opt_trips_data_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_morning_419.csv",
                   other_data_save_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\other_trips_morning_419.csv")