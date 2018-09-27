import tushare as ts

def get_name(code,pro):
    df = pro.namechange(ts_code=code, fields='name')
    num = df.shape[0]
    for i in range(1,num):
        name = df.loc[i]["name"]
        if "ST" not in name:
            return name

if __name__ == '__main__':
    df = ts.get_st_classified()
    df["code"] = df["code"].apply(lambda x: x +".SH" if x[0] == "6" else x + ".SZ")
    # stock_name_list = df["name"].tolist()
    # with open("ST_stock.txt",'w',encoding="utf-8") as f:
    #     for name in stock_name_list:
    #         f.write(name + "\n")
    pro = ts.pro_api("35df2181b8de73f89857c4f48329a72a17e47f92ee520a534b0954a2")
    # df = pro.namechange(ts_code='002018.SZ', fields='name')
    # print(df.iloc[1]["name"])
    df["原名"] = df["code"].apply(lambda code:get_name(code,pro))
    print(df)
    df.to_csv("st_stock.csv",encoding="utf-8",index=False)