"""
这是一个使用历史模拟法自动计算资产组合在险价值（VaR，Value at Risk）的软件
获取证券数据使用的API接口来自于TuShare，需要注册TuShare社区账户并获取个人TOKEN才能调用该接口
在本案例中，选用的（证券）资产组合分别是'奥特佳.SZ'、'华安证券.SH'以及'四维图新.SZ'，数量对应的分别为400股，900股和100股
选取数据的起始时间为2019年1月1日，截止时间为最近结束的一个交易日
（需注意：TuShare社区数据更新为每天下午5点左右，选取当天为最后一个交易日时需留意空指针）

关于在险价值VaR（Value at Risk）
在险价值VaR（以下简称VaR）是用于衡量资产风险的一种方法，其表示的是：
在给定的置信水平(Alpha)下，在下一个交易日该资产组合损失有1-Alpha的概率不会超过VaR
e.g. 资产组合A在置信水平为5%时的VaR为200：资产组合A在下一个交易日有95%(1-5%)的概率损失不会超过200元

"""
import numpy as np
import pandas as pd
import datetime
import tushare as ts
import matplotlib.pyplot as plt

# 定义所需固定变量，Alpha为置信水平(0 < Alpha < 1)
date = datetime.datetime
today = date.strftime(date.today(), "%Y%m%d")
TOKEN = '你的TuShare账户TOKEN'
Alpha = 0.05
# 定义资产组合中每种资产的数量
storage_List = [400, 900, 100]


# 绘制波动幅度
def plot_floating_value(X,Y):
    plt.plot(X, Y)
    plt.xlabel('Trading Day No.X')
    plt.ylabel('Floating Value')


# 设置tushare账户TOKEN
ts.set_token(TOKEN)
pro = ts.pro_api()

# 获取相应证券的历史数据信息
df_atj = pro.daily(ts_code='002239.SZ', start_date='20190101', end_date=today)
df_hazq = pro.daily(ts_code='600909.SH', start_date='20190101', end_date=today)
df_swtx = pro.daily(ts_code='002405.SZ', start_date='20190101', end_date=today)

# 按照交易日期升序排序
df_atj = df_atj.sort_values(by='trade_date')
df_hazq = df_hazq.sort_values(by='trade_date')
df_atj = df_atj.sort_values(by='trade_date')

# 初始化资产组合的DataFrame
df_comb = pd.DataFrame()

# 计算第一天的市值及其波动情况
atj = df_atj.iloc[0].open * storage_List[0]
hazq = df_hazq.iloc[0].open * storage_List[1]
swtx = df_swtx.iloc[0].open * storage_List[2]
total_worth = atj + hazq + swtx
curr_col = {'Trade Date': '20190101',
            df_atj.ts_code[0]: atj,
            df_hazq.ts_code[0]: hazq,
            df_swtx.ts_code[0]: swtx,
            'Total Value': total_worth,
            'Floating Rate': 0.0,
            'Floating Value': 0.0}
df_comb = df_comb.append(curr_col, ignore_index=True)

# 计算第2天开始到当前的总市值及波动情况
for i in range(1, df_atj.shape[0]):
    atj = df_atj.iloc[i].open * storage_List[0]
    hazq = df_hazq.iloc[i].open * storage_List[1]
    swtx = df_swtx.iloc[i].open * storage_List[2]
    trade_date = df_atj.iloc[i].trade_date
    floating_rate = (atj+hazq+swtx-total_worth)/total_worth
    floating_value = atj+hazq+swtx-total_worth
    total_worth = atj + hazq + swtx

    curr_col = {'Trade Date': trade_date,
                df_atj.ts_code[0]: atj,
                df_hazq.ts_code[0]: hazq,
                df_swtx.ts_code[0]: swtx,
                'Total Value': total_worth,
                'Floating Rate': floating_rate,
                'Floating Value': floating_value}
    df_comb = df_comb.append(curr_col, ignore_index=True)

# 绘制资产组合价格波动值图表
print(df_comb)
plot_floating_value(np.arange(0, df_comb.shape[0], 1), df_comb['Floating Value'])

# 按照市值波动率进行升序排序
df_comb = df_comb.sort_values('Floating Rate')
confidence_rate = df_comb['Floating Rate'][int(df_comb.shape[0]*Alpha)]

# 计算VaR
VaR = (-1) * confidence_rate * df_comb.loc[df_comb.shape[0]-1]['Total Value']
print("VaR = ", VaR)

# 将波动率保留两位小数
df_comb['Floating Rate'] = round(df_comb['Floating Rate'], 4)

# 绘制波动率分布直方图
df_comb.hist('Floating Rate', bins=100)

plt.show()

