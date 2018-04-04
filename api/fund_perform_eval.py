# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 16:29:54 2018

@author: helf
"""
import numpy as np
import pandas as pd

def cal_MaxDrawdown(values=None):
    '''
    计算最大回测序列
    :param values: 净值序列，pd.Series格式，index=日期，value=净值
    :return: 最大回测序列
    '''
    max_drawdown_series = pd.Series(index=values.index)
    max_drawdown_series.iloc[0] = 0
    for nn in range(1, len(values)):
        tmp_max = np.max(values.iloc[0:nn+1])
        max_drawdown_series.iloc[nn] = (values.iloc[nn] - tmp_max) / tmp_max

    max_drawdown = np.min(max_drawdown_series)
    return max_drawdown, max_drawdown_series


def PerformEval(net_value=None, benchmark_value=None, riskfree_rate=0.015, return_type='d'):
    if (len(net_value) == 0):
        print ('输入净值序列不能为空！')
        return False
    elif (len(net_value) != len(benchmark_value)):
        print ('净值序列和基准序列必须相同！')
        return False

    if riskfree_rate == None:
        riskfree_rate = 0.015

    if return_type == 'd':          # 输入为日收益率
        N_seq = 244
    elif return_type == 'w':        # 输入为周收益率
        N_seq = 52
    elif return_type == 'm':        # 输入为月收益率
        N_seq = 12
    else:
        print ('收益率序列类型有误！')
        return False

    if len(net_value) == 1:
        total_return = 0
        annual_return = 0
        daily_return = 0
        excess_return = 0
        annual_voltility = 0
        downside_voltility = 0
        max_drawdown = 0
        sharpe = 0
        sortino = 0
        alpha = 0
        beta = 0
        information_ratio = 0
        win = 0

        benchmark_total_return = 0
        benchmark_annual_return = 0
        benchmark_excess_return = 0
        benchmark_voltility = 0
        benchmark_downside_voltility = 0
        benchmark_max_drawdown = 0
        benchmark_sharpe = 0
        benchmark_sortino = 0
        benchmark_alpha = 0
        benchmark_beta = 0
        benchmark_information_ratio = 0
        benchmark_win = 0

    else:
        net_value = net_value.astype('float')
        benchmark_value = benchmark_value.astype('float')

        total_return = net_value[-1] / net_value[0] - 1
        annual_return = (1 + total_return) ** (float(N_seq) / float(len(net_value))) - 1

        daily_return = net_value.diff(1) / net_value.shift(1)
        daily_return = daily_return.dropna()
        annual_voltility = np.std(daily_return) * np.sqrt(N_seq)

        daily_return_downside = daily_return * [int(tmp < 0) for tmp in daily_return]
        daily_return_downside = daily_return_downside.dropna()
        downside_voltility = np.std(daily_return_downside) * np.sqrt(N_seq)

        max_drawdown, tmp = cal_MaxDrawdown(net_value)

        excess_return = annual_return - riskfree_rate
        if annual_voltility != 0:
            sharpe = excess_return / annual_voltility
        else:
            sharpe = 1e9

        if downside_voltility != 0:  # 考虑下行波动率为0的情况
            sortino = excess_return / downside_voltility
        else:
            sortino = 1e9

        benchmark_total_return = benchmark_value[-1] / benchmark_value[0] - 1
        benchmark_annual_return = (1 + benchmark_total_return) ** (float(N_seq) / float(len(benchmark_value))) - 1
        benchmark_excess_return = benchmark_annual_return - riskfree_rate

        benchmark_daily_return = benchmark_value.diff(1) / benchmark_value.shift(1)
        benchmark_daily_return = benchmark_daily_return.dropna()
        benchmark_voltility = np.std(benchmark_daily_return) * np.sqrt(N_seq)
        benchmark_max_drawdown, tmp = cal_MaxDrawdown(benchmark_value)

        benchmark_daily_return_downside = benchmark_daily_return * [int(tmp < 0) for tmp in benchmark_daily_return]
        benchmark_daily_return_downside = benchmark_daily_return_downside.dropna()
        benchmark_downside_voltility = np.std(benchmark_daily_return_downside) * np.sqrt(N_seq)

        if benchmark_voltility != 0:
            benchmark_sharpe = benchmark_excess_return / benchmark_voltility
        else:
            benchmark_sharpe = 1e9

        if benchmark_downside_voltility != 0:  # 考虑下行波动率为0的情况
            benchmark_sortino = benchmark_excess_return / benchmark_downside_voltility
        else:
            benchmark_sortino = 1e9

        if len(daily_return) > 1:
            beta = np.cov(daily_return - riskfree_rate/N_seq, benchmark_daily_return - riskfree_rate/N_seq)[0, 1] / np.var(benchmark_daily_return)
            alpha = excess_return - beta * benchmark_excess_return
            # information_ratio = np.sqrt(N_seq) * (np.mean(daily_return) - np.mean(benchmark_daily_return)) / np.std(daily_return - benchmark_daily_return)
            epsilon = (daily_return - riskfree_rate/N_seq) - alpha/N_seq - beta*(benchmark_daily_return - riskfree_rate/N_seq)
            information_ratio = (alpha/np.sqrt(N_seq))/(np.std(epsilon)+1e-9)   # +1e-9 避免除0的情况

        else:
            beta = 1
            alpha = 0
            information_ratio = 0

        benchmark_alpha = 0
        benchmark_beta = 1
        benchmark_information_ratio = 0

        win = float(sum([int(tmp >= 0) for tmp in daily_return]))/float(len(daily_return))      # python2.7 里整数除以整数最后还是整数，需要先转化成float
        benchmark_win = float(sum([int(tmp >= 0) for tmp in benchmark_daily_return]))/float(len(benchmark_daily_return))

    perform_result = {'total_return': total_return,
                    'annual_return': annual_return,
                    'excess_return': excess_return,
                    'annual_voltility': annual_voltility,
                    'downside_voltility': downside_voltility,
                    'max_drawdown': max_drawdown,
                    'sharpe': sharpe,
                    'sortino': sortino,
                    'alpha': alpha,
                    'beta': beta,
                    'information_ratio': information_ratio,
                    'win': win,
                    'benchmark_total_return': benchmark_total_return,
                    'benchmark_annual_return': benchmark_annual_return,
                    'benchmark_excess_return': benchmark_excess_return,
                    'benchmark_voltility': benchmark_voltility,
                    'benchmark_downside_voltility': benchmark_downside_voltility,
                    'benchmark_max_drawdown': benchmark_max_drawdown,
                    'benchmark_sharpe': benchmark_sharpe,
                    'benchmark_sortino': benchmark_sortino,
                    'benchmark_alpha': benchmark_alpha,
                    'benchmark_beta': benchmark_beta,
                    'benchmark_information_ratio': benchmark_information_ratio,
                    'benchmark_win': benchmark_win,
                      }

    return perform_result
