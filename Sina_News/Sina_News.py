# -*- coding:utf-8 -*-

import json
import MySQLdb
import requests


class Sina_News(object):
    def __init__(self, newclass='gnxw'):
        self.url = 'http://api.roll.news.sina.com.cn/zt_list?'
        self.newclass = newclass

    def get_data(self, page=1):
        params = {'channel':'news',
                'cat_1': self.newclass, # 新闻类型，国内新闻（gnxw）、国际新闻（gjxw）和社会新闻（shxw）
                'cat_2': '',
                'level': '',
                'show_ext': '1',
                'show_all': '1',
                'show_num': '1000', #每次请求1000个数据
                'tag': '1',
                'format': 'json',  # 返回json数据
                'page': page  # 请求的页面
                }
        html = requests.get(self.url, params=params).content
        html_json = json.loads(html)["result"]
        return html_json

    def get_pages(self):
        total = int(self.get_data()["total"]) #获取该类新闻总条数
        #由每次请求1000条新闻，计算出总页数
        if total%1000 != 0:
            pages = (total//1000) + 1
        else:
            pages = total//1000
        return pages

    def get_new(self):
        pages = self.get_pages()

        for p in range(1,pages+1):
            
            data = self.get_data(page=p)["data"]
            self.execute_sql(data=data, page=p)

    def create_sql(self, item):
        '''创建SQL语句，item数据类型是字典'''
        k = "`, `".join(tuple(item.keys()))
        v = tuple(item.values())
        parms = k, v
        return "INSERT INTO Sina_News(`%s`) VALUES %s;" % parms

    def execute_sql(self, data, page):
        # 创建数据库连接
        db = MySQLdb.connect("localhost", "root", "root", "data", charset='utf8')
        cursor = db.cursor()
        num = 1
        for d in data:
            sql = self.create_sql(item=d)
            print('Crawl the page', page, ': Write data', num)
            try:
                cursor.execute(sql) # 执行sql语句
                db.commit()  # 提交到数据库执行
                num += 1
            except:
                db.rollback()

        db.close() # 关闭数据库连接


if __name__ == '__main__':
    print(u'''
    ========================
        0：国内新闻
        1：国际新闻
        2：社会新闻
    ========================''')

    news = ['gnxw','gjxw','shxw']
    newclass = news[int(input(u'请输入数字获取对应新闻：'))]
    Sina_News = Sina_News(newclass)
    Sina_News.get_new()
