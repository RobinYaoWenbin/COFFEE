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

class distribution_plot:
    def __init__(self):
        pass
    @staticmethod
    def commuting_veh_dis(input_dis_file):
        df = pd.read_excel(input_dis_file)
        df['adjust'] = df['adjust'] - 1
        df['adjust'] = df[['adjust']].applymap(lambda x:str(x))
        plt.rcParams['figure.dpi'] = 300
        plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
        ax = plt.subplot(1, 1, 1)
        ax.plot(df['adjust'] , df['m_ad_r'] , label='$D_{ma}$')
        ax.plot(df['adjust'], df['m_de_r'],label='$D_{md}$')
        ax.plot(df['adjust'], df['e_ad_r'], label='$D_{ea}$')
        ax.plot(df['adjust'], df['e_de_r'], label='$D_{ed}$')
        ax.plot(df['adjust'], df['off_r'], label='$D_{o}$')
        plt.xlabel('Degree of adjustment')
        plt.ylabel('Probability')
        plt.legend()
        plt.show()
    @staticmethod
    def veh_for_business_family_dis(input_dis_file):
        df = pd.read_excel(input_dis_file)
        df['adjust'] = df['adjust'] - 1
        df['adjust'] = df[['adjust']].applymap(lambda x: str(x))
        plt.rcParams['figure.dpi'] = 300
        plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
        ax = plt.subplot(1, 1, 1)
        ax.plot(df['adjust'], df['ratio'])
        plt.xlabel('Degree of adjustment')
        plt.ylabel('Probability')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    distribution_plot.commuting_veh_dis(input_dis_file="../../data/survey_data/company_survey_data/出行规律性强通勤者出发时间调整情况.xlsx")


