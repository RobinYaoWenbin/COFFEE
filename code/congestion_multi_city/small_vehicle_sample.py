import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import transbigdata as tbd
import geopandas as gpd
import networkx as nx
from tqdm import tqdm
import json
import gc
from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib.pyplot import MultipleLocator
import statsmodels.formula.api as smf
import copy
import time, datetime
import osmnx as ox
from sklearn.cluster import KMeans
import logging
import time
import utils
import seaborn as sns
import math
import geopandas as gpd
import fiona
from mpl_toolkits.mplot3d import Axes3D
from math import radians, cos, sin, asin, sqrt
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class get_small_vehicle:
    def __init__(self):
        pass
    @staticmethod
    def analyze_hangzhou(lpr_file):
        df = pd.read_csv(lpr_file)
        tmp_df = df.groupby(['vhc_plate_type_no'])['vhc_no'].nunique().reset_index().rename(columns={'vhc_no':'count'})
        small_veh_num = list(tmp_df[tmp_df['vhc_plate_type_no'] == 2]['count'])[0] + \
                        list(tmp_df[tmp_df['vhc_plate_type_no'] == 52]['count'])[0]
        total_num = sum(tmp_df['count'])
        print("小型汽车数量为{0}，机动车总数为{1},小型汽车占比为{2}。".format(small_veh_num,total_num,small_veh_num/total_num))

if __name__ == "__main__":
    get_small_vehicle.analyze_hangzhou(lpr_file="E:/study_e/HZMultiSourceData/LPRData_2104/HZ_LPRdata_425.csv")