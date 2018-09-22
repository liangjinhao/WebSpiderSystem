import pandas as pd

pd.set_option("expand_frame_repr", False)

if __name__ == '__main__':
    file = open("../Data/news_detail/SH600000.csv","r",encoding="utf-8")
    df = pd.read_csv(file, encoding="utf-8")
    print(df)
    df.dropna(inplace=True)
    print(df)