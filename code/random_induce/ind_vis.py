import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib.pyplot import MultipleLocator
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

class visualization:
    def __init__(self):
        pass
    @staticmethod
    def ran_ind_pol1_vis(input_file_path,ts,save_file):
        file_name_list = os.listdir(input_file_path)
        tmp_netload = {}
        tmp_sam_list = []
        for i in range(len(file_name_list)):
            df = pd.read_csv(input_file_path+file_name_list[i] , encoding='gbk')
            if i == 0:
                netload_list_before = utils.get_ts_netload(df=df, ts=ts)
                tmp_netload['tol'] = netload_list_before
            df['tss'] = df['tss'] + df['delay']
            df['tso'] = df['tso'] + df['delay']
            netload_list_after = utils.get_ts_netload(df=df, ts=ts)
            tmp_netload[file_name_list[i][:-4][10:]] = netload_list_after
            tmp_sam_list.append( file_name_list[i][:-4][10:] )
        tmp_netload['x'] = list( range( int(24*60/ts) ) )
        df_load = pd.DataFrame(tmp_netload)
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        ax = plt.gca()
        plt.xlabel('Time slots')
        plt.ylabel('Network load')
        x_major_locator = MultipleLocator(5)
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(df_load['x'], df_load['tol'], '.-', color='black', linewidth=0.5, markersize=1.5,
                     label='original network load')
        for i in range(len(tmp_sam_list)):
            plt.plot(df_load['x'], df_load[tmp_sam_list[i]], '.-', linewidth=0.51, markersize=1.5,
                 label='network load under {0}% trips induced'.format(tmp_sam_list[i]))
        plt.legend(fontsize='xx-small',frameon=False)
        plt.show()
        df_load.to_csv(save_file,index=False,encoding='gbk')

if __name__ == "__main__":
    visualization.ran_ind_pol1_vis(input_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\adjust_diff_sample_15\\",
                                   ts=15,save_file="E:\\study_e\\analysis_of_IBTDM\\data\\random_induce\\policy_1\\adjust_diff_sample_15.csv")