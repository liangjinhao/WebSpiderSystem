import pandas as pd
from Programs import parseHandler

pd.set_option("expand_frame_repr", False)

if __name__ == '__main__':
    parser = parseHandler.ParseHandler()
    df = pd.read_csv("../Data/news/SH600004.csv", encoding="utf-8")
    urls = df["url"].tolist()
    url = urls[22]
    print(url)
    result = parser.parse(url)
    print(result)