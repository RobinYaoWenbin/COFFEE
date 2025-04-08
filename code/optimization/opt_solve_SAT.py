import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.pyplot import MultipleLocator
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

class solve:
    '''
    using ortools to solve the MIP probloms, the steps are following:
    To solve a MIP problem, your program should include the following steps :

    Import the linear solver wrapper,
    declare the MIP solver,
    define the variables,
    define the constraints,
    define the objective,
    call the MIP solver and
    display the solution
    '''
    def __init__(self,opt_trips_file,ts,max_di,is_sample,sample_num,research_hour,num_search_workers,logger):
        self.ts = ts
        self.df_trips = pd.read_csv(opt_trips_file,encoding='gbk')
        if is_sample:
            self.df_trips = self.df_trips.sample(n=sample_num, random_state=0)
        self.df_trips.reset_index(drop=True,inplace=True)
        self.df_trips['M'] = self.df_trips[['ori_sec','des_sec']].apply(utils.get_ts_num,args=(self.ts,),axis=1)
        self.df_trips['tss'] = self.df_trips['ori_sec'].apply(utils.get_timeslots,args=(self.ts,))
        self.df_trips['tso'] = self.df_trips['des_sec'].apply(utils.get_timeslots, args=(self.ts,))
        self.max_di = max_di
        self.research_hour = research_hour  # 需要从0点开始
        self.num_search_workers = num_search_workers
        self.logger = logger
        self.logger.info("构造函数完成")
        print("构造函数完成")
        self.start = time.time()

    def declare_solver(self):
        # Create the mip solver with the SCIP backend.
        solver = cp_model.CpModel()
        self.solver = solver
        self.logger.info("声明求解器完成")
        print("声明求解器完成")

    def defvar(self):
        # define xi
        trips = []  # a list that store trips, trips[i] means i-th trip. trips[i] is a binary decision matrix, see word for details.
        for i in range(len(self.df_trips)):
            tmp={}
            for j in range(self.df_trips.loc[i,'M']):
                for k in range(int(self.research_hour*60/self.ts)):
                    tmp[j, k] = self.solver.NewBoolVar('')
            trips.append(tmp)
        # define di
        delay = []
        for i in range(len(self.df_trips)):
            tmp = self.solver.NewIntVar(-self.max_di, self.max_di, 'd_{0}'.format(i))
            delay.append(tmp)
        # define vi
        v_list = []
        for i in range(len(self.df_trips)):
            tmp = {}
            for j in range(self.df_trips.loc[i,'M']):
                tmp[j] = self.solver.NewIntVar(0 , int(self.research_hour*60/self.ts) , '')
            v_list.append(tmp)
        # define P
        P_list = []
        for i in range(len(self.df_trips)):
            tmp = {}
            for j in range(int(self.research_hour*60/self.ts)):
                tmp[j] = self.solver.NewBoolVar('')
            P_list.append(tmp)
        # define peak
        peak = self.solver.NewIntVar(0, 999999, 'peak')
        self.trips = trips
        self.delay = delay
        self.v_list = v_list
        self.P_list = P_list
        self.peak = peak
        self.logger.info("定义变量完成")
        print("定义变量完成")

    def creacons(self):
        # 约束v大于等于0小于等于N
        for i in range(len(self.v_list)):
            tmp_v = self.v_list[i]
            self.solver.Add( tmp_v[0]>=0 )
            self.solver.Add(tmp_v[self.df_trips.loc[i,'M']-1] < int(self.research_hour*60/self.ts) )
        # constraints of v
        for i in range(len(self.v_list)):
            tmp_v = self.v_list[i]
            tmp_x = self.trips[i]
            for j in range(self.df_trips.loc[i,'M']):
                self.solver.Add(sum([(k*tmp_x[j,k]) for k in range(int(self.research_hour*60/self.ts))]) == tmp_v[j])
        # 对x增加一个约束，任何一行仅有一个1
        for i in range(len(self.v_list)):
            tmp_x = self.trips[i]
            for j in range(self.df_trips.loc[i,'M']):
                self.solver.AddExactlyOne(tmp_x[j,k] for k in range( int(self.research_hour*60/self.ts) ) )
        # constraints of v_j+1 = v_j + 1
        for i in range(len(self.v_list)):
            tmp_v = self.v_list[i]
            for j in range(self.df_trips.loc[i,'M']):
                if j < (self.df_trips.loc[i,'M'] - 1) :
                    self.solver.Add( (tmp_v[j] + 1 ) == tmp_v[j+1] )
        # constraints of v_j >= ts+di and v_j <= to+di
        # for i in range(len(self.v_list)):
        #     tmp_v = self.v_list[i]
        #     tmp_d = self.delay[i]
        #     tmp_tss = self.df_trips.loc[i,'tss']
        #     tmp_tso = self.df_trips.loc[i,'tso']
        #     for j in range(self.df_trips.loc[i, 'M']):
        #         self.solver.Add(tmp_v[j] >= tmp_tss + tmp_d)
        #         self.solver.Add(tmp_v[j] <= tmp_tso + tmp_d)
        # 上面注释的代码所显示的约束可以有更简化的等价约束
        for i in range(len(self.v_list)):
            tmp_v = self.v_list[i]
            tmp_d = self.delay[i]
            tmp_tss = self.df_trips.loc[i,'tss']
            tmp_tso = self.df_trips.loc[i,'tso']
            self.solver.Add(tmp_v[0] == tmp_tss + tmp_d)
            self.solver.Add( tmp_v[self.df_trips.loc[i, 'M']-1 ] == tmp_tso + tmp_d  )
        # constraints of P = Q * X
        for i in range(len(self.df_trips)):
            tmp_P = self.P_list[i]
            tmp_x = self.trips[i]
            # tmp_Q = [1 for i in range( self.df_trips.loc[i, 'M'] ) ]  # 由于Q向量全是1，所以其实无所谓
            for j in range(int(self.research_hour*60/self.ts)):
                self.solver.Add( sum( [  (1*tmp_x[k,j]) for k in range(self.df_trips.loc[i, 'M']) ] ) == tmp_P[j])
        # constraints of lt <= peak
        for i in range(int(self.research_hour * 60 / self.ts)):
            self.solver.Add( sum( [ self.P_list[j][i]  for j in range( len(self.df_trips) ) ] ) <= self.peak )
        print("创建约束完成")
        self.logger.info("创建约束完成")

    def crea_obj_func(self):
        self.solver.Minimize( self.peak )
        print("创建目标函数完成")
        self.logger.info("创建目标函数完成")

    def Invoke(self):
        print("开始求解")
        self.logger.info("开始求解")
        self.solver_model = cp_model.CpSolver()
        self.solver_model.parameters.max_time_in_seconds = 4000
        self.solver_model.parameters.log_search_progress = True
        self.solver_model.parameters.num_search_workers = self.num_search_workers
        self.status = self.solver_model.Solve(self.solver)
        print("求解完成")
        self.logger.info("求解完成")

    def give_solution(self,is_save,save_data_path):
        if self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE:
            print(f'Total cost = {self.solver_model.ObjectiveValue()}\n')
            self.logger.info(f'Total cost = {self.solver_model.ObjectiveValue()}\n')
            # 将优化求解得到的值进行保存
            # 整理di
            delay_solu = []
            for i in range(len(self.df_trips)):
                delay_solu.append( self.solver_model.Value(self.delay[i]) )
            v_list_solu = []
            for i in range(len(self.df_trips)):
                tmp = []
                for j in range(self.df_trips.loc[i, 'M']):
                    tmp.append(self.solver_model.Value(self.v_list[i][j]))
                v_list_solu.append(tmp)
            P_list_solu = []
            for i in range(len(self.df_trips)):
                tmp = []
                for j in range(int(self.research_hour*60/self.ts)):
                    tmp.append( int(self.solver_model.BooleanValue(self.P_list[i][j])) )
                P_list_solu.append(tmp)
            # x_list = []
            # for i in range(len(self.df_trips)):
            #     tmp_i = []
            #     for j in range(self.df_trips.loc[i,'M']):
            #         tmp_j = []
            #         for k in range(int(self.research_hour*60/self.ts)):
            #             tmp_j.append( int(self.solver_model.BooleanValue(self.trips[i][j,k]))  )
            #         tmp_i.append(tmp_j)
            #     x_list.append(tmp_i)
            self.df_trips['delay'] = delay_solu
            self.df_trips['v_list'] = v_list_solu
            self.df_trips['P_list'] = P_list_solu
            # self.df_trips['x_matrix'] = x_list
            if is_save:
                self.df_trips.to_csv(save_data_path,index=False,encoding='gbk')
            print("结果整理完成")
            self.logger.info("结果整理完成")
        else:
            print('No solution found.')
            self.logger.info("No solution found.")
            if self.status == cp_model.INFEASIBLE:
               print("The problem was proven infeasible.")
               self.logger.info("The problem was proven infeasible.")
            elif self.status == cp_model.MODEL_INVALID:
               print("The given CpModelProto didn't pass the validation step.")
               self.logger.info("The given CpModelProto didn't pass the validation step.")
            else:
                print(self.status)
                self.logger.info(self.status)
        end = time.time()
        print('程序执行时间: {0}min'.format(round((end - self.start)/60 , 2) ))
        self.logger.info('程序执行时间: {0}min'.format(round((end - self.start)/60 , 2) ))

if __name__ == "__main__":
    # 本地运行
    # logger = get_logger(file_path="E:\\study_e\\analysis_of_IBTDM\\code\\log\\")
    # obj =  solve(opt_trips_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_morning_419.csv",ts=15,max_di=1,
    #              is_sample=True, sample_num=1000 ,research_hour=12,num_search_workers=4,logger=logger)
    # obj.declare_solver()
    # obj.defvar()
    # obj.creacons()
    # obj.crea_obj_func()
    # obj.Invoke()
    # obj.give_solution(is_save=True,save_data_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\example_solution_optim_trips_morning_419.csv")

    # 天河服务器运行
    logger = get_logger(file_path="../log/")
    obj = solve(opt_trips_file="../../data/optim_data/optim_trips_morning_419.csv", ts=15, max_di=1,
                is_sample=False, sample_num=None, research_hour=12, num_search_workers=3, logger=logger)
    obj.declare_solver()
    obj.defvar()
    obj.creacons()
    obj.crea_obj_func()
    obj.Invoke()
    obj.give_solution(is_save=True, save_data_path="../../data/optim_data/best_solution_optim_trips_morning_419.csv")