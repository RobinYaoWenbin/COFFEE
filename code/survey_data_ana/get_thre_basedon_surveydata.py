import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def get_com_regu_thre1(ser,adj_df):
    if ser['period'] == 0:
        probabilities = list(adj_df['off_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return -(result - 1)
    elif ser['period'] == 1:
        probabilities = list(adj_df['m_ad_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return -(result - 1)
    else:
        probabilities = list(adj_df['e_ad_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return -(result - 1)

def get_com_regu_thre2(ser,adj_df):
    if ser['period'] == 0:
        probabilities = list(adj_df['off_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return (result - 1)
    elif ser['period'] == 1:
        probabilities = list(adj_df['m_de_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return (result - 1)
    else:
        probabilities = list(adj_df['e_de_r'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return (result - 1)

def get_businessveh_thre1(ser,adj_df):
    if len(adj_df) == 0:
        return 0
    else:
        probabilities = list(adj_df['ratio'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return -(result - 1)

def get_businessveh_thre2(ser,adj_df):
    if len(adj_df) == 0:
        return 0
    else:
        probabilities = list(adj_df['ratio'])
        elements = list(adj_df['adjust'])
        result = random.choices(elements, probabilities)[0]
        return (result - 1)

def get_familyveh_thre1(ser,adj_df):
    probabilities = list(adj_df['ratio'])
    elements = list(adj_df['adjust'])
    result = random.choices(elements, probabilities)[0]
    return -(result - 1)

def get_familyveh_thre2(ser,adj_df):
    probabilities = list(adj_df['ratio'])
    elements = list(adj_df['adjust'])
    result = random.choices(elements, probabilities)[0]
    return (result - 1)

class get_thre:
    def __init__(self):
        pass
    @staticmethod
    def get(portrait_file,tra_regu_file,com_regu1_file,com_regu2_file,com_regu3_file,familyveh_file,businessveh_file,data_save_file):
        df_por = pd.read_csv(portrait_file, encoding='gbk')
        df_regu = pd.read_csv(tra_regu_file, encoding='gbk')
        df = pd.merge(df_por, df_regu, how='left', on='vhc_no')
        df_adj_thre = pd.DataFrame([])
        df_list = []
        df_list.append(df[((df['label'] == 0) | (df['label'] == 2)) & (df['regu_label'] == 2)])  # 规律性强通勤出行者
        df_list.append(df[((df['label'] == 0) | (df['label'] == 2)) & (df['regu_label'] == 0)])  # 规律性中通勤出行者
        df_list.append(df[((df['label'] == 0) | (df['label'] == 2)) & (
        (df['regu_label'] != 2) & (df['regu_label'] != 0))])  # 规律性弱通勤出行者
        df_list.append(df[df['label'] == 3])  # 网约出租车辆
        df_list.append(df[df['label'] == 5])  # 临时办事车辆
        df_list.append(df[(df['label'] != 3) & (df['label'] != 0) & (df['label'] != 2) & (df['label'] != 5)])  # 家庭不常用车辆
        print("total number of vehicles {0},commuting vehicles with strong regularity{1},commuting vehicles with medium regularity {2},commuting vehicles with weak regularity{3},taxis {4},local vehicles{5},non local vehicles{6}".format(
            len(df), len(df_list[0]), len(df_list[1]), len(df_list[2]), len(df_list[3]), len(df_list[4]),
            len(df_list[5])
        ))
        # 出行规律性强通勤出行者
        tmp_adj_dis = pd.read_excel(com_regu1_file)
        tmp_df = df_list[0][['vhc_no','label','regu_label']]
        tmp_period_df = pd.DataFrame({'period': [0, 1, 2]})
        tmp_df = pd.merge(tmp_df, tmp_period_df, how='cross')
        tmp_df['thre1'] = tmp_df.apply(get_com_regu_thre1 , args=(tmp_adj_dis,) , axis=1)
        tmp_df['thre2'] = tmp_df.apply(get_com_regu_thre2, args=(tmp_adj_dis,), axis=1)
        df_list[0] = tmp_df
        # 出行规律性中通勤出行者
        tmp_adj_dis = pd.read_excel(com_regu2_file)
        tmp_df = df_list[1][['vhc_no', 'label', 'regu_label']]
        tmp_period_df = pd.DataFrame({'period': [0, 1, 2]})
        tmp_df = pd.merge(tmp_df, tmp_period_df, how='cross')
        tmp_df['thre1'] = tmp_df.apply(get_com_regu_thre1, args=(tmp_adj_dis,), axis=1)
        tmp_df['thre2'] = tmp_df.apply(get_com_regu_thre2, args=(tmp_adj_dis,), axis=1)
        df_list[1] = tmp_df
        # 出行规律性弱通勤出行者
        tmp_adj_dis = pd.read_excel(com_regu3_file)
        tmp_df = df_list[2][['vhc_no', 'label', 'regu_label']]
        tmp_period_df = pd.DataFrame({'period': [0, 1, 2]})
        tmp_df = pd.merge(tmp_df, tmp_period_df, how='cross')
        tmp_df['thre1'] = tmp_df.apply(get_com_regu_thre1, args=(tmp_adj_dis,), axis=1)
        tmp_df['thre2'] = tmp_df.apply(get_com_regu_thre2, args=(tmp_adj_dis,), axis=1)
        df_list[2] = tmp_df
        # 网约出租车辆
        tmp_df = df_list[3][['vhc_no', 'label', 'regu_label']]
        tmp_df['period'] = 0
        tmp_df['thre1'] = 0
        tmp_df['thre2'] =0
        df_list[3] = tmp_df
        # 临时办事车辆
        tmp_adj_dis = pd.read_excel(businessveh_file)
        tmp_df = df_list[4][['vhc_no', 'label', 'regu_label']]
        tmp_df['period'] = 0
        tmp_df['thre1'] = tmp_df.apply(get_businessveh_thre1, args=(tmp_adj_dis,), axis=1)
        tmp_df['thre2'] = tmp_df.apply(get_businessveh_thre2, args=(tmp_adj_dis,), axis=1)
        df_list[4] = tmp_df
        # 家庭不常用车辆
        tmp_adj_dis = pd.read_excel(familyveh_file)
        tmp_df = df_list[5][['vhc_no', 'label', 'regu_label']]
        tmp_df['period'] = 0
        tmp_df['thre1'] = tmp_df.apply(get_familyveh_thre1, args=(tmp_adj_dis,), axis=1)
        tmp_df['thre2'] = tmp_df.apply(get_familyveh_thre2, args=(tmp_adj_dis,), axis=1)
        df_list[5] = tmp_df
        # 各类车辆合并
        for i in range(6):
            df_adj_thre = df_adj_thre.append(df_list[i] , ignore_index=True)
        print("total number of threshold table{0}".format(len(df_adj_thre)))
        df_adj_thre.to_csv(data_save_file , index=False,encoding='gbk')

if __name__ == "__main__":
    get_thre.get(portrait_file="../../data/veh_portrait/veh_all_sam_portrait.csv",
                tra_regu_file="../../data/travel_regu_data/veh_regu_cluster.csv",
                com_regu1_file="../../data/survey_data/own_survey_data/出行规律性强通勤者出发时间调整情况.xlsx",
                 com_regu2_file="../../data/survey_data/own_survey_data/出行规律性中等通勤者出发时间调整情况.xlsx",
                 com_regu3_file="../../data/survey_data/own_survey_data/出行规律性弱通勤者出发时间调整情况.xlsx",
                 familyveh_file="../../data/survey_data/own_survey_data/家庭不常用车辆出发时间调整情况.xlsx",
                 businessveh_file="../../data/survey_data/own_survey_data/办事车辆出发时间调整情况.xlsx",
                 data_save_file="../../data/survey_data/adj_thre_data.csv")








