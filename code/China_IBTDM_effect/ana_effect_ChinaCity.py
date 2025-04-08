import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import sys
from matplotlib.pyplot import MultipleLocator
import random
# from pyecharts import Map
# from pyecharts import Geo
from pyecharts.charts import Map
from pyecharts.charts import Geo
from pyecharts import options as opts
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
from matplotlib import ticker
import seaborn as sns
import copy
import time, datetime
import logging
import time
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def relation_congestioneffect_cv(x):
    y = 0.84*(0.9191*x+0.0630)-0.26
    return y

def relation_enveffect_cv(x):
    y = 0.74 * (0.9191*x+0.0630) - 0.26
    return y

def relation_congestioneffect_cv_15(x):
    y = 0.84*(0.8378*x+0.1059)-0.26
    return y

def relation_enveffect_cv_15(x):
    y = 0.74 * (0.8378*x+0.1059) - 0.26
    return y

class ana_effect:
    def __init__(self):
        pass
    @staticmethod
    def get_effect(getui_cv_file,sheetname,rela1,rela2,data_save_file):
        df = pd.read_excel(getui_cv_file,sheet_name=sheetname)
        df.rename(columns={'60分钟切片-按工作日平均':'cv'},inplace=True)
        df['con_y'] = rela1(df['cv'])
        df['env_y'] = rela2(df['cv'])
        df.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def get_effect_15min(getui_cv_file,sheetname,rela1,rela2,data_save_file):
        df = pd.read_excel(getui_cv_file,sheet_name=sheetname)
        df.rename(columns={'15分钟切片-按工作日平均':'cv'},inplace=True)
        df['con_y'] = rela1(df['cv'])
        df['env_y'] = rela2(df['cv'])
        df.to_csv(data_save_file,index=False,encoding='gbk')
    @staticmethod
    def plot_effect_congestion(effect_file,var_name,save_file):
        df = pd.read_csv(effect_file,encoding='gbk')
        data = list(zip(df['城市名'],df[var_name]))
        geo = (Geo()
               .add_schema(maptype="china", itemstyle_opts=opts.ItemStyleOpts(color="#404a59"))
               .set_global_opts(
                    title_opts=opts.TitleOpts(
                    title="The effect of alleviating traffic congestion in major cities in China",
                    title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
                    pos_left="center"
        ),
            visualmap_opts=opts.VisualMapOpts(
                is_piecewise=True,
                pieces=[
                    {"min": 0.19, "max": 0.23, "label": "19%-23%"},
                    {"min": 0.23, "max": 0.27, "label": "23%-27%"},
                    {"min": 0.27, "max": 0.31, "label": "27%-31%"},
                    {"min": 0.31, "max": 0.35, "label": "31%-35%"},
                    {"min": 0.35, "max": 0.39, "label": "35%-39%"},
                ],
                textstyle_opts=opts.TextStyleOpts(color="#fff"),
            )
        )
        )
        # 添加坐标和数据
        geo.add_coordinate('杭州市萧山区', 120.26, 30.18)
        geo.add_coordinate('青岛市黄岛区', 120.20, 35.96)
        geo.add_coordinate('黔西南布依族苗族自治州', 104.91, 25.09)
        geo.add("", data, symbol_size=15)

        # 渲染图表
        geo.render(save_file)

    @staticmethod
    def plot_effect_env(effect_file,var_name,save_file):
        df = pd.read_csv(effect_file,encoding='gbk')
        data = list(zip(df['城市名'],df[var_name]))
        geo = (Geo()
        .add_schema(maptype="china", itemstyle_opts=opts.ItemStyleOpts(color="#404a59"))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="The effect of alleviating traffic congestion in major cities in China",
                title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
                pos_left="center"
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_piecewise=True,
                pieces=[
                    {"min": 0.14, "max": 0.18, "label": "14%-18%"},
                    {"min": 0.18, "max": 0.22, "label": "18%-22%"},
                    {"min": 0.22, "max": 0.26, "label": "22%-26%"},
                    {"min": 0.26, "max": 0.30, "label": "26%-30%"},
                ],
                textstyle_opts=opts.TextStyleOpts(color="#fff"),
            )
        )
        )
        # 添加坐标和数据
        geo.add_coordinate('杭州市萧山区', 120.26, 30.18)
        geo.add_coordinate('青岛市黄岛区', 120.20, 35.96)
        geo.add_coordinate('黔西南布依族苗族自治州', 104.91, 25.09)
        geo.add("", data, symbol_size=15)
        geo.render(save_file)


if __name__ == "__main__":
    # ana_effect.get_effect(getui_cv_file="../../data/China_IBTDM_effect/Getui/筛选城市及对应cv.xls",sheetname='42个cv值',
    #                       rela1=relation_congestioneffect_cv,rela2=relation_enveffect_cv,
    #                       data_save_file="../../data/China_IBTDM_effect/China_city_effect.csv")

    # ana_effect.plot_effect_congestion(effect_file="../../data/China_IBTDM_effect/China_city_effect.csv",var_name='con_y',
    #                        save_file="../../data/China_IBTDM_effect/中国主要城市缓堵效果.html")

    ana_effect.plot_effect_congestion(effect_file="../../data/China_IBTDM_effect/15minChina_city_effect.csv",
                                      var_name='con_y',
                                      save_file="../../data/China_IBTDM_effect/15minRelievecongestioneffect.html")




