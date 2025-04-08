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

class survey_data:
    def __init__(self):
        pass
    @staticmethod
    def data_preprocess(data_file,strong_com_beh_file,median_com_beh_file,weak_com_beh_file,family_veh_beh_file,
                        business_veh_beh_file):
        df = pd.read_excel(data_file,sheet_name="数字版")
        print("survey data rows: {0}.".format(len(df)))
        # 错误数据滤除
        df = df[~ ( ((df['S13']==2)&(df['S11']!=1))  |
                 ((df['S13'] == 2) & ((df['S17'] != 1) & (df['S17'] != 2))) |
                 (df['S4']==1) | (df['S9']==1) | (df['S10']==2) )
                ]
        print("After filtering out the erroneous data, the remaining questionnaire data consists of {0}".format( len(df) ))
        # 筛选出需要的数据
        df = df[df['S10'] == 1]
        print("The total number of questionnaires using private cars for travel:{0}".format(len(df)))
        # 出行规律性强的通勤出行者
        tmp = df[(df['S11'] == 1) &
                 (df['S18'] == 1)&
                 ((df['S19'] == 1)|
                  (df['S19']==2) )]
        print("Commuter travelers with strong regularity in travel:{0}".format(len(tmp)))
        tmp_accept = tmp
        tmp_ac_morn_ad = tmp_accept.groupby(['A3'])['ID'].count().reset_index().rename(columns={'A3':'adjust','ID': 'm_ad_f'})
        tmp_sum = sum(tmp_ac_morn_ad['m_ad_f'])
        tmp_ac_morn_ad['m_ad_r'] = tmp_ac_morn_ad['m_ad_f'] / tmp_sum
        tmp_ac_morn_delay = tmp_accept.groupby(['A4'])['ID'].count().reset_index().rename(columns={'A4':'adjust','ID': 'm_de_f'})
        tmp_sum = sum(tmp_ac_morn_delay['m_de_f'])
        tmp_ac_morn_delay['m_de_r'] = tmp_ac_morn_delay['m_de_f'] / tmp_sum
        tmp_ac_even_ad = tmp_accept.groupby(['A5'])['ID'].count().reset_index().rename(columns={'A5':'adjust','ID': 'e_ad_f'})
        tmp_sum = sum(tmp_ac_even_ad['e_ad_f'])
        tmp_ac_even_ad['e_ad_r'] = tmp_ac_even_ad['e_ad_f'] / tmp_sum
        tmp_ac_even_delay = tmp_accept.groupby(['A6'])['ID'].count().reset_index().rename(columns={'A6':'adjust','ID': 'e_de_f'})
        tmp_sum = sum(tmp_ac_even_delay['e_de_f'])
        tmp_ac_even_delay['e_de_r'] = tmp_ac_even_delay['e_de_f'] / tmp_sum
        tmp_ac_off_peak = tmp_accept.groupby(['A7'])['ID'].count().reset_index().rename(columns={'A7':'adjust','ID': 'off_f'})
        tmp_sum = sum(tmp_ac_off_peak['off_f'])
        tmp_ac_off_peak['off_r'] = tmp_ac_off_peak['off_f'] / tmp_sum
        strong_com_beh = pd.merge(tmp_ac_morn_ad[['adjust','m_ad_r']],tmp_ac_morn_delay[['adjust','m_de_r']],on='adjust',how='outer')
        strong_com_beh = pd.merge(strong_com_beh , tmp_ac_even_ad[['adjust','e_ad_r']],on='adjust',how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_even_delay[['adjust', 'e_de_r']], on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_off_peak[['adjust', 'off_r']], on='adjust', how='outer')
        strong_com_beh.fillna(0,inplace=True)
        strong_com_beh.to_excel(strong_com_beh_file,index=False)
        tmp = df[(df['S11'] == 1) &
                 (~( (df['S18'] == 1)&
                 ((df['S19'] == 1)|
                  (df['S19']==2) ) ) ) &
                 (~(((df['S18'] == 2)|
                  (df['S18']==3) )&
                 (df['S19'] == 3)))]
        print("Commuter travelers with moderate regularity in travel:{0}".format(len(tmp)))
        # tmp_accept = tmp[(tmp['A1.当您今天有出行安排时，给予您一定的补偿，您是否愿意在一定范围内调整自己的出发时间？（单选）'] <= 3) |
        #                  (tmp['A9.当政府希望您在一定幅度内改变出发时间时，若奖励为现金，您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A10.当政府希望您在一定幅度内改变出发时间时，若奖励为代金券（包含乘车折扣券、共享单车兑换券、商品优惠券、试听会员等），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A11.当政府希望您在一定幅度内改变出发时间时，若奖励为抽奖盲盒（有一定几率获得更好的奖品），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A18.若取消杭州市限行政策，实行出行激励政策（如通过奖励一定的金额以调整出发时间），您对此的态度是？（单选）'] <= 3)]
        # print("出行规律性中等的通勤出行者愿意接受IBTDM的共{0}人".format(len(tmp_accept)))
        tmp_accept = tmp
        tmp_ac_morn_ad = tmp_accept.groupby(['A3'])['ID'].count().reset_index().rename(columns={'A3': 'adjust', 'ID': 'm_ad_f'})
        tmp_sum = sum(tmp_ac_morn_ad['m_ad_f'])
        tmp_ac_morn_ad['m_ad_r'] = tmp_ac_morn_ad['m_ad_f'] / tmp_sum
        tmp_ac_morn_delay = tmp_accept.groupby(['A4'])['ID'].count().reset_index().rename(columns={'A4': 'adjust', 'ID': 'm_de_f'})
        tmp_sum = sum(tmp_ac_morn_delay['m_de_f'])
        tmp_ac_morn_delay['m_de_r'] = tmp_ac_morn_delay['m_de_f'] / tmp_sum
        tmp_ac_even_ad = tmp_accept.groupby(['A5'])['ID'].count().reset_index().rename(columns={'A5': 'adjust', 'ID': 'e_ad_f'})
        tmp_sum = sum(tmp_ac_even_ad['e_ad_f'])
        tmp_ac_even_ad['e_ad_r'] = tmp_ac_even_ad['e_ad_f'] / tmp_sum
        tmp_ac_even_delay = tmp_accept.groupby(['A6'])['ID'].count().reset_index().rename(columns={'A6': 'adjust', 'ID': 'e_de_f'})
        tmp_sum = sum(tmp_ac_even_delay['e_de_f'])
        tmp_ac_even_delay['e_de_r'] = tmp_ac_even_delay['e_de_f'] / tmp_sum
        tmp_ac_off_peak = tmp_accept.groupby(['A7'])['ID'].count().reset_index().rename(columns={'A7': 'adjust', 'ID': 'off_f'})
        tmp_sum = sum(tmp_ac_off_peak['off_f'])
        tmp_ac_off_peak['off_r'] = tmp_ac_off_peak['off_f'] / tmp_sum
        strong_com_beh = pd.merge(tmp_ac_morn_ad[['adjust', 'm_ad_r']], tmp_ac_morn_delay[['adjust', 'm_de_r']],
                                  on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_even_ad[['adjust', 'e_ad_r']], on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_even_delay[['adjust', 'e_de_r']], on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_off_peak[['adjust', 'off_r']], on='adjust', how='outer')
        strong_com_beh.fillna(0, inplace=True)
        strong_com_beh.to_excel(median_com_beh_file, index=False)
        # 出行规律性弱的通勤出行者
        tmp = df[(df['S11'] == 1) &
                 ((df['S18'] == 2)|
                  (df['S18']==3) )&
                 (df['S19'] == 3)]
        print("Commuter travelers with weak travel patterns:{0}".format(len(tmp)))
        # tmp_accept = tmp[(tmp['A1.当您今天有出行安排时，给予您一定的补偿，您是否愿意在一定范围内调整自己的出发时间？（单选）'] <= 3) |
        #                  (tmp['A9.当政府希望您在一定幅度内改变出发时间时，若奖励为现金，您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A10.当政府希望您在一定幅度内改变出发时间时，若奖励为代金券（包含乘车折扣券、共享单车兑换券、商品优惠券、试听会员等），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A11.当政府希望您在一定幅度内改变出发时间时，若奖励为抽奖盲盒（有一定几率获得更好的奖品），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A18.若取消杭州市限行政策，实行出行激励政策（如通过奖励一定的金额以调整出发时间），您对此的态度是？（单选）'] <= 3)]
        # print("出行规律性弱的通勤出行者愿意接受IBTDM的共{0}人".format(len(tmp_accept)))
        tmp_accept = tmp
        tmp_ac_morn_ad = tmp_accept.groupby(['A3'])['ID'].count().reset_index().rename(columns={'A3': 'adjust', 'ID': 'm_ad_f'})
        tmp_sum = sum(tmp_ac_morn_ad['m_ad_f'])
        tmp_ac_morn_ad['m_ad_r'] = tmp_ac_morn_ad['m_ad_f'] / tmp_sum
        tmp_ac_morn_delay = tmp_accept.groupby(['A4'])['ID'].count().reset_index().rename(columns={'A4': 'adjust', 'ID': 'm_de_f'})
        tmp_sum = sum(tmp_ac_morn_delay['m_de_f'])
        tmp_ac_morn_delay['m_de_r'] = tmp_ac_morn_delay['m_de_f'] / tmp_sum
        tmp_ac_even_ad = tmp_accept.groupby(['A5'])['ID'].count().reset_index().rename(columns={'A5': 'adjust', 'ID': 'e_ad_f'})
        tmp_sum = sum(tmp_ac_even_ad['e_ad_f'])
        tmp_ac_even_ad['e_ad_r'] = tmp_ac_even_ad['e_ad_f'] / tmp_sum
        tmp_ac_even_delay = tmp_accept.groupby(['A6'])['ID'].count().reset_index().rename(columns={'A6': 'adjust', 'ID': 'e_de_f'})
        tmp_sum = sum(tmp_ac_even_delay['e_de_f'])
        tmp_ac_even_delay['e_de_r'] = tmp_ac_even_delay['e_de_f'] / tmp_sum
        tmp_ac_off_peak = tmp_accept.groupby(['A7'])['ID'].count().reset_index().rename(columns={'A7': 'adjust', 'ID': 'off_f'})
        tmp_sum = sum(tmp_ac_off_peak['off_f'])
        tmp_ac_off_peak['off_r'] = tmp_ac_off_peak['off_f'] / tmp_sum
        strong_com_beh = pd.merge(tmp_ac_morn_ad[['adjust', 'm_ad_r']], tmp_ac_morn_delay[['adjust', 'm_de_r']],
                                  on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_even_ad[['adjust', 'e_ad_r']], on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_even_delay[['adjust', 'e_de_r']], on='adjust', how='outer')
        strong_com_beh = pd.merge(strong_com_beh, tmp_ac_off_peak[['adjust', 'off_r']], on='adjust', how='outer')
        strong_com_beh.fillna(0, inplace=True)
        strong_com_beh.to_excel(weak_com_beh_file, index=False)
        # 家庭不常用车辆
        tmp = df[df['S11']==2]
        print("local vehicles:{0}".format(len(tmp)))
        # tmp_accept = tmp[(tmp['A1.当您今天有出行安排时，给予您一定的补偿，您是否愿意在一定范围内调整自己的出发时间？（单选）'] <= 3) |
        #                  (tmp['A9.当政府希望您在一定幅度内改变出发时间时，若奖励为现金，您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A10.当政府希望您在一定幅度内改变出发时间时，若奖励为代金券（包含乘车折扣券、共享单车兑换券、商品优惠券、试听会员等），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A11.当政府希望您在一定幅度内改变出发时间时，若奖励为抽奖盲盒（有一定几率获得更好的奖品），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A18.若取消杭州市限行政策，实行出行激励政策（如通过奖励一定的金额以调整出发时间），您对此的态度是？（单选）'] <= 3)]
        # print("家庭不常用车辆愿意接受IBTDM的共{0}人".format(len(tmp_accept)))
        tmp_accept = tmp
        tmp_adjust = tmp_accept.groupby(['A7'])['ID'].count().reset_index().rename(columns={'A7': 'adjust', 'ID': 'freq'})
        tmp_sum = sum(tmp_adjust['freq'])
        tmp_adjust['ratio'] = tmp_adjust['freq'] / tmp_sum
        tmp_adjust.to_excel(family_veh_beh_file,index=False)
        # 办事车辆
        tmp = df[df['S11']==3]
        print("non local vehicles:{0}".format(len(tmp)))
        # tmp_accept = tmp[(tmp['A1.当您今天有出行安排时，给予您一定的补偿，您是否愿意在一定范围内调整自己的出发时间？（单选）'] <= 3) |
        #                  (tmp['A9.当政府希望您在一定幅度内改变出发时间时，若奖励为现金，您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A10.当政府希望您在一定幅度内改变出发时间时，若奖励为代金券（包含乘车折扣券、共享单车兑换券、商品优惠券、试听会员等），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A11.当政府希望您在一定幅度内改变出发时间时，若奖励为抽奖盲盒（有一定几率获得更好的奖品），您的接受意愿是？（单选）'] <= 3) |
        #                  (tmp['A18.若取消杭州市限行政策，实行出行激励政策（如通过奖励一定的金额以调整出发时间），您对此的态度是？（单选）'] <= 3)]
        # print("办事车辆愿意接受IBTDM的共{0}人".format(len(tmp_accept)))
        tmp_accept = tmp
        tmp_adjust = tmp_accept.groupby(['A8'])['ID'].count().reset_index(
            ).rename(columns={'A8': 'adjust', 'ID': 'freq'})
        tmp_sum = sum(tmp_adjust['freq'])
        tmp_adjust['ratio'] = tmp_adjust['freq'] / tmp_sum
        tmp_adjust.to_excel(business_veh_beh_file,index=False)
        # 网约出租车辆
        tmp = df[df['S11'] > 3]
        print("taxis:{0}".format(len(tmp)))
    @staticmethod
    def get_dis_periods(data_file,adjust_file):
        df = pd.read_excel(data_file, sheet_name="数字版")
        print("survey data:{0}.".format(len(df)))
        # 错误数据滤除
        df = df[~ (((df['S13'] == 2) & (df['S11'] != 1)) |
                   ((df['S13'] == 2) & ((df['S17'] != 1) & (df['S17'] != 2))) |
                   (df['S4'] == 1) | (df['S9'] == 1) | (df['S10'] == 2))
        ]
        print("After filtering out the erroneous data, the remaining questionnaire data consists of{0}".format(len(df)))
        # 筛选出需要的数据
        df = df[df['S10'] == 1]
        print("The total number of questionnaires using private cars for travel:{0}".format(len(df)))
        tmp = df[(df['S11'] == 1)]  #提取出通勤车
        tmp = tmp[['ID','A3','A4','A5','A6','A7']]
        tmp.rename(columns={'A3':'早高峰提前','A4':'早高峰延后','A5':'晚高峰提前','A6':'晚高峰延后','A7':'平峰'},inplace=True)
        tmp.to_excel(adjust_file,index=False)

if __name__ == "__main__":
    # survey_data.data_preprocess(data_file="../../data/survey_data/【公司】杭州市出行激励政策接受度问卷调查-原始数据（200份）-0421.xlsx",
    #                             strong_com_beh_file="../../data/survey_data/company_survey_data/出行规律性强通勤者出发时间调整情况.xlsx",
    #                             median_com_beh_file="../../data/survey_data/company_survey_data/出行规律性中等通勤者出发时间调整情况.xlsx",
    #                             weak_com_beh_file="../../data/survey_data/company_survey_data/出行规律性弱通勤者出发时间调整情况.xlsx",
    #                             family_veh_beh_file="../../data/survey_data/company_survey_data/家庭不常用车辆出发时间调整情况.xlsx",
    #                             business_veh_beh_file="../../data/survey_data/company_survey_data/办事车辆出发时间调整情况.xlsx")

    survey_data.get_dis_periods(data_file="../../data/survey_data/【公司】杭州市出行激励政策接受度问卷调查-原始数据（500份）-0425.xlsx",
                                adjust_file="../../data/survey_data/company_survey_data/通勤车辆各时段出发时间调整情况.xlsx")









