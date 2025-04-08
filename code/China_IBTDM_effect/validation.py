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
import seaborn as sns
import statsmodels.formula.api as smf
import copy
import time, datetime
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

class validation:
    def __init__(self):
        pass
    @staticmethod
    def cal_corr(getui_cv,lpr_cv):
        A1 = pd.Series(getui_cv)
        B1 = pd.Series(lpr_cv)
        corr_pearson = B1.corr(A1, method= 'pearson')
        corr_spearman = B1.corr(A1, method='spearman')
        print("pearson correlation{0}，spearman correlation{1}.".format(corr_pearson,corr_spearman))
    @staticmethod
    def plot(file):
        df = pd.read_excel(file)
        corr_pearson = df['Getui'].corr(df['LPR'], method='pearson')
        print(corr_pearson)
        plt.figure(figsize=(8, 6))  # 指定绘图对象宽度和高度
        ax = plt.subplot(1, 1, 1)
        results = smf.ols('LPR ~ Getui', data=df).fit()
        print(results.summary())
        sns.regplot(x='Getui', y='LPR', data=df, ax=ax,
                    scatter_kws={'marker': '.', 's': 10, 'alpha': 0.3},
                    line_kws={'color': 'g'})
        plt.xlabel('$c_v$ of Getui')
        plt.ylabel('$c_v$ of LPR')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # # 按照周几来平均
    # validation.cal_corr(getui_cv=[0.532473182,0.615067574,0.635407983,0.646766354,0.66283758,0.678948891,0.689796586],
    #                     lpr_cv=[0.585,0.594,0.724,0.563,0.664,0.682,0.677])
    # # 按照所有工作日来平均
    # validation.cal_corr(getui_cv=[0.547882913,0.62423689,0.635323136,0.637710094,0.651277045,0.676632198,0.689343841],
    #                     lpr_cv=[0.585,0.594,0.724,0.563,0.664,0.682,0.677])

    validation.plot(file="../../data/China_IBTDM_effect/数据质量分析.xlsx")