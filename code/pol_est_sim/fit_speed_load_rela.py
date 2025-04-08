import pandas as pd
import numpy as np
import geopandas as gpd
from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
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

class fit:
    def __init__(self):
        pass
    @staticmethod
    def start(data_file,fit_result_save_file,func,bounds):
        df = pd.read_csv(data_file,encoding='gbk')
        # 增加早晚高峰数据点的权重
        peak_df = df[((df['ts']>=28)&(df['ts']<=35)) | ((df['ts']>=64)&(df['ts']<=75))]
        for i in range(6):
            df = df.append(peak_df,ignore_index=True)
        x = np.array(df['netload'],dtype='float64')
        y = np.array(df['speed'],dtype="float64")
        popt1 , pov1 = curve_fit(func , x,y,method='trf',maxfev=10000,bounds=bounds)
        print("拟合得到的系数依次为:",popt1)
        np.save(fit_result_save_file, np.array(popt1))
        return popt1
    @staticmethod
    def plot_result(data_file,popt1,func):
        df = pd.read_csv(data_file, encoding='gbk')
        df.sort_values(by=['netload'],inplace=True)
        x = np.array(df['netload'], dtype='float64')
        y = np.array(df['speed'], dtype="float64")
        yval = func(x,popt1[0],popt1[1],popt1[2])
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        plt.scatter(x,y,s=1,label="value distribution")
        plt.plot(x,yval,color='black',label="fitted curve")
        plt.xlabel("Network load")
        plt.ylabel("Average speed (km/h)")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # popt1 = fit.start(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv",
    #                   fit_result_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\mfd拟合结果_newell.npy",
    #                   func=utils.newell_model,bounds=([20,0,10000],[80,100000000,1000000]))
    # # print(newell_model(np.array([0],dtype='float64'), popt1[0], popt1[1], popt1[2]))
    # fit.plot_result(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv",popt1=popt1,func=utils.newell_model)
    popt1 = fit.start(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv",
                      fit_result_save_file="E:\\study_e\\analysis_of_IBTDM\\data\\simu_pol_eva_data\\mfd拟合结果_exp.npy",
                      func=utils.exp_func,bounds=([0,0,0],[80,np.inf,80]))
    # print(newell_model(np.array([0],dtype='float64'), popt1[0], popt1[1], popt1[2]))
    fit.plot_result(data_file="E:\\study_e\\analysis_of_IBTDM\\data\\speed_load_data\\speed_load_data_0419.csv",
                    popt1=popt1, func=utils.exp_func)