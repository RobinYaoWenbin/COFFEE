import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import transbigdata as tbd
import folium
import os
import re
import sys
from matplotlib.pyplot import MultipleLocator
import random
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
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

class get_cameras:
    def __init__(self):
        pass
    @staticmethod
    def start(research_boundry_file,dev_file,is_plot,html_save_path=None,is_save_dev_data=True,dev_data_save_path=None):
        research_gdf = gpd.read_file(research_boundry_file)
        research_gdf = research_gdf.set_crs(4326, allow_override=True)
        dev_df = pd.read_csv(dev_file)
        dev_df = tbd.clean_outofshape(dev_df, shape=research_gdf, col=['Lng84', 'Lat84'], accuracy=1)
        if is_plot:
            map = folium.Map(
                location=[list(research_gdf['geometry'])[0].centroid.y, list(research_gdf['geometry'])[0].centroid.x],
                tiles='cartodbpositron', zoom_start=9)
            # 限行范围
            line_coords = []
            for coor in list(research_gdf['geometry'][0].exterior.coords):
                tmp = [coor[1], coor[0]]
                line_coords.append(tmp)
            folium.PolyLine(line_coords,
                            radius=50,
                            color='blue',
                            fill_color='blue',
                            fill=False,
                            fill_opacity=0,
                            opacity=1).add_to(map)
            # 限行区内的电警卡口分布
            for i in range(len(dev_df)):
                folium.Circle(
                    location=[list(dev_df['Lat84'])[i], list(dev_df['Lng84'])[i]],
                    radius=10,
                    color='red',
                    fill_color='red',
                    fill=True,
                    fill_opacity=1,
                    popup=list(dev_df['id'])[i] ,
                ).add_to(map)
            map.save(html_save_path)
        if is_save_dev_data:
            dev_df[['id', 'Lng84', 'Lat84']].to_csv(dev_data_save_path, index=False, encoding='gbk')
        return dev_df[['id', 'Lng84', 'Lat84']]
    @staticmethod
    def vis(research_boundry_file,dev_file,html_save_path):
        research_gdf = gpd.read_file(research_boundry_file)
        research_gdf = research_gdf.set_crs(4326, allow_override=True)
        dev_df = pd.read_csv(dev_file,encoding='gbk')
        map = folium.Map(
            location=[list(research_gdf['geometry'])[0].centroid.y, list(research_gdf['geometry'])[0].centroid.x],
            tiles='cartodbpositron', zoom_start=9)
        # 限行范围
        line_coords = []
        for coor in list(research_gdf['geometry'][0].exterior.coords):
            tmp = [coor[1], coor[0]]
            line_coords.append(tmp)
        folium.PolyLine(line_coords,
                        radius=50,
                        color='blue',
                        fill_color='blue',
                        fill=False,
                        fill_opacity=0,
                        opacity=1).add_to(map)
        # 限行区内的电警卡口分布
        for i in range(len(dev_df)):
            folium.Circle(
                location=[list(dev_df['Lat84'])[i], list(dev_df['Lng84'])[i]],
                radius=10,
                color='red',
                fill_color='red',
                fill=True,
                fill_opacity=1,
                popup=list(dev_df['id'])[i],
            ).add_to(map)
        map.save(html_save_path)

if __name__ == "__main__":
    # get_cameras.start(research_boundry_file='E:\\study_e\\HZMultiSourceData\\限行区域wgs84\\限行区域wgs84.shp',
    #                 dev_file='E:\\study_e\\HZMultiSourceData\\原始点位清洗wgs84.csv',
    #                 is_plot=True,html_save_path='E:\\study_e\\analysis_of_IBTDM\\figures\\严格清洗版本电警卡口分布图.html',
    #                 is_save_dev_data=True,
    #                 dev_data_save_path='E:\\study_e\\analysis_of_IBTDM\\data\\restriction_pol\\严格清洗版限行区内电警卡口设备.csv')

    get_cameras.vis(research_boundry_file="E:\\study_e\\HZMultiSourceData\\限行区域wgs84\\限行区域wgs84.shp",
                    dev_file="E:\\study_e\\analysis_of_IBTDM\\data\\restriction_pol\\严格清洗版限行区内电警卡口设备.csv",
                    html_save_path="E:\\study_e\\analysis_of_IBTDM\\figures\\严格清洗版本电警卡口分布图.html")