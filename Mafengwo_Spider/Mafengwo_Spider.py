# -*- coding: utf-8 -*-

import MySQLdb
import requests
import json
from lxml import etree



class MafengwoSpider:
    def __init__(self,con):
        self.con = con
        # 初始化页面，从第一页开始爬取
        self.page = 1
        self.url = 'http://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        # 定义表头
        self.headers = {
                        'Host': 'www.mafengwo.cn',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': 'http://www.mafengwo.cn/mdd/citylist/21536.html',
                        'Content-Length': '20',
                        'Connection': 'keep-alive'
                        }
    
    def GetPage(self):
        # 分析发现数据是通过post请求方式获取的，
        # 提交参数包含mddid(目测是该板块的id，该参数不变)、page(页码，改变值可以请求到不同页面)；
        # 响应的数据json格式，使用json包来解析 
        data = {"mddid" : "21536", "page" : self.page}
        html = requests.post(url=self.url, data=data, headers=self.headers)
        html = json.loads(html.text)

        lists = etree.HTML(html['list'])
        L = lists.xpath('//li')

        # 定义data列表，用于保存该页面提取的数据
        data = {}
        for l in L:
            data['home_url'] = self.process_data(l.xpath('div[@class="img"]/a/@href'))
            data['home_img'] = self.process_data(l.xpath('div[@class="img"]//img/@data-original'))
            data['cnname'] = self.process_data(l.xpath('div[@class="img"]/a/div/text()[1]'))
            data['enname'] = self.process_data(l.xpath('div[@class="img"]//p[@class="enname"]/text()'))
            data['visit_nums'] = self.process_data(l.xpath('dl[@class="caption"]//div[@class="nums"]/b/text()'))
            data['detail'] = self.process_data(l.xpath('dl[@class="caption"]//div[@class="detail"]/text()'))

            #print(data)
            self.write_sql(data)  #把数据写入数据库

        # 判断当前所在页码，并判断是否还有下一页，如果有则继续爬取，否则停止爬取
        pages = etree.HTML(html['page'])
        print("Start crawling the page:", pages.xpath('//span[@class="pg-current"]//text()')[0])

        if len(pages.xpath('//a[@class="pg-next _j_pageitem"]//text()')) == 0:
            # 所有页面爬取完
            print("Crawl finished......")
        else:
            # 爬取下一页
            self.page += 1
            return self.GetPage()

    def process_data(self, data):
        # 处理数据，因为有一些数据的字段缺失的，为了避免后面程序的错误，这里需要做处理
        if len(data)==0:
            return ""
        else:
            return data[0].strip()


    # 把dict数据转换为sql语句，并将记录插入到数据库中
    def write_sql(self,data):
        k = '`, `'.join(tuple(data.keys()))
        v = tuple(data.values())
        parms = k, v

        sql = 'INSERT INTO Mafengwo_db (`%s`) VALUES %s;' % parms

        try:
            self.con.execute(sql)
            #print(sql)
        except:
            pass

if __name__ == '__main__':
    # 创建数据库连接
    db = MySQLdb.connect("localhost", "root", "root", "data", charset='utf8')   
    con = db.cursor()

    Mafengwo = MafengwoSpider(con)
    Mafengwo.GetPage()
    
    # 程序结束，关闭连接
    db.close()
