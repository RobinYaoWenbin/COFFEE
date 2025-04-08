import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../lib/")
from datetime import datetime, timezone, timedelta
import opt_solve_SAT
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

def get_logger(file_path):
    '''
    logging.basicConfig函数各参数：
    filename：指定日志文件名；
    filemode：和file函数意义相同，指定日志文件的打开模式，'w'或者'a'；
    format：指定输出的格式和内容，format可以输出很多有用的信息，
    level logging.INFO,
    '''
    #调用配置函数
    logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:%(message)s',
                        filename= f'{file_path}{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.txt',
                        level='INFO',
                        filemode='a'
    )
    return logging

class solu_solve:
    def __init__(self):
        pass
    @staticmethod
    def get_solu(logger , file_path,adj_thre_file,ts,is_sample,sample_num,research_hour, num_search_workers,is_save,save_data_path,save_data_prefix):
        file_name_list = os.listdir(file_path)
        for i in range(len(file_name_list)):
            print("目前正在处理第{0}个子样本文件:{1}".format( i , file_name_list[i] ))
            logger.info("目前正在处理第{0}个子样本文件:{1}".format( i , file_name_list[i] ))
            tmp_obj = opt_solve_SAT.solve(opt_trips_file=file_path+file_name_list[i],
                        adj_thre_file=adj_thre_file,
                        ts=ts, is_sample=is_sample, sample_num=sample_num, research_hour=research_hour, 
                        num_search_workers=num_search_workers, logger=logger)
            tmp_obj.declare_solver()
            tmp_obj.defvar()
            tmp_obj.creacons()
            tmp_obj.crea_obj_func()
            tmp_obj.Invoke()
            tmp_obj.give_solution(is_save=is_save,
                              save_data_path=save_data_path+save_data_prefix+file_name_list[i])

if __name__ == "__main__":
    #################################本地运行##############################
    # logger = get_logger(file_path="E:\\study_e\\analysis_of_IBTDM\\code\\log\\")
    # obj = solu_solve.get_solu(logger=logger, file_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_spilt_allday\\",
    #                           ts=15,max_di=1,is_sample=True,sample_num=30,research_hour=24, num_search_workers=4,
    #                           is_save=True,save_data_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\trip_solution_allday\\",
    #                           save_data_prefix="sub_")

    #################################天河超算##############################
    #################################早高峰##############################
    # logger = get_logger(file_path="../log/")
    # obj = solu_solve.get_solu(logger=logger,
    #                           file_path="../../data/optim_data/optim_trips_spilt_morning/",
    #                           ts=15, max_di=1, is_sample=False, sample_num=None, research_hour=24, num_search_workers=12,
    #                           is_save=True,
    #                           save_data_path="../../data/optim_data/trip_solution_morning/",
    #                           save_data_prefix="sub_")

    #################################晚高峰##############################
    # logger = get_logger(file_path="../log/")
    # obj = solu_solve.get_solu(logger=logger,
    #                           file_path="../../data/optim_data/optim_trips_spilt_evening/",
    #                           ts=15, max_di=1, is_sample=False, sample_num=None, research_hour=24,
    #                           num_search_workers=12,
    #                           is_save=True,
    #                           save_data_path="../../data/optim_data/trip_solution_evening/",
    #                           save_data_prefix="sub_")

    ##################################全天###################################
    # logger = get_logger(file_path="../log/")
    # obj = solu_solve.get_solu(logger=logger,
    #                           file_path="../../data/optim_data/optim_trips_spilt_allday/",
    #                           ts=15, max_di=1, is_sample=False, sample_num=None, research_hour=24,
    #                           num_search_workers=12,
    #                           is_save=True,
    #                           save_data_path="../../data/optim_data/trip_solution_allday/",
    #                           save_data_prefix="sub_")

    ##################################4月25日全天###################################
    logger = get_logger(file_path="../log/")
    obj = solu_solve.get_solu(logger=logger,
                              file_path="../../data/ibtdm_cons_travel/split2_optim_trips_spilt_allday_0425/",
                              adj_thre_file="../../data/survey_data/adj_thre_data.csv",
                              ts=15, is_sample=False, sample_num=None, research_hour=24,
                              num_search_workers=16,
                              is_save=True,
                              save_data_path="../../data/survey_data/trip_solution_allday_0425/",
                              save_data_prefix="sub_")
