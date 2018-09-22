import tushare as ts
import pandas as pd


if __name__ == '__main__':
    filePath = "../Data/macroEconomy/工业品出厂价格指数.csv"
    with open(filePath,encoding='utf-8') as f:
        df = pd.read_csv(f,encoding='utf-8')
        columns_dict = {
            "month" :"统计月份",
            "ppiip" :"工业品出厂价格指数",
            "ppi" :"生产资料价格指数",
            "qm":"采掘工业价格指数",
            "rmi":"原材料工业价格指数",
            "pi":"加工工业价格指数",
            "cg":"生活资料价格指数",
            "food":"食品类价格指数",
            "clothing":"衣着类价格指数",
            "roeu":"一般日用品价格指数",
            "dcg":"耐用消费品价格指数"
        }
        columns = columns_dict.values()
        df.rename(columns=columns_dict, inplace=True)
        df.to_csv(filePath, index=False, columns=columns, encoding="utf-8")

"""
if __name__ == '__main__':
    # df = ts.get_deposit_rate()        # 存款利率
    # df = ts.get_loan_rate()           # 贷款利率
    # df = ts.get_rrr()                 # 存款准备金
    # df = ts.get_money_supply()        # 货币供应量
    # df = ts.get_money_supply_bal()    # 货币供应量(年底余额)
    # df = ts.get_gdp_year()            # 国内生产总值(年度)
    # df = ts.get_gdp_quarter()         # 国内生产总值(季度)
    # df = ts.get_gdp_for()             # 三大需求对GDP贡献
    # df = ts.get_gdp_pull()            # 三大产业对GDP拉动
    # df = ts.get_gdp_contrib()         # 三大产业贡献率
    # df = ts.get_cpi()                 # 居民消费价格指数
    df = ts.get_ppi()                  # 工业品出厂价格指数
    columns = df.columns.values
    filePath = "../Data/macroEconomy/工业品出厂价格指数.csv"
    df.to_csv(filePath,index=False,columns=columns,encoding="utf-8")
"""