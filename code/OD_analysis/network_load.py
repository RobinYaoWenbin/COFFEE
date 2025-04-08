import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
from matplotlib.pyplot import MultipleLocator
import copy
import time, datetime
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class netload:
    def __init__(self):
        pass
    @staticmethod
    def get_ts_load(ts,OD_file,is_plot,is_save_data,save_data_file):
        '''
        获个各个time slot的网络载荷,并绘图展示
        :return:
        '''
        def get_ts(x,ts):
            x = str(x)
            x_min = int(x[11:13])*60+int(x[14:16])+int(x[17:19])/60
            return int(x_min/ts)
        df = pd.read_csv(OD_file,encoding='gbk')
        travel_ts = []  # 存在出行的time slots
        df['ori_ts'] = df['cap_date_ori'].apply(get_ts , args=(ts,))
        df['des_ts'] = df['cap_date_des'].apply(get_ts, args=(ts,))
        for i in range(len(df)):
            if i % 100000 == 0:
                print("已完成{0}%".format(round(i/len(df)*100,2) ))
            tmp = list(range(df.loc[i,'ori_ts'] ,df.loc[i,'des_ts']+1 ))
            travel_ts.extend(tmp)
        # 统计list中各元素的数量
        ts_num = int(24*60/ts)
        netload = []
        for i in range(ts_num):
            netload.append(travel_ts.count(i))
        if is_plot:
            plt.rcParams['figure.dpi'] = 300  # 分辨率
            ax = plt.gca()
            plt.xlabel('Time slots')
            plt.ylabel('Network load')
            x_major_locator = MultipleLocator(5)
            ax.xaxis.set_major_locator(x_major_locator)
            plt.plot(range(0,ts_num), netload, '.-', color='black')
            plt.show()
        if is_save_data:
            df = pd.DataFrame({'timeslot':range(0,ts_num),
                                'netload':netload})
            df.to_csv(save_data_file , index=False,encoding='gbk')


if __name__ == "__main__":
    netload.get_ts_load(ts=15,OD_file='E:\\study_e\\analysis_of_IBTDM\\data\\ODFile\\OD_419.csv',
                        is_plot=True, is_save_data=True, save_data_file='E:\\study_e\\analysis_of_IBTDM\\data\\网络载荷随时间变化数据_0419.csv')