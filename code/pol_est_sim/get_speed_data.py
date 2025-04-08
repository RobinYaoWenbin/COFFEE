import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
import copy
import time, datetime
import geopandas as gpd
import transbigdata as tbd
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class prepare_data:
    def __init__(self):
        pass
    @staticmethod
    def get_speed_data(speed_file,research_area_file,ts,speed_data_save,taxi_data_save):
        # 读取限行区域
        research_gdf = gpd.read_file(filename=research_area_file)
        research_gdf = research_gdf.set_crs(4326, allow_override=True)
        f = open(speed_file, encoding='utf-8')
        reader = pd.read_csv(f, sep=',', iterator=True)
        loop = True
        chunkSize = 8000000
        chunks = []
        iteration = 0
        while loop:
            try:
                print("正在进行第{0}次循环".format(iteration))
                chunk = reader.get_chunk(chunkSize)
                print("清洗前出租车GPS数据情况:")
                tbd.data_summary(data=chunk, col=['plate', 'time'], show_sample_duration=True)
                chunk = tbd.clean_outofshape(data=chunk, shape=research_gdf, col=['lng', 'lat'], accuracy=400)
                chunk = chunk[chunk['occupancy'] != 0]
                chunk = chunk[(chunk['speed']>=0.1) & (chunk['speed']<=120)]
                print("清洗后出租车GPS数据情况:")
                tbd.data_summary(data=chunk, col=['plate', 'time'], show_sample_duration=True)
                chunks.append(chunk)
                iteration += 1
            except StopIteration:
                loop = False
                print("Iteration is stopped.")
        df = pd.concat(chunks, ignore_index=True)
        # 计算区域平均速度
        df['time_str'] = df['time'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        df['sec'] = df['time_str'].apply(utils.t2s_fulltime)
        df['ts'] = df['sec'].apply(utils.get_timeslots, args=(ts,))
        df_speed = df.groupby(['ts'])[['speed']].median().reset_index()
        df.to_csv(taxi_data_save,index=False,encoding='gbk')
        df_speed.to_csv(speed_data_save,index=False,encoding='gbk')

    @staticmethod
    def get_speed_auto(speed_file_path,research_area_file,speed_save_file_path,taxi_save_file_path,ts):
        file_name_list = os.listdir(speed_file_path)
        for i in range(len(file_name_list)):
            speed_data_save = speed_save_file_path + 'speed_' + file_name_list[i][7:]
            taxi_data_save = taxi_save_file_path + 'hz_gps_after_process_' + file_name_list[i][7:]
            prepare_data.get_speed_data(speed_file=speed_file_path+file_name_list[i],
                                        research_area_file=research_area_file,ts=ts,
                                        speed_data_save=speed_data_save,taxi_data_save=taxi_data_save)

if __name__ == "__main__":
    prepare_data.get_speed_data(speed_file="E:\\study_e\\HZMultiSourceData\\GPS_data\\hz_gps_0419.csv",
                   research_area_file="E:\\study_e\\HZMultiSourceData\\限行区域wgs84\\限行区域wgs84.shp",
                   ts=15,
                   speed_data_save="E:\\study_e\\analysis_of_IBTDM\\data\\speedfile\\speed_0419.csv",
                   taxi_data_save="E:\\study_e\\HZMultiSourceData\\GPSData_after_process\\hz_gps_after_process_0419.csv")
    # prepare_data.get_speed_auto(speed_file_path="E:\\study_e\\HZMultiSourceData\\GPS_data\\",
    #                             research_area_file="E:\\study_e\\HZMultiSourceData\\限行区域wgs84\\限行区域wgs84.shp",
    #                             speed_save_file_path="E:\\study_e\\analysis_of_IBTDM\\data\\speedfile\\",
    #                             taxi_save_file_path="E:\\study_e\\HZMultiSourceData\\GPSData_after_process\\",
    #                             ts=15)