import os,sys
# 获取根目录并且加入环境变量
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)

# 新闻数据保存路径
news_folder_path = os.path.join(root_path, "Data", "news")
# 新闻详细数据保存路径
news_detail_folder_path = os.path.join(root_path, "Data", "news_detail")
# 判断是否存在这个文件夹，不存在则创建
if not os.path.exists(news_detail_folder_path):
    os.makedirs(news_detail_folder_path)
if not os.path.exists(news_folder_path):
    os.makedirs(news_folder_path)

# tushare token
tushare_token = "35df2181b8de73f89857c4f48329a72a17e47f92ee520a534b0954a2"


