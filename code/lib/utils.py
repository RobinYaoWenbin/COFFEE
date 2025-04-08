import pandas as pd
import numpy as np

def t2s(t):
    h,m,s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def t2s_fulltime(t):
    return int(t[11:13])*3600 + int(t[14:16])*60 + int(t[17:19])

def get_ts_num(ser,ts):
    return (int(ser['des_sec']/60/ts) - int(ser['ori_sec']/60/ts) + 1)

def get_timeslots(x,ts):
    return int(x/60/ts)

def get_ts_netload(df,ts):
    df.reset_index(drop=True,inplace=True)
    travel_ts = []
    for i in range(len(df)):
        tmp = list(range(df.loc[i, 'tss'], df.loc[i, 'tso'] + 1))
        travel_ts.extend(tmp)
    ts_num = int(24 * 60 / ts)
    netload = []
    for i in range(ts_num):
        netload.append(travel_ts.count(i))
    return netload

def newell_model(n,vf,beta,nj):
    return vf*(1-np.exp( -beta/vf*(1/n-1/nj) ))

def exp_func(n,a,b,c):
    return ( a * np.exp(-b*(n/10000)) + c  )

def get_period(ser):
    if ser['label'] == -1:
        return 0
    else:
        if (ser['ori_sec']>=26100) and (ser['ori_sec']<=38700):
            return 1
        elif (ser['ori_sec']>=56700) and (ser['ori_sec']<=69300):
            return 2
        else:
            return 0