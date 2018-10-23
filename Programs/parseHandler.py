import requests,datetime
from pyquery import PyQuery as pq

class ParseHandlerType(type):
    """ 解释器类的元类 """
    def __init__(self,class_name, parent_classes, attrs):
        pass

    def __call__(self, *args, **kwargs):
        obj = self.__new__(self,*args,**kwargs)
        self.__init__(obj,*args,**kwargs)
        return obj

class ParseHandler(object,metaclass=ParseHandlerType):
    """ 解析器类 """
    def __init__(self):
        self._func_dict = {
            "http://finance.sina.com.cn":"_parse_finance_sina",
            "http://finance.eastmoney.com":"_parse_eastmoney",
            "http://stock.stockstar.com":"_parse_stockstar",
            "http://stock.10jqka.com.cn":"_parse_stock_10jqka",
            "http://yuanchuang.10jqka.com.cn":"_parse_yuanchuang_10jqka",
            "http://bond.10jqka.com.cn":"_parse_bond_10jqka",
            "http://ggjd.cnstock.com":"_parse_cnstock",
            "http://finance.ce.cn":"_parse_ce",
            "http://stock.jrj.com.cn":"_parse_jrj",
            "http://www.p5w.net":"_parse_p5w",
            "http://www.sohu.com":"_parse_sohu",
            "http://stock.sohu.com":"_parse_stock_sohu",
            "http://game.people.com.cn":"_parse_people",
            "http://www.thepaper.cn":"_parse_thepaper",
            "http://sc.stock.cnfol.com":"_parse_cnfol",
            "http://news.hongzhoukan.com":"_parse_hongzhoukan",
            "http://www.yicai.com":"_parse_yicai",
            "http://news.mysteel.com":"_parse_mysteel",
            "http://news.sina.com.cn":"_parse_news_sina",
            "http://company.stcn.com":"_parse_company_stcn",
            "http://www.chinanews.com":"_parse_chinanews",
            "http://www.ifanr.com":"_parse_ifanr",
            "http://companies.caixin.com":"_parse_companies_caixin",
            "http://tech.sina.com.cn":"_parse_tech_sina",
            "http://stock.hexun.com":"_parse_stock_hexun",
            "http://cj.sina.com.cn":"_parse_cj_sina",
            "http://finance.qq.com":"_parse_finance_qq",
            "http://auto.people.com.cn":"_parse_auto_people"
        }

    def parse(self,url):
        """ 解析 统一的解析入口 """
        byte_html = self._request(url)
        protocol = "http://"
        url = url.replace(protocol,"")
        domain = protocol + url.split("/")[0]
        return self._dispatch(domain,byte_html)

    @staticmethod
    def _request(url):
        """ 请求数据 """
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
        }
        response =requests.get(url=url,headers=headers)
        return response.content

    def _dispatch(self,domain,byte_html):
        """ 分发 分发到具体的解析函数 """
        if domain in self._func_dict:
            func = getattr(self,self._func_dict[domain])
            try:
                result = func(byte_html)
                return result
            except Exception as e:
                print("获取网页数据出现异常:",e)
                return None
        else:
            print("{}\t解释器没有这个域名的解析方法".format(domain))
            return None

    @staticmethod
    def _parse_finance_sina(byte_html):
        """ 新浪财经 """
        html = byte_html.decode("utf-8")
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.w1240 > h1").text()
        # 日期
        date = doc("#top_bar > div > div.date-source > span.date").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 正文内容
        content = ""
        p_list = doc("#artibody")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_eastmoney(byte_html):
        """ 东方财富网 """
        html = byte_html.decode("utf-8")
        doc = pq(html)
        # 标题
        title = doc(".mainFrame .main_left .newsContent > h1").text()
        # 日期
        date = doc(".Info .time-source .time").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#ContentBody")("p")[1:]
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_stockstar(byte_html):
        """ 证券之星 """
        html = byte_html.decode("gbk")
        doc = pq(html)
        # 标题
        title = doc("#container-box > h1").text()
        # 日期
        date = doc("#pubtime_baidu").text()
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("#container-article")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_stock_10jqka(byte_html):
        """ 同花顺 """
        html = str(byte_html, "gbk", errors='replace')
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.clearfix > div.main-fl.fl > h2").text()
        # 日期
        date = doc("#pubtime_baidu").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div.main-content.clearfix > div.main-fl.fl > div.main-text.atc-content")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_cnstock(byte_html):
        """ 中国证券网 """
        html = byte_html.decode("gbk")
        doc = pq(html)
        # 标题
        title = doc("#pager-content > h1").text()
        # 日期
        date = doc("#pager-content > div:nth-child(2) > span.timer").text()
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("#qmt_content_div")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_ce(byte_html):
        """ 中国经济网 """
        html = byte_html.decode("gbk")
        doc = pq(html)
        # 标题
        title = doc("#articleTitle").text()
        # 日期
        date = doc("#articleTime").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#articleText")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_jrj(byte_html):
        """ 金融界 """
        html = str(byte_html, "gbk", errors='replace')
        doc = pq(html)
        # 标题
        title = doc("body > div.header > div.main.jrj-clear > div.left > div.titmain > h1").text()
        # 日期
        date = doc("body > div.header > div.main.jrj-clear > div.left > div.titmain > p > span:nth-child(3)").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div.header > div.main.jrj-clear > div.left > div.titmain > div.texttit_m1")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_p5w(byte_html):
        """ 全景网 """
        html = byte_html.decode("gbk")
        doc = pq(html)
        # 标题
        title = doc(".newscontent_right2 >h1").text()
        # 日期
        date = doc(".content_info.clearfix .left > time").text()
        date = str(datetime.datetime.now().year) + "年" +date
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc(".Custom_UnionStyle")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_sohu(byte_html):
        """ 搜狐 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("#article-container > div.left.main > div.text > div.text-title > h1").text()
        # 日期
        date = doc("#news-time").text()
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M")
        # 内容
        content = ""
        p_list = doc("#mp-editor")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_people(byte_html):
        """ 人民网 """
        html = byte_html.decode("gbk")
        doc = pq(html)
        # 标题
        title = doc("body > div.clearfix.w1000_320.text_title > h1").text()
        # 日期
        date = doc("body > div.clearfix.w1000_320.text_title > div > div.fl").text()[:16]
        date = datetime.datetime.strptime(date,"%Y年%m月%d日%H:%M")
        # 内容
        content = ""
        p_list = doc("#rwb_zw")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_thepaper(byte_html):
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.bdwd.main.clearfix > div.main_lt > div.newscontent > h1").text()
        # 日期
        date = doc("body > div.bdwd.main.clearfix > div.main_lt > div.newscontent > div.news_about > p:nth-child(2)").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        # 内容
        content = ""
        string_list = doc("body > div.bdwd.main.clearfix > div.main_lt > div.newscontent > div.news_txt").text()
        for string in string_list:
            content += string.strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_yuanchuang_10jqka(byte_html):
        html = str(byte_html, "gbk", errors='replace')
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.clearfix > div.main-fl.fl > h2").text()
        # 日期
        date = doc("#pubtime_baidu").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div.main-content.clearfix > div.main-fl.fl > div.main-text.atc-content")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_cnfol(byte_html):
        """ 图说财经 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.allCnt > div.artMain.mBlock > h3.artTitle").text()
        # 日期
        date = doc("body > div.allCnt > div.artMain.mBlock > div.artDes > span:nth-child(2)").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        string_list = doc("body > div.allCnt > div.artMain.mBlock > div.Article").text()
        for string in string_list:
            content += string.strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_hongzhoukan(byte_html):
        """ 红周刊 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.newswrap > div.listnew_con > div.listnew_left > div.lists > div.article > h1").text()
        # 日期
        date = doc("body > div.newswrap > div.listnew_con > div.listnew_left > div.lists > div.article > h2 > span:nth-child(1)").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("body > div.newswrap > div.listnew_con > div.listnew_left > div.lists > div.article")("p")
        for p in p_list:
            content += p.text.strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_yicai(byte_html):
        """ 第一财经 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.g-bd.f-cb > div.g-mn.g-mn-w.g-mn-mt1.f-fl > div.m-text > div.title.f-pr > h1").text()
        # 日期
        date = doc("body > div.g-bd.f-cb > div.g-mn.g-mn-w.g-mn-mt1.f-fl > div.m-text > div.title.f-pr > p > em").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div.g-bd.f-cb > div.g-mn.g-mn-w.g-mn-mt1.f-fl > div.m-text > div.m-txt")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_mysteel(byte_html):
        """ 我的钢铁 """
        html = byte_html.decode("GBK")
        doc = pq(html)
        # 标题
        title = doc("body > div.wrap.clearfix > div.main > div.articleBox > h1").text()
        # 日期
        date = doc("body > div.wrap.clearfix > div.main > div.articleBox > div.article-infor > span:nth-child(1)").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        # 内容
        content = ""
        p_list = doc("#text")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_news_sina(byte_html):
        """ 新浪新闻 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.w1240 > h1").text()
        # 日期
        date = doc("#top_bar > div > div.date-source > span").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#article > div:nth-child(3)")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_company_stcn(byte_html):
        """ 证券时报 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.content.clearfix > div.kx_left > div.intal_tit > h2").text()
        # 日期
        date = doc("body > div.content.clearfix > div.kx_left > div.intal_tit > div").text()[:16]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        # 内容
        content = ""
        p_list = doc("#ctrlfscont")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_chinanews(byte_html):
        """ 中国新闻网 """
        html = byte_html.decode("GBK")
        doc = pq(html)
        # 标题
        title = doc("#cont_1_1_2 > h1").text()
        # 日期
        date = doc("#cont_1_1_2 > div.left-time > div.left-t").text()[:17]
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#cont_1_1_2 > div.left_zw")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_ifanr(byte_html):
        """ ifanr """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("#content-meta-header > div > h1").text()
        # 日期
        date = doc("#ArticleContentMeta > div.c-meta-share__left > div > p").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        # 内容
        content = ""
        p_list = doc("#article-content-wrapper > div > article")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_companies_caixin(byte_html):
        """ ifanr """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("#conTit > h1").text()
        # 日期
        date = doc("#artInfo").text()[:17]
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#Main_Content_Val")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_tech_sina(byte_html):
        """ 新浪科技 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("#main_title").text()
        # 日期
        date = doc("#page-tools > span > span.titer").text()[:17]
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#artibody")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_stock_hexun(byte_html):
        """ 和讯股票 """
        html = byte_html.decode("GBK")
        doc = pq(html)
        # 标题
        title = doc("body > div.layout.mg.articleName > h1").text()
        # 日期
        date = doc("body > div.layout.mg.articleName > div > div.tip.fl > span").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div:nth-child(16) > div.w600 > div.art_context > div.art_contextBox")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_stock_sohu(byte_html):
        """ 搜狐股票 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.layout.mg.articleName > h1").text()
        # 日期
        date = doc("body > div.layout.mg.articleName > div > div.tip.fl > span").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div:nth-child(16) > div.w600 > div.art_context > div.art_contextBox")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_cj_sina(byte_html):
        """ 新浪头条 """
        html = byte_html.decode()
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.w1240 > h1").text()
        # 日期
        date = doc("#top_bar > div > div.date-source > span").text()
        date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
        # 内容
        content = ""
        p_list = doc("#artibody")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_finance_qq(byte_html):
        """ 腾讯财经 """
        html = byte_html.decode("GBK")
        doc = pq(html)
        # 标题
        title = doc("#Main-Article-QQ > div > div.qq_main > div.qq_article > div.hd > h1").text()
        # 日期
        date = doc("#Main-Article-QQ > div > div.qq_main > div.qq_article > div.hd > div > div.a_Info > span.a_time").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        # 内容
        content = ""
        p_list = doc("#Cnt-Main-Article-QQ")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_auto_people(byte_html):
        """ 人民网 """
        html = byte_html.decode("GBK")
        doc = pq(html)
        # 标题
        title = doc("body > div.clearfix.w1000_320.text_title > h1").text()
        # 日期
        date = doc("body > div.clearfix.w1000_320.text_title > div > div.fl").text()[:16]
        date = datetime.datetime.strptime(date, "%Y年%m月%d日%H:%M")
        # 内容
        content = ""
        p_list = doc("body > div.clearfix.w1000_320.text_con > div.fl.text_con_left > div.box_con")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result

    @staticmethod
    def _parse_bond_10jqka(byte_html):
        """ 同花顺财经 """
        html = str(byte_html,"gbk",errors="replace")
        doc = pq(html)
        # 标题
        title = doc("body > div.main-content.clearfix > div.main-fl.fl > h2").text()
        # 日期
        date = doc("#pubtime_baidu").text()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 内容
        content = ""
        p_list = doc("body > div.main-content.clearfix > div.main-fl.fl > div.main-text.atc-content")("p")
        for p in p_list:
            content += p.text_content().strip()
        result = {
            "title": title, "date": date, "content": content
        }
        return result










