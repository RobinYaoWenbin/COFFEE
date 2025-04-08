import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
sys.path.append("../pol_est_sim/")
sys.path.append("../IBTDM_multi_city/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import utils
import copy
import time, datetime
import get_trips_distribution
import simu_traffic
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class ran_ind_simu:
    def __init__(self):
        pass
    @staticmethod
    def start(trip_dis_file_path,v_n_rela_file,free_speed,ts,data_save_path):
        file_name_list = os.listdir(trip_dis_file_path)
        for file in file_name_list:
            print("正在处理{0}文件.".format(file))
            filename = file.split(".")[0]
            data_save_file = data_save_path+filename+".csv"
            simu_obj = simu_traffic.simu(
                trip_dis_file=trip_dis_file_path+file,
                v_n_rela_file=v_n_rela_file,
                free_speed=free_speed, ts=ts)
            simu_obj.traffic_simu()
            simu_obj.plot(data_save_file=data_save_file)
    @staticmethod
    def start_xiaoshan(trip_dis_file_path,v_n_rela_file,free_speed,ts,data_save_path):
        file_name_list = os.listdir(trip_dis_file_path)
        for file in file_name_list:
            print("正在处理{0}文件.".format(file))
            filename = file.split(".")[0]
            data_save_file = data_save_path+filename+".csv"
            simu_obj = simu_traffic_xiaoshan.simu(
                trip_dis_file=trip_dis_file_path+file,
                v_n_rela_file=v_n_rela_file,
                free_speed=free_speed, ts=ts)
            simu_obj.traffic_simu()
            simu_obj.plot(data_save_file=data_save_file)

    @staticmethod
    def start_kunming(trip_dis_file_path, v_n_rela_file, free_speed, ts, data_save_path):
        file_name_list = os.listdir(trip_dis_file_path)
        for file in file_name_list:
            print("正在处理{0}文件.".format(file))
            filename = file.split(".")[0]
            data_save_file = data_save_path + filename + ".csv"
            simu_obj = simu_traffic_kunming.simu(
                trip_dis_file=trip_dis_file_path + file,
                v_n_rela_file=v_n_rela_file,
                free_speed=free_speed, ts=ts)
            simu_obj.traffic_simu()
            simu_obj.plot(data_save_file=data_save_file)
    @staticmethod
    def sample_rate_pol_eva_result_vis(simu_result_path,speed_load_file,data_save_file):
        df = pd.read_csv(speed_load_file,encoding='gbk')
        df.rename(columns={'speed':'origin_speed','netload':'origin_netload'},inplace=True)
        file_name_list = os.listdir(simu_result_path)
        sam_rate_list = []
        for file in file_name_list:
            sam_rate = file.split(".")[0].split("_")[-1]
            sam_rate_list.append(sam_rate)
            tmp_df = pd.read_csv(simu_result_path+file,encoding='gbk')
            tmp_df.rename(columns={'speed':'speed_'+str(sam_rate),'netload':'netload_'+str(sam_rate)} , inplace=True)
            df  = pd.merge(df  ,tmp_df , how='inner' , on='ts')
        fontsize = 15
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        fig, axes = plt.subplots()
        fig.set_size_inches(10, 8)
        lns1 = axes.plot(df['ts'], df['origin_speed'], '.-', label='original $V_a$',
                         linewidth=2,markersize=4.8)
        lns = lns1
        for sam_rate in sam_rate_list:
            lns2 = axes.plot(df['ts'], df['speed_'+str(sam_rate)], '.-', label='$V_a$ under {0}% trips induced'.format(sam_rate),
                         linewidth=2, markersize=4.8)
            lns += lns2
        twin_axes = axes.twinx()
        lns2 = twin_axes.plot(df['ts'], df['origin_netload'], '--', label='original $N_l$',
                              linewidth=2,
                              markersize=4.8)
        lns += lns2
        for sam_rate in sam_rate_list:
            lns2 = twin_axes.plot(df['ts'], df['netload_'+str(sam_rate)], '--', label='$N_l$ under {0}% trips induced'.format(sam_rate),
                         linewidth=2, markersize=4.8)
            lns += lns2
        axes.set_xlabel("Time slots", fontsize=fontsize)
        axes.set_ylabel("Average speed (km/h)", fontsize=fontsize)
        twin_axes.set_ylabel("Network load", fontsize=fontsize)
        plt.setp(axes.get_xticklabels(), fontsize=fontsize)
        plt.setp(axes.get_yticklabels(), fontsize=fontsize)
        plt.setp(twin_axes.get_yticklabels(), fontsize=fontsize)
        labs = [l.get_label() for l in lns]
        # num1 = 1.09; num2=0; num3 = 3; num4 = 0
        # axes.legend(lns, labs, fontsize=fontsize, frameon=False,ncol=1,bbox_to_anchor=(num1, num2), loc=num3, borderaxespad=num4)
        axes.legend(lns, labs, fontsize=fontsize-3, frameon=False, ncol=1)
        df.to_csv(data_save_file,index=False,encoding='gbk')
        plt.show()

if __name__ == "__main__":
    # ran_ind_simu.start(trip_dis_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_15_trip_distribution\\",
    #                    v_n_rela_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\mfd拟合结果_newell.npy",
    #                    free_speed=39.75,ts=15,
    #                    data_save_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_15_pol_eva_result\\")
    # ran_ind_simu.sample_rate_pol_eva_result_vis(simu_result_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_15_pol_eva_result\\",
    #                                             speed_load_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv",
    #                                             data_save_file="E:\\study_e\\analysis_of_IBTDM\data\\random_ind_pol_eva_data\\policy_1\\adjust_15_simu_traffic_state.csv")
    # ran_ind_simu.sample_rate_pol_eva_result_vis(
    #     simu_result_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_1\\adjust_30_pol_eva_result\\",
    #     speed_load_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv",
    #     data_save_file="E:\\study_e\\analysis_of_IBTDM\data\\random_ind_pol_eva_data\\policy_1\\adjust_30_simu_traffic_state.csv")
    # ran_ind_simu.sample_rate_pol_eva_result_vis(
    #     simu_result_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_2\\adjust_15_pol_eva_result\\",
    #     speed_load_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv",
    #     data_save_file="E:\\study_e\\analysis_of_IBTDM\data\\random_ind_pol_eva_data\\policy_2\\adjust_15_simu_traffic_state.csv")
    ran_ind_simu.sample_rate_pol_eva_result_vis(
        simu_result_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_ind_pol_eva_data\\policy_2\\adjust_30_pol_eva_result\\",
        speed_load_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv",
        data_save_file="E:\\study_e\\analysis_of_IBTDM\data\\random_ind_pol_eva_data\\policy_2\\adjust_30_simu_traffic_state.csv")