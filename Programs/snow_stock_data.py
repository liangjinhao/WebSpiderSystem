import os,sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import pandas as pd
pd.set_option('expand_frame_repr',False)
from Program import StockName
import requests, time,pickle
from pandas.errors import EmptyDataError
columns_rename_dict = {
    'symbol': '股票代码', 'name': '股票名称', 'time': '交易日期', 'issue_date': '上市日期','open': '开盘价', 'high': '最高价', 'low': '最低价',
    'current' : '收盘价','last_close':'昨收', 'percent': '涨跌幅', 'amplitude': '振幅', 'volume_ratio': '量比',
    'volume': '成交量', 'amount': '成交额', 'turnover_rate': '换手率','limit_up': '涨停价', 'limit_down': '跌停价',
    'pe_ttm': '市盈率TTM', 'pb': '市净率','float_market_capital' : '流通市值', 'market_capital': '总市值'
}
# 用来保存抓取错误的股票代码
error_stock = []
# 创建一个sessiom
session = requests.session()
# 设置请求头，模拟浏览器
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
# 获取雪球网的session
session.get('https://xueqiu.com/')
# 雪球数据
stock_url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol={stock_symbol}&extend=detail'
stock_dict = StockName.getAllStock()
# 遍历更新
for market,stock_list in stock_dict.items():
    for stock_code in stock_list:
        try:
            # 个股数据链接
            url = stock_url.format(stock_symbol=market.upper()+stock_code)
            session.headers['Host'] = "stock.xueqiu.com"
            response = session.get(url=url,timeout=30)
            # 按照json格式解析
            stock = response.json()
            # 获取数据成功且股票没有退市
            if stock['error_code'] == 0 and stock['data']['quote']:
                # 股票是否停牌
                quote = stock['data']['quote']
                if quote['open']:
                    # 当前日期
                    time_local = time.localtime(quote['time']/1000)
                    current_date = time.strftime("%Y-%m-%d",time_local)
                    quote['time'] = quote['timestamp'] = current_date
                    # 上市日期
                    time_local = time.localtime(quote['issue_date']/1000)
                    issue_date = time.strftime("%Y-%m-%d",time_local)
                    quote['issue_date'] = issue_date
                    quote_format = {}
                    # 遍历quote将数据转化成DataFrame的格式
                    for k,v in quote.items():
                        if k in columns_rename_dict.keys():
                            quote_format[k] = [v]
                    df = pd.DataFrame(quote_format)
                    df.rename(index=str,columns=columns_rename_dict,inplace=True)
                    # 股票保存路径
                    path = "{root}/Data/{market}/{market_lower}{stock_code}.csv"
                    stock_path = path.format(market=market.upper(),stock_code=stock_code,root=rootPath,market_lower =market)
                    print(stock_path)
                    exit()
                    # 判断文件是否存在
                    if os.path.exists(stock_path):
                        try:
                            old_df = pd.read_csv(stock_path,encoding='gbk')
                        except EmptyDataError as e:
                            old_df = pd.DataFrame()
                        df = pd.concat([df,old_df],ignore_index=True,sort=True)
                        df = df[list(columns_rename_dict.values())]
                    df.drop_duplicates(subset=['交易日期'],keep='last',inplace=True)
                    df.to_csv(stock_path,index=False,encoding="gbk")
                    print("股票%s :完成"%stock_code)
                else:
                    print("股票%s :停牌"%stock_code)
            else:
                print("股票%s :退市"%stock_code)
        except Exception as e:
            print(e)
            print("%s:错误"%stock_code)
            error_stock.append(stock_code)
print("所有股票数据获取成功!!!!!!!")
if len(error_stock) != 0:
    print("共有%d个抓取错误的股票"%len(error_stock))
    pickle.dump(error_stock, 'error_stock.plk')