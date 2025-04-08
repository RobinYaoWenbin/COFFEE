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
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class merge:
    def __init__(self):
        pass
    @staticmethod
    def start(subfile_path,save_data):
        tol_df = pd.DataFrame([])
        file_name_list = os.listdir(subfile_path)
        for i in range(len(file_name_list)):
            tmp_df = pd.read_csv(subfile_path+file_name_list[i] , encoding='gbk')
            tol_df = tol_df.append(tmp_df,ignore_index=True)
        tol_df.to_csv(save_data,index=False,encoding='gbk')

if __name__ == "__main__":
    merge.start(subfile_path = "E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\trip_solution\\",
                save_data = "E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\merge_solution_optim_trips_morning_419.csv")