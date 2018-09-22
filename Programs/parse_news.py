import sys, os
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

import pandas as pd
import tushare as ts
import multiprocessing
from Programs import parseHandler
pd.set_option("expand_frame_repr", False)
# tushare Token设置
token = "3fccf079ae131a7870aa4131483f2ef77b83548a6e0d26c95148cc34"
pro = ts.pro_api(token=token)


def deal_news(parser,file_path,file_save_path):
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
        stock_df = pro.daily(ts_code=stock, start_date=start_date, end_date=end_date, fields=["trade_date", "pct_change"])
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


if __name__ == '__main__':
    parser = parseHandler.ParseHandler()
    news_folder = os.path.join(root_path, "Data", "news")
    if not os.path.exists(news_folder):
        print("新闻内容文件夹不存在，请先执行snow_news.py文件")
        exit()
    save_path = os.path.join(root_path, "Data", "news_detail")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    files = None
    # 获取文件列表
    for _, _, files in os.walk(news_folder):
        pass
    pool = multiprocessing.Pool()
    # 遍历执行
    for file in files[:1]:
        file_path = os.path.join(news_folder, file)
        file_save_path = os.path.join(save_path,file)
        deal_news(parser, file_path, file_save_path)
        # pool.apply_async(func=deal_news, args=(parser, file_path, file_save_path))
    # pool.close()
    # pool.join()
    print("结束")