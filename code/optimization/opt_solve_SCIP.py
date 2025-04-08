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
import utils
plt.rc('font',family='Times New Roman')
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

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
    def __init__(self,opt_trips_file,ts,max_di,is_sample,sample_num,research_hour):
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
        print("构造函数完成")

    def declare_solver(self,num_search_workers):
        # Create the mip solver with the SCIP backend.
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            print("initialise the solver failed.")
            return
        self.solver = solver
        self.solver.SetNumThreads(num_search_workers)
        print("声明求解器完成")

    def defvar(self):
        # define xi
        trips = []  # a list that store trips, trips[i] means i-th trip. trips[i] is a binary decision matrix, see word for details.
        for i in range(len(self.df_trips)):
            tmp={}
            for j in range(self.df_trips.loc[i,'M']):
                for k in range(int(self.research_hour*60/self.ts)):
                    tmp[j, k] = self.solver.IntVar(0, 1, '')
            trips.append(tmp)
        # define di
        delay = []
        for i in range(len(self.df_trips)):
            tmp = self.solver.IntVar(-self.max_di, self.max_di, 'd_{0}'.format(i))
            delay.append(tmp)
        # define vi
        v_list = []
        for i in range(len(self.df_trips)):
            tmp = {}
            for j in range(self.df_trips.loc[i,'M']):
                tmp[j] = self.solver.IntVar(0 , int(self.research_hour*60/self.ts) , '')
            v_list.append(tmp)
        # define P
        P_list = []
        for i in range(len(self.df_trips)):
            tmp = {}
            for j in range(int(self.research_hour*60/self.ts)):
                tmp[j] = self.solver.IntVar(0, 1, '')
            P_list.append(tmp)
        # define peak
        peak = self.solver.IntVar(0, 999999, 'peak')
        self.trips = trips
        self.delay = delay
        self.v_list = v_list
        self.P_list = P_list
        self.peak = peak
        print("定义变量完成")

    def creacons(self):
        # constraints of v
        for i in range(len(self.v_list)):
            tmp_v = self.v_list[i]
            tmp_x = self.trips[i]
            for j in range(self.df_trips.loc[i,'M']):
                self.solver.Add(self.solver.Sum([(k*tmp_x[j,k]) for k in range(int(self.research_hour*60/self.ts))]) == tmp_v[j])
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
                self.solver.Add( self.solver.Sum( [  (1*tmp_x[k,j]) for k in range(self.df_trips.loc[i, 'M']) ] ) == tmp_P[j] )
        # constraints of lt <= peak
        for i in range(int(self.research_hour * 60 / self.ts)):
            self.solver.Add( self.solver.Sum( [ self.P_list[j][i]  for j in range( len(self.df_trips) ) ] ) <= self.peak )
        print("创建约束完成")

    def crea_obj_func(self):
        self.solver.Minimize( self.peak )
        print("创建目标函数完成")

    def Invoke(self):
        print("开始求解")
        self.status = self.solver.Solve()
        print("求解完成")

    def give_solution(self,is_save,save_data_path):
        if self.status == pywraplp.Solver.OPTIMAL or self.status == pywraplp.Solver.FEASIBLE:
            print(f'Total cost = {self.solver.Objective().Value()}\n')
            # 将优化求解得到的值进行保存
            # 整理di
            delay_solu = []
            for i in range(len(self.df_trips)):
                delay_solu.append(self.delay[i].solution_value())
            v_list_solu = []
            for i in range(len(self.df_trips)):
                tmp = []
                for j in range(self.df_trips.loc[i, 'M']):
                    tmp.append(self.v_list[i][j].solution_value())
                v_list_solu.append(tmp)
            P_list_solu = []
            for i in range(len(self.df_trips)):
                tmp = []
                for j in range(int(self.research_hour*60/self.ts)):
                    tmp.append(self.P_list[i][j].solution_value())
                P_list_solu.append(tmp)
            self.df_trips['delay'] = delay_solu
            self.df_trips['v_list'] = v_list_solu
            self.df_trips['P_list'] = P_list_solu
            if is_save:
                self.df_trips.to_csv(save_data_path,index=False,encoding='gbk')
            print("结果整理完成")
        else:
            print('No solution found.')
            if self.status == pywraplp.Solver.INFEASIBLE:
               print("The problem was proven infeasible.")
            elif self.status == pywraplp.Solver.MODEL_INVALID:
               print("	The given CpModelProto didn't pass the validation step.")
            else:
                print(self.status)

if __name__ == "__main__":
    obj =  solve(opt_trips_file="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\optim_trips_morning_419.csv",ts=15,max_di=2,
                 is_sample=True, sample_num=15,research_hour=12)
    obj.declare_solver(num_search_workers = 4)
    obj.defvar()
    obj.creacons()
    obj.crea_obj_func()
    obj.Invoke()
    obj.give_solution(is_save=True,save_data_path="E:\\study_e\\analysis_of_IBTDM\\data\\optim_data\\solution_optim_trips_morning_419.csv")
