# 加入环境变量
import os,sys
currentPath = os.path.dirname(os.path.abspath(__file__))
rootPath = os.path.split(currentPath)[0]
sys.path.append(rootPath)

import requests, multiprocessing, re, datetime
import pandas as pd
import tushare as ts
# 新闻数据保存路径
newsPath = os.path.join(rootPath, "Data", "news")
# 判断是否存在这个文件夹，不存在则创建
if not os.path.exists(newsPath):
    os.makedirs(newsPath)
# 设置pandas输出样式
pd.set_option("expand_frame_repr", False)

# 获取新闻数据
def get_stock_news(session, symbol_id, newsPath):
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

# 处理从tushare抓取的上市股票代码
def getAllStock():
    token = "3fccf079ae131a7870aa4131483f2ef77b83548a6e0d26c95148cc34"
    pro = ts.pro_api(token=token)
    try:
        data = pro.stock_basic(list_status="L")["ts_code"]
    except Exception as e:
        return None
    stock = {"sh": [], "sz": []}
    sz_stock_list = data[data.str[-2:] == "SZ"]
    sh_stock_list = data[data.str[-2:] == "SH"]
    stock["sz"] = sz_stock_list.str[:6].tolist()
    stock["sh"] = sh_stock_list.str[:6].tolist()
    return stock


if __name__ == '__main__':
    stock_dict = None
    for i in range(10):
        stock_dict = getAllStock()
        if stock_dict:
            print("获取股票列表成功!!")
            break
    else:
        print("获取股票列表失败！！检查tushareToken或者网络")
        exit()
    session = requests.session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36"
    }
    session.get("https://xueqiu.com/")
    pool = multiprocessing.Pool()
    for market, stock_list in stock_dict.items():
        for stock in stock_list:
            symbol_id = "{market}{stock}".format(market=market.upper(), stock=stock)
            # get_stock_news(session,symbol_id,newsPath)
            pool.apply_async(func=get_stock_news, args=(session, symbol_id, newsPath))
    pool.close()
    pool.join()
    print("结束")
