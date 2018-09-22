from bs4 import BeautifulSoup
import requests


def getAllStock():
    """
    获取所有目前上市的所有股票的数据
    :return:
    """
    # 获取股票的url
    url = r"http://quote.eastmoney.com/stocklist.html"
    while 1:
        response = requests.get(url=url)
        if response.status_code == 200:
            # 更改字符编码
            response.encoding = 'gbk'
            # 解析网页,使用lxml解析器
            soup = BeautifulSoup(response.text,'html5lib')
            # 股票列表容器
            try:
                quotesearch = soup.find_all(id='quotesearch')[0]
                break
            except:
                print("html文档获取失败重新获取")
    # 获取所有股票的a标签列表
    stock_list = quotesearch.select("a[target='_blank']")
    # 用于存储数据
    stock_code_list = {'sh':[],'sz':[]}
    # 遍历a标签
    for stock_a in stock_list:
        try:
            # 获取a标签中的文本
            stock = stock_a.string
            # 股票名称
            # stock_name = stock[:-8]
            # 股票代码
            stock_code = stock[-7:-1]
            # 获取代码前3个数
            stock_code_3 = stock_code[:3]
            # 上海的股票
            if stock_code_3 in ['600','601','603']:
                stock_code_list['sh'].append(stock_code)
            # 深圳的股票
            if stock_code_3 in ['300','002','000']:
                stock_code_list['sz'].append(stock_code)
        except Exception as e:
            print("标签没有数据")
    print("股票列别获取成功")
    return stock_code_list

def getAllMarketIndex():
    # 获取A股中所有的大盘指数
    pass


if __name__ == '__main__':
    getAllStock()