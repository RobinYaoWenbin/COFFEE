import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.pyplot import MultipleLocator
sys.path.append("../lib/")
from tqdm import tqdm
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import copy
import time, datetime
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class spilt:
    def __init__(self):
        pass
    @staticmethod
    def get_bins_width(M_series):
        bins_width = 3.5 * np.std(M_series, ddof=1) / (len(M_series) ** (1 / 3))
        if bins_width<1:
            return 1
        return bins_width
    @staticmethod
    def spilt_sample(df , bins_width , N):
        if len(df) == 0:
            return {}
        spilt_df_list = {}
        bin_num = int((max(df['M']) - min(df['M'])) / bins_width) + 1
        df['label'] = pd.cut(df['M'],bin_num,labels=range(bin_num))
        label_set = list(set(df['label']))
        for i in range(len(label_set)):
            tmp_label = label_set[i]
            tmp_df = df[df['label']==tmp_label]
            shuffled = tmp_df.sample(frac=1)
            shuffled.drop(columns='label',inplace=True)
            results = np.array_split(shuffled, N)
            j=0
            for part in tqdm(results):
                tmp = spilt_df_list.get(j,[])
                if len(tmp) == 0:
                    spilt_df_list[j] = part
                else:
                    # spilt_df_list[j] = tmp.append(part,ignore_index=True)
                    spilt_df_list[j] = pd.concat([tmp, part], ignore_index=True) 
                j+=1
        return spilt_df_list

    def read_data(self,data_file,ts):
        self.ts = ts
        self.df_trips = pd.read_csv(data_file,encoding='gbk')
        self.df_trips['M'] = self.df_trips[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(self.ts,), axis=1)
        self.df_trips['tss'] = self.df_trips['ori_sec'].apply(utils.get_timeslots, args=(self.ts,))
        self.df_trips['tso'] = self.df_trips['des_sec'].apply(utils.get_timeslots, args=(self.ts,))

    def start_spilt(self,N,is_save,save_file_path,save_file_prefix):
        spilt_files = {}
        for i in range(int(24*60/self.ts)):
            print("正在处理time slots {0}".format(i))
            tmp_df_trips = self.df_trips[self.df_trips['tss'] == i]
            if len(tmp_df_trips) == 0:
                continue
            bins_width = self.get_bins_width(tmp_df_trips['M'])
            print("bin width is {0}".format(bins_width))
            tmp_spilt_df_dict = self.spilt_sample(df=tmp_df_trips, bins_width=bins_width, N=N)
            for j in range(N):
                tmp = spilt_files.get(j,[])
                if len(tmp) == 0:
                    spilt_files[j] = tmp_spilt_df_dict[j]
                else:
                    # spilt_files[j] = tmp.append(tmp_spilt_df_dict[j],ignore_index=True)
                    spilt_files[j] = pd.concat([tmp, tmp_spilt_df_dict[j]], ignore_index=True) 
        self.spilt_files = spilt_files
        if is_save:
            for key in self.spilt_files.keys():
                tmp = self.spilt_files[key]
                tmp.to_csv(save_file_path+save_file_prefix+str(key)+'.csv' , index=False,encoding='gbk')

    def validation(self,file_path,original_file,ts,save_file,is_plot):
        file_name_list = os.listdir(file_path)
        spilt_files = {}
        tot_len = 0
        veh_num = set()
        for i in range(len(file_name_list)):
            spilt_files[i] = pd.read_csv(file_path+file_name_list[i],encoding='gbk')
            tot_len = tot_len + len(spilt_files[i])
            veh_num = veh_num | set(spilt_files[i]['vhc_no'])
        df_trips = pd.read_csv(original_file,encoding='gbk')
        df_trips['M'] = df_trips[['ori_sec', 'des_sec']].apply(utils.get_ts_num, args=(ts,), axis=1)
        df_trips['tss'] = df_trips['ori_sec'].apply(utils.get_timeslots, args=(ts,))
        df_trips['tso'] = df_trips['des_sec'].apply(utils.get_timeslots, args=(ts,))
        print("样本划分后各个子样本的出行总和为{0}，车辆数总和为{1}。划分前出行总和为{2}，车辆数总和为{3}.".format(
            tot_len,len(veh_num),len(df_trips),len(set(df_trips['vhc_no']))))
        # 绘制出各个数据集的网络载荷
        tol_netload = utils.get_ts_netload(df=df_trips,ts=ts)
        sample_netload = {}
        for i in range(len(file_name_list)):
            tmp_df = spilt_files[i]
            sample_netload[i] = utils.get_ts_netload(df=tmp_df,ts=ts)
        sample_netload['total'] = tol_netload
        df_load = pd.DataFrame(sample_netload)
        df_load['x']=list(range(int(24*60/ts)))
        df_load.to_csv(save_file,index=False,encoding='gbk')
        if is_plot:
            fontsize = 20
            plt.rcParams['xtick.direction'] = 'in'
            plt.rcParams['ytick.direction'] = 'in'
            fig, axes = plt.subplots()
            fig.set_size_inches(10, 8)
            lns1 = axes.plot(df_load['x'], df_load['total'], color='black', label='Total network load')
            lns = lns1
            twin_axes = axes.twinx()
            for i in range(len(file_name_list)):
                lns2 = twin_axes.plot(df_load['x'], df_load[i], label='subsample '+str(i))
                lns += lns2
            axes.set_xlabel("Time slots", fontsize=fontsize)
            axes.set_ylabel("Network load (total sample)",  fontsize=fontsize)
            twin_axes.set_ylabel("Network load (subsample)",  fontsize=fontsize)
            plt.setp(axes.get_xticklabels(), fontsize=fontsize)
            plt.setp(axes.get_yticklabels(), fontsize=fontsize)
            plt.setp(twin_axes.get_yticklabels(), fontsize=fontsize)
            labs = [l.get_label() for l in lns]
            num1 = 1.05; num2=1;num3 = 3; num4 = 0
            axes.legend(lns, labs,  fontsize=fontsize-8,frameon=False,ncol=3,
                        loc=0)
            plt.show()


if __name__ == "__main__":
    # ## 早高峰
    # obj = spilt()
    # obj.read_data(data_file = "E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_morning_419.csv",ts=15)
    # obj.start_spilt(N=15,is_save=True,save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_morning\\",
    #                 save_file_prefix="optim_trips_morning_419_")
    # obj.validation(file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_morning\\",
    #                original_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_morning_419.csv",ts=15,
    #                save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\各个样本数据的网络载荷分布.csv",is_plot=True)

    ## 晚高峰
    # obj = spilt()
    # obj.read_data(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_evening_419.csv", ts=15)
    # obj.start_spilt(N=15, is_save=True,
    #                 save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_evening\\",
    #                 save_file_prefix="optim_trips_evening_419_")
    # obj.validation(file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_evening\\",
    #                original_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_evening_419.csv", ts=15,
    #                save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\各个样本数据的网络载荷分布（晚高峰）.csv", is_plot=True)

    ## 全天
    # obj = spilt()
    # obj.read_data(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_allday_419.csv", ts=15)
    # obj.start_spilt(N=36, is_save=True,
    #                 save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_allday\\",
    #                 save_file_prefix="optim_trips_allday_419_")
    # obj.validation(file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_allday\\",
    #                original_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_allday_419.csv", ts=15,
    #                save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\各个样本数据的网络载荷分布（全天）.csv", is_plot=True)

    ## 4月25日
    # 对4月25日也进行相同的操作
    obj = spilt()
    obj.read_data(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_allday_425.csv", ts=15)
    obj.start_spilt(N=36, is_save=True,
                    save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_allday_0425\\",
                    save_file_prefix="optim_trips_allday_425_")
    obj.validation(file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_allday_0425\\",
                   original_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_allday_425.csv", ts=15,
                   save_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\各个样本数据的网络载荷分布（全天）_0425.csv",
                   is_plot=True)