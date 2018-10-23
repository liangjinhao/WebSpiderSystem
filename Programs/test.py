from Programs import parseHandler

if __name__ == '__main__':
    parse = parseHandler.ParseHandler()
    url = "http://bond.10jqka.com.cn/20150421/c571935693.shtml"
    print(parse.parse(url))