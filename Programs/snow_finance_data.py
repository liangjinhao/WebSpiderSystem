import requests
from multiprocessing import Pool
import os
import datetime
import pandas as pd
from Programs import StockName


def get_stock_finance(stock_symbol,session,rootPath):
    num = 1
    count = 0
    df = pd.DataFrame()
    while True:
        try:
            url = f"https://xueqiu.com/stock/f10/finmainindex.json?symbol={stock_symbol}&page={num}&size=100"
            response = session.get(url,timeout=10)
            if response.status_code == 200:
                finance_data_list = response.json().get("list")
                if finance_data_list:
                    for data in finance_data_list:
                        if df.empty:
                            columns = data.keys()
                            columns_dict = {k:[] for k in columns}
                            df = pd.DataFrame(columns_dict)
                        df.loc[count] = data
                        count += 1
                    num += 1
                else:
                    break
            else:
                print("访问页面出错")
        except Exception as e:
            print(f"出现异常:{e}")
    try:
        if not df.empty:
            # 删除一些没用的字段,更新一些信息
            df.drop(labels=['name',"totalshare","compcode"],axis=1,inplace=True)
            df['symbol'] = stock_symbol
            file = os.path.join(rootPath,f"{stock_symbol}.csv")
            df['reportdate'] = df['reportdate'].apply(lambda date:datetime.datetime.strptime(str(date),"%Y%m%d"))
            columns_list = [
                "symbol","reportdate","basiceps","epsdiluted","epsweighted","naps","opercashpershare",
                "peropecashpershare","netassgrowrate","dilutedroe","weightedroe","mainbusincgrowrate","netincgrowrate",
                "totassgrowrate","salegrossprofitrto","mainbusiincome","mainbusiprofit","totprofit","netprofit",
                "totalassets","totalliab","totsharequi","operrevenue","invnetcashflow","finnetcflow",
                "chgexchgchgs","cashnetr","cashequfinbal"
            ]
            df.to_csv(file,index=False,encoding="gbk",columns=columns_list)
            print(f"{stock_symbol}完成!!!!!")
        else:
            print(f"{stock_symbol}为空!!!!!")
    except Exception as e:
        print(f"保存文件异常:{e}")


if __name__ == '__main__':
    rootPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Data","finance")
    t_list = []
    session = requests.session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    session.get('https://xueqiu.com/')
    print("开始爬取")
    stock_dict = StockName.getAllStock()
    pool = Pool()
    for market,code_list in stock_dict.items():
        for code in code_list:
            stock_symbol = f"{market.upper()}{code}"
            pool.apply_async(get_stock_finance,args=(stock_symbol,session,rootPath))
    pool.close()
    pool.join()
    print("全部完成")