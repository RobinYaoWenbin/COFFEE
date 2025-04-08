import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
sys.path.append("../pol_est_sim/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import utils
import copy
import time, datetime
import get_trips_distribution
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class trip_dis:
    def __init__(self):
        pass
    @staticmethod
    def get_free_speed_trip_file(OD_file_with_free_speed,trip_after_pol,data_save_file):
        df_free = pd.read_csv(OD_file_with_free_speed,encoding='gbk')
        df_trip = pd.read_csv(trip_after_pol , encoding='gbk')
        df_trip['tss'] = df_trip['ori_sec'].apply(utils.get_timeslots, args=(15,))
        print(len(df_trip))
        df_trip = pd.merge(df_trip,df_free[['vhc_no','ori_sec','origin','des_sec','destination','free_tratime']],how='inner',on=['vhc_no','ori_sec','origin','des_sec','destination'])
        df_trip = df_trip[['vhc_no','tss','free_tratime']]
        print(len(df_trip))
        df_trip.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def get_random_ind_free_speed_trip_file(random_ind_trip_file_path,OD_file_with_free_speed,data_save_path):
        file_name_list = os.listdir(random_ind_trip_file_path)
        for file in file_name_list:
            print("正在处理{0}文件.".format(file))
            data_save_file_name = data_save_path+file
            trip_dis.get_free_speed_trip_file(OD_file_with_free_speed=OD_file_with_free_speed,
                                              trip_after_pol=random_ind_trip_file_path+file,
                                              data_save_file=data_save_file_name)
    @staticmethod
    def get_distribution_ran_ind(OD_free_speed_file_path,output_file_path,ts):
        file_name_list = os.listdir(OD_free_speed_file_path)
        for file in file_name_list:
            print("正在处理{0}文件.".format(file))
            filename = file.split(".")[0]
            save_file = output_file_path+filename+'.npy'
            get_trips_distribution.trips_dis.get_distribution(OD_file_free_speed=OD_free_speed_file_path+file,
                                                              ts=ts,trip_distribution_file=save_file)

if __name__ == "__main__":
    trip_dis.get_free_speed_trip_file(OD_file_with_free_speed="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\OD_with_freespeed_0425.csv",
                                      trip_after_pol="../../data/congestion_pricing/OD_sample_425.csv",
                                      data_save_file="../../data/congestion_pricing/trip_freespeed_after_pol.csv")
    # # trip_dis.get_random_ind_free_speed_trip_file(random_ind_trip_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\adjust_diff_sample_15\\",
    # #                                              OD_file_with_free_speed="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\OD_with_freespeed_0419.csv",
    # #                                              data_save_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_diff_sample_15\\")
    # trip_dis.get_distribution_ran_ind(OD_free_speed_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_diff_sample_15\\",
    #                                   output_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_15_trip_distribution\\",ts=15)