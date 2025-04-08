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
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import utils
import copy
import time, datetime
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class simu:
    def __init__(self,trip_dis_file,v_n_rela_file,free_speed,ts):
        self.trip_dis = np.load(trip_dis_file, allow_pickle='TRUE').item()
        popt1 = np.load(v_n_rela_file)
        self.popt1 = popt1.tolist()
        # self.v_n_func = utils.exp_func
        self.v_n_func = utils.newell_model
        # print(self.v_n_func(np.array([1000,60000]),self.popt1[0],self.popt1[1],self.popt1[2] ))
        self.n_list = []  # 存储各个time slot的network load
        self.v_list = []  # 存储各个time slot的speed
        self.remain_demand = []  # 存储各个time slot结束时的剩余需求
        self.tol_demand = []  # 存储各个time slot的总需求
        self.free_speed = free_speed
        self.ts = ts
    def ini_simu(self):
        tmp_n = len(self.trip_dis[0])
        tmp_v = self.v_n_func(np.array([tmp_n]), self.popt1[0], self.popt1[1], self.popt1[2])[0]
        tmp_trip_dis = self.trip_dis[0]
        self.tol_demand.append(tmp_trip_dis)
        self.n_list.append(tmp_n)
        self.v_list.append(tmp_v)
        coef = tmp_v / self.free_speed
        finished_demand = self.ts*60*coef
        tmp_trip_dis['free_tratim'] = tmp_trip_dis['free_tratime'] - finished_demand
        tmp_trip_dis = tmp_trip_dis[tmp_trip_dis['free_tratime'] > 0 ]
        tmp_trip_dis.reset_index(drop=True,inplace=True)
        self.remain_demand.append(tmp_trip_dis)
    def step_simu(self,step_i):
        last_ts_remain_demand = self.remain_demand[step_i-1]
        this_ts_demand = self.trip_dis[step_i]
        tmp_tol_demand = last_ts_remain_demand.append(this_ts_demand,ignore_index=True)
        tmp_n = len(tmp_tol_demand)
        tmp_v = self.v_n_func(np.array([tmp_n]), self.popt1[0], self.popt1[1], self.popt1[2])[0]
        self.tol_demand.append(tmp_tol_demand)
        self.n_list.append(tmp_n)
        self.v_list.append(tmp_v)
        coef = tmp_v / self.free_speed
        finished_demand = self.ts * 60 * coef
        last_ts_remain_demand['free_tratime'] = last_ts_remain_demand['free_tratime'] - finished_demand
        last_ts_remain_demand = last_ts_remain_demand[last_ts_remain_demand['free_tratime'] > 0]
        this_ts_demand['free_tratime'] = this_ts_demand['free_tratime'] - finished_demand*0.6
        this_ts_demand = this_ts_demand[this_ts_demand['free_tratime'] > 0]
        remain_tol_demand = last_ts_remain_demand.append(this_ts_demand,ignore_index=True)
        remain_tol_demand.reset_index(drop=True, inplace=True)
        self.remain_demand.append(remain_tol_demand)
    def traffic_simu(self):
        self.ini_simu()
        for i in range(1,int(24*60/self.ts)):
            self.step_simu(step_i=i)
    def plot(self,data_save_file):
        # 绘制原来的network load 和 speed以及仿真得到的network load和speed
        tmp_dict = {'ts':list(range(int(24*60/self.ts))),
                    'netload':self.n_list,
                    'speed':self.v_list}
        df_simu = pd.DataFrame(tmp_dict)
        fontsize = 10
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        fig, axes = plt.subplots()
        # fig.set_size_inches(10, 8)
        lns1 = axes.plot(df_simu['ts'], df_simu['speed'],'.-', color='black', label='average speed',linewidth=2, markersize=4.8)
        lns = lns1
        twin_axes = axes.twinx()
        lns2 = twin_axes.plot(df_simu['ts'], df_simu['netload'],'.-', label='network load', linewidth=2, markersize=4.8)
        lns += lns2
        axes.set_xlabel("Time slots", fontsize=fontsize)
        axes.set_ylabel("Average speed (km/h)", fontsize=fontsize)
        twin_axes.set_ylabel("Network load", fontsize=fontsize)
        plt.setp(axes.get_xticklabels(), fontsize=fontsize)
        plt.setp(axes.get_yticklabels(), fontsize=fontsize)
        plt.setp(twin_axes.get_yticklabels(), fontsize=fontsize)
        labs = [l.get_label() for l in lns]
        axes.legend(lns, labs, fontsize=fontsize, frameon=False,loc=0)
        plt.show()
        df_simu.to_csv(data_save_file,index=False,encoding='gbk')

if __name__ == "__main__":
    obj = simu(trip_dis_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\trip_distribution_0419.npy",
               v_n_rela_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\mfd拟合结果_newell.npy",
               free_speed=39.75,ts=15)
    obj.traffic_simu()
    obj.plot(data_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\限行区交通状态仿真.csv")