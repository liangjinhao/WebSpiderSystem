from settings import *
import requests, multiprocessing, re, datetime
import pandas as pd
import tushare as ts
from Programs import parseHandler

# 设置pandas输出样式
pd.set_option("expand_frame_repr",False)

def get_stock_news(session,symbol_id,newsPath):
    # 获取新闻数据
    print(symbol_id+"开始抓取数据!!")
    filePath = os.path.join(newsPath, symbol_id + ".csv")
    date_time = None
    try:
        if os.path.exists(filePath):
            # 判断该文件是否存在
            file = open(filePath, "r", encoding="utf-8")
            df = pd.read_csv(file, encoding="utf-8")
            if df.empty:
                # 为空
                df = pd.DataFrame({"datetime": [], "title": [], "content": [], "url": []})
            else:
                # 不为空
                date_time = df.loc[0]["datetime"]
                date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        else:
            # 文件不存在
            df = pd.DataFrame({"datetime": [], "title": [], "content": [], "url": []})
        page = 1        # 页码
        total = 0       # 新闻个数
        flag = False    # 标志位
        # 数据url
        temp_url = "https://xueqiu.com/statuses/stock_timeline.json?symbol_id={symbol_id}&count=20&source=自选股新闻&page={page}"
        while True:
            try:
                data_url = temp_url.format(symbol_id=symbol_id, page=page)
                # session.proxies = {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}
                response = session.get(data_url, timeout=30)
                data_list = response.json().get("list")
                if not data_list:
                    # 若列表为空，表示获取到头了
                    print("{symbol_id} 共有 {total} 条数据".format(symbol_id=symbol_id, total=total))
                    break
                temp_df = pd.DataFrame({"title": [], "content": [], "url": [], "datetime": []})
                for i, item in enumerate(data_list):
                    try:
                        total += 1  # 总数自增
                        data = dict()
                        # 获取标题
                        data['title'] = item.get("title")
                        # 获取文本内容和url
                        [(data['content'], data['url'])] = re.findall(r'(.*?)<a href="(.*?)"', item.get("description"))
                        if item.get("timeBefore").startswith("今天"):
                            # 若时间是以今天开头
                            data["datetime"] = item.get("timeBefore").replace("今天", datetime.datetime.now().strftime("%Y-%m-%d"))
                        else:
                            # 不是
                            data['datetime'] = str(datetime.datetime.now().year)+"-" + item.get("timeBefore") if \
                                not re.findall(r"\d*-\d*-\d* \d*:\d*",item.get("timeBefore"))else item.get("timeBefore").replace("/","-")
                        temp_datetime = datetime.datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
                        # 判断是否存在停止时间，获取更新数据到了上一次的停止时间
                        if date_time and temp_datetime <= date_time:
                            total -= 1
                            flag = True
                            if total > 0:
                                print("{}的新闻数据更新{}条!!!!".format(symbol_id, total))
                            else:
                                print("{}没有获取到新的新闻数据!!!!".format(symbol_id))
                            break
                        temp_df.loc[i] = data
                    except Exception as e:
                        total -= 1
                        continue
                # 合并
                df = pd.concat([df, temp_df], ignore_index=True,sort=True)
                page += 1
                if flag:
                    # 结束
                    break
            except Exception as e:
                print("{}出现异常:{e}".format(symbol_id,e=e))
        try:
            df.drop_duplicates(subset=["datetime", "url"], inplace=True)        # 去重
            df.sort_values(by="datetime", inplace=True, ascending=False)        # 按照时间顺序排列，由近到远
            df.to_csv(filePath, index=False, columns=["datetime", "title", "content", "url"])
            print("{symbol_id} 完成!!!!!!".format(symbol_id=symbol_id))
        except Exception as e:
            print("保存文件出错 {e}".format(e=e))
            print(df)
    except Exception as e:
        print("{}出现错误:{e}".format(symbol_id,e=e))

def deal_news(parser,file_path,file_save_path):
    # 解析新闻数据
    try:
        # 股票代码
        stock = os.path.basename(file_path)[:8]
        stock = stock[2:8] + "." + stock[:2]
        print("{}开始!!!".format(stock))
        # 读取文件
        file = open(file_path, "r", encoding="utf-8")
        df = pd.read_csv(file, encoding="utf-8")
        date_time = None
        if df.empty:
            print("{}这个文件是空的!!!".format(stock))
            return
        else:
            pass
        news_detail_df = pd.DataFrame(data={"title": [], "date": [], "content": []})
        i = 0
        for url in df["url"]:
            try:
                result = parser.parse(url)
                news_detail_df.loc[i] = result
                i += 1
            except Exception as e:
                pass
                print("url:{}解析出错,url出现重定向获取定时刷新".format(url))
        news_detail_df.dropna(inplace=True)                                             # 去空值
        news_detail_df["date"] = news_detail_df["date"].apply(lambda x: x.date().strftime("%Y%m%d")) # 修改时间格式
        news_detail_df.reset_index(drop=True, inplace=True)                             # 重定义索引
        start_date = news_detail_df.at[news_detail_df.shape[0]-1, "date"]               # 获取开始时间
        end_date = news_detail_df.at[0, "date"]                                         # 获取结束时间
        # stock_df = pro.daily(ts_code=stock, start_date=start_date, end_date=end_date, fields=["trade_date", "pct_change"])
        stock_df = get_stock_detail(stock,start_date,end_date)
        if stock_df is None:
            return
        merge_df = pd.merge(left=news_detail_df, right=stock_df, right_on="trade_date", left_on="date")
        merge_df.drop("trade_date", inplace=True, axis=1)
        merge_df.drop_duplicates(subset=["date", "title"], inplace=True)  # 去重
        merge_df.sort_values(by="date", inplace=True, ascending=False)  # 按照时间顺序排列，由近到远
        merge_df["date"] = merge_df["date"].apply(lambda x: "{}-{}-{}".format(x[:4], x[4:6], x[6:8]))
        if not merge_df.empty:
            merge_df.to_csv(file_save_path, index=False, columns=["date", "title", "content", "pct_change"])
            print("{}完成!!!共{}行数据".format(stock, str(merge_df.shape[0])))
        else:
            print("{}为空!!!")
    except Exception as e:
        print("出现错误:{}".format(e))

def get_stock_detail(stock,start_date,end_date):
    """ 获取股票详细信息 """
    pro = ts.pro_api(token=tushare_token)
    for i in range(10):
        try:
            data = pro.daily(ts_code=stock, start_date=start_date, end_date=end_date, fields=["trade_date", "pct_change"])
            return data
        except Exception as e:
            print("出现异常",e)
    return None

def getAllStock():
    """ 从tushare抓取的上市股票代码 """
    pro = ts.pro_api(token=tushare_token)
    for i in range(10):
        try:
            data = pro.stock_basic(list_status="L")["ts_code"]
            stock = {"sh": [], "sz": []}
            sz_stock_list = data[data.str[-2:] == "SZ"]
            sh_stock_list = data[data.str[-2:] == "SH"]
            stock["sz"] = sz_stock_list.str[:6].tolist()
            stock["sh"] = sh_stock_list.str[:6].tolist()
            return stock
        except Exception as e:
            print("异常:",e)
    print("获取股票列表失败！！检查settings.py里的tushareToken或者网络")
    exit()

if __name__ == '__main__':
    # 获取股票列表
    # stock_dict = getAllStock()
    #
    # #### 采用多进程的方式去抓取股票新闻数据
    # session = requests.session()
    # session.headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36"
    # }
    # session.get("https://xueqiu.com/")
    pool = multiprocessing.Pool()
    # for market, stock_list in stock_dict.items():
    #     for stock in stock_list[:2]:
    #         symbol_id = "{market}{stock}".format(market=market.upper(), stock=stock)
    #         # get_stock_news(session,symbol_id,newsPath)
    #         pool.apply_async(func=get_stock_news, args=(session, symbol_id, news_folder_path))
    # pool.close()
    # pool.join()
    # print("抓取股票新闻数据结束!!!!")

    ###### 下面是解析抓取回来的股票新闻信息然后在解析成详细信息
    parser = parseHandler.ParseHandler()    # 创建一个解析类对象
    files = []  # 保存股票新闻文件列表
    for _,_,files_list in os.walk(news_folder_path):files += files_list # 获取股票列表
    for file in files:
        file_path = os.path.join(news_folder_path, file)
        file_save_path = os.path.join(news_detail_folder_path,file)
        # deal_news(parser, file_path, file_save_path)
        pool.apply_async(func=deal_news, args=(parser, file_path, file_save_path))
    pool.close()
    pool.join()
    print("解析股票新闻数据结束!!!!")






